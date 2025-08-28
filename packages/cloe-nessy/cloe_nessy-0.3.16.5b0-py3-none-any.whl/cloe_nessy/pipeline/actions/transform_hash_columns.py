from typing import Any

from pydantic import BaseModel, Field, model_validator
from pyspark.sql import functions as F

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext

SUPPORTED_ALGORITHMS = {"hash", "md5", "sha1", "sha2", "xxhash64", "crc32"}
VALID_SHA2_BITS = {224, 256, 384, 512}


class HashSettings(BaseModel):
    """Represents the settings for hashing columns.

    Attributes:
        columns: List of column names to hash.
        algorithm: Hashing algorithm to use. Must be one of
            "hash", "md5", "sha1", "sha2", "xxhash64", or "crc32".
        bits: Bit length for the 'sha2' algorithm. Optional.
    """

    columns: list[str]
    algorithm: str = Field(..., description="Hashing algorithm to use")
    bits: int | None = Field(default=None, description="Only required for sha2")

    @model_validator(mode="before")
    def validate_all(cls, values):
        """Validates the input values for a hashing operation before model instantiation.

        This method performs the following checks:

        1. Ensures the specified hashing algorithm is supported.
        2. Validates that at least one column is provided and that the columns parameter is a non-empty list.
        3. Checks that hashing multiple columns is only supported for the 'hash' and 'xxhash64' algorithms.
        4. For the 'sha2' algorithm, ensures that the 'bits' parameter is one of the valid options.
        5. Ensures that the 'bits' parameter is not provided for algorithms other than 'sha2'.

        Raises:
            ValueError: If the algorithm is unsupported, no columns are provided, the columns parameter is invalid,
                        or the 'bits' parameter is invalid for the specified algorithm.
            NotImplementedError: If multiple columns are provided and the algorithm does not support hashing multiple columns.

        Args:
            cls: The class being validated.
            values: A dictionary of input values containing 'algorithm', 'columns', and 'bits'.

        Returns:
            The validated input values.
        """
        algorithm = values.get("algorithm")
        columns = values.get("columns")
        bits = values.get("bits")

        if algorithm not in SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"Unsupported hashing algorithm '{algorithm}'. Supported algorithms are: {SUPPORTED_ALGORITHMS}."
            )

        if not columns or not isinstance(columns, list) or len(columns) == 0:
            raise ValueError("At least one column must be provided.")

        if len(columns) > 1 and algorithm not in {"hash", "xxhash64"}:
            raise NotImplementedError(
                f"Hashing multiple columns is only supported for 'hash' and 'xxhash64'. Algorithm '{algorithm}' does not support this."
            )

        if algorithm == "sha2":
            if bits not in VALID_SHA2_BITS:
                raise ValueError(f"'bits' must be one of {VALID_SHA2_BITS} when using 'sha2'.")
        elif bits is not None:
            raise ValueError("'bits' is only allowed when algorithm is 'sha2'.")

        return values


class HashConfig(BaseModel):
    """A configuration model for defining hash settings for specific columns.

    Attributes:
        hash_config: A dictionary where the keys are column names
            (as strings) and the values are `HashSettings` objects that define
            the hash settings for each column.

    Methods:
        validate_config: Validates the hash configuration to ensure it contains
            at least one entry and that all column names are valid strings. Raises a
            `ValueError` if the configuration is invalid.
    """

    hash_config: dict[str, HashSettings]

    @model_validator(mode="before")
    def validate_config(cls, values):
        """Validates the hash configuration provided in the model.

        This method is executed in "before" mode to ensure that the `hash_config`
        field in the input values meets the required criteria:

        - It must be a dictionary.
        - It must contain at least one entry.
        - Each key in the dictionary must be a non-empty string.

        Raises:
            ValueError: If `hash_config` is missing, not a dictionary, empty, or
                        contains invalid column names.

        Args:
            cls: The class to which this validator is applied.
            values: The input values to validate.

        Returns:
            The validated input values.
        """
        config = values.get("hash_config")
        if not config or not isinstance(config, dict) or len(config) == 0:
            raise ValueError("Hash configuration must contain at least one entry.")
        for new_col in config:
            if not new_col or not isinstance(new_col, str):
                raise ValueError(f"Invalid column name '{new_col}' in hash configuration.")
        return values


class TransformHashColumnsAction(PipelineAction):
    """Hashes specified columns in a DataFrame using a chosen algorithm.

    Given the following `hash_config`:

    Example:
        ```yaml
        Hash Columns:
            action: TRANSFORM_HASH_COLUMNS
            options:
                hash_config:
                - hashed_column1:
                    columns: ["column1", "column2"]
                    algorithm: "sha2"
                    bits: 224
                - hashed_column2:
                    columns: ["column1"]
                    algorithm: "crc32"
        ```

    Given a DataFrame `df` with the following structure:

    | column1 | column2 | column3 |
    |---------|---------|---------|
    |   foo   |   bar   |   baz   |

    After running the action, the resulting DataFrame will look like:

    | column1 | column2 | column3 |                 hashed_column1                            | hashed_column2 |
    |---------|---------|---------|-----------------------------------------------------------|----------------|
    |   foo   |   bar   |   baz   |  17725b837e9c896e7123b142eb980131dcc0baa6160db45d4adfdb21 |  1670361220    |


    !!! note "Hash values might vary"
        The actual hash values will depend on the hashing algorithm used and the input data.
    """

    name: str = "TRANSFORM_HASH_COLUMNS"

    def run(
        self,
        context: PipelineContext,
        *,
        hash_config: HashConfig | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Hashes the specified columns in the DataFrame.

        Args:
            context: Context in which this Action is executed.
            hash_config: Dictionary that contains the configuration for executing the hashing.

        Returns:
            Updated PipelineContext with hashed columns.

        Raises:
            ValueError: If columns are missing, data is None, or algorithm/bits are invalid.
            ValueError: If the hash configuration is invalid.
        """
        if context.data is None:
            raise ValueError("Context data is required for hashing.")

        if not hash_config:
            raise ValueError("Hash configuration is required.")

        df = context.data

        hash_functions = {
            "hash": lambda cols: F.hash(*[F.col(c) for c in cols]).cast("string"),
            "xxhash64": lambda cols: F.xxhash64(F.concat_ws("||", *[F.col(c) for c in cols])).cast("string"),
            "md5": lambda cols: F.md5(F.concat_ws("||", *[F.col(c) for c in cols])).cast("string"),
            "sha1": lambda cols: F.sha1(F.concat_ws("||", *[F.col(c) for c in cols])).cast("string"),
            "sha2": lambda cols, bits: F.sha2(F.concat_ws("||", *[F.col(c) for c in cols]), bits).cast("string"),
            "crc32": lambda cols: F.crc32(F.concat_ws("||", *[F.col(c) for c in cols])).cast("string"),
        }
        default_sha2_bits = 256

        config_obj = HashConfig.model_validate({"hash_config": hash_config})
        for new_col, config in config_obj.hash_config.items():
            hash_func = hash_functions[config.algorithm]
            if config.algorithm == "sha2":
                df = df.withColumn(new_col, hash_func(config.columns, config.bits or default_sha2_bits))  # type: ignore
            else:
                df = df.withColumn(new_col, hash_func(config.columns))  # type: ignore

        return context.from_existing(data=df)
