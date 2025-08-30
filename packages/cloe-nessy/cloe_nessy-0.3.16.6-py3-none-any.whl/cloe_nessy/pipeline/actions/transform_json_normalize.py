from typing import Any, cast

import pyspark.sql.functions as F

from cloe_nessy.pipeline.pipeline_action import PipelineAction
from cloe_nessy.pipeline.pipeline_context import PipelineContext


class TransformJsonNormalize(PipelineAction):
    """Normalizes and flattens the DataFrame by exploding array columns and flattening struct columns.

    The method performs recursive normalization on the DataFrame present in the context,
    ensuring that the order of columns is retained and new columns created by flattening
    structs are appended after existing columns.

    Example:
        ```yaml
        Normalize Tables:
            action: TRANSFORM_JSON_NORMALIZE
            options:
                exclude_columns: coordinates
        ```
        Example Input Data:

        | id | name   | coordinates          | attributes                |
        |----|--------|----------------------|---------------------------|
        | 1  | Alice  | [10.0, 20.0]         | {"age": 30, "city": "NY"} |
        | 2  | Bob    | [30.0, 40.0]         | {"age": 25, "city": "LA"} |

        Example Output Data:

        | id | name   | coordinates | attributes_age | attributes_city |
        |----|--------|-------------|----------------|-----------------|
        | 1  | Alice  | [10.0, 20.0]| 30             | NY              |
        | 2  | Bob    | [30.0, 40.0]| 25             | LA              |
    """

    name: str = "TRANSFORM_JSON_NORMALIZE"

    def run(
        self,
        context: PipelineContext,
        *,
        exclude_columns: list[str] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Executes the normalization process on the DataFrame present in the context.

        Please note that columns retain their relative order during the
        normalization process, and new columns created by flattening structs are
        appended after the existing columns.

        Args:
            context: The pipeline context that contains the DataFrame to be normalized.
            exclude_columns: A list of column names to exclude from the normalization process.
                    These columns will not be exploded or flattened.
            **_: Additional keyword arguments (not used).

        Returns:
            A new pipeline context with the normalized DataFrame.

        Raises:
            ValueError: If the DataFrame in the context is `None`.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        if not exclude_columns:
            exclude_columns = []
        df = TransformJsonNormalize._normalize(context.data, exclude_columns=cast(list, exclude_columns))
        return context.from_existing(data=df)

    @staticmethod
    def _normalize(df, exclude_columns):
        """Recursively normalizes the given DataFrame by exploding arrays and flattening structs.

        This method performs two primary operations:
        1. Explodes any array columns, unless they are in the list of excluded columns.
        2. Flattens any struct columns, renaming nested fields and appending them to the top-level DataFrame.

        The method continues these operations in a loop until there are no array or struct columns left.

        Args:
            df: The input DataFrame to normalize.
            exclude_columns: A list of column names to exclude from the normalization process. These columns
                                         will not be exploded or flattened.

        Returns:
            pyspark.sql.DataFrame: The normalized DataFrame with no array or struct columns.
        """

        def explode_arrays(df, exclude_columns):
            array_present = False
            for col in df.columns:
                if df.schema[col].dataType.typeName() == "array" and col not in exclude_columns:
                    df = df.withColumn(col, F.explode(col))
                    array_present = True
            return df, array_present

        def flatten_structs(df):
            struct_present = False
            struct_columns = [col for col in df.columns if df.schema[col].dataType.typeName() == "struct"]
            for col in struct_columns:
                df = df.select(F.col("*"), F.col(col + ".*"))
                nested_columns = df.select(F.col(col + ".*")).schema.names
                for nested_col in nested_columns:
                    df = df.withColumnRenamed(nested_col, f"{col}_{nested_col}")
                df = df.drop(col)
                struct_present = True
            return df, struct_present

        array_present = True
        struct_present = True

        while array_present or struct_present:
            df, array_present = explode_arrays(df, exclude_columns)
            df, struct_present = flatten_structs(df)

        return df
