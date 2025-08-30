from typing import Any

from pyspark.sql import DataFrame
from pyspark.sql.functions import col, from_json, schema_of_json, unbase64

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformDecodeAction(PipelineAction):
    """Decodes values of a specified column in the DataFrame based on the given format.

    Example:
        === "Decode JSON column"
            ```yaml
            Expand JSON:
                action: "TRANSFORM_DECODE"
                options:
                    column: "data"
                    input_format: "json"
                    schema: "quality INT, timestamp TIMESTAMP, value DOUBLE"
            ```
        === "Decode base64 column"
            ```yaml
            Decode base64:
                action: TRANSFORM_DECODE
                options:
                    column: encoded_data
                    input_format: base64
                    schema: string
            ```
    """

    name: str = "TRANSFORM_DECODE"

    def run(
        self,
        context: PipelineContext,
        *,
        column: str | None = None,
        input_format: str | None = None,
        schema: str | None = None,
        **_: Any,  # define kwargs to match the base class signature
    ) -> PipelineContext:
        """Decodes values of a specified column in the DataFrame based on the given format.

        Args:
            context: The context in which this Action is executed.
            column: The name of the column that should be decoded.
            input_format: The format from which the column should be decoded.
                Currently supported formats are 'base64' and 'json'.
            schema: For JSON input, the schema of the JSON object. If empty,
                the schema is inferred from the first row of the DataFrame. For base64 input,
                the data type to which the column is cast.

        Raises:
            ValueError: If no column is specified.
            ValueError: If no input_format is specified.
            ValueError: If the data from context is None.
            ValueError: If an invalid input_format is provided.

        Returns:
            The context after the execution of this Action, containing the DataFrame with the decoded column(s).
        """
        if not column:
            raise ValueError("No column specified.")
        if not input_format:
            raise ValueError("No input_format specified")
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data
        match input_format.lower():
            case "base64":
                df = self._decode_base64(df, column, schema)  # type: ignore
            case "json":
                df = self._decode_json(df, column, schema)  # type: ignore
            case _:
                raise ValueError(
                    f"Invalid input_format: [ '{input_format}' ]. Please specify a valid format to decode.",
                )

        return context.from_existing(data=df)  # type: ignore

    def _decode_base64(self, df: DataFrame, column: str, base64_schema: str | None):
        """Decode base64 column."""
        df_decoded = df.withColumn(column, unbase64(col(column)))
        if base64_schema:
            df_decoded = df_decoded.withColumn(column, col(column).cast(base64_schema))
        return df_decoded

    def _decode_json(self, df: DataFrame, column: str, json_schema: str | None):
        """Decode json column."""
        distinct_schemas = (
            df.select(column)
            .withColumn("json_schema", schema_of_json(col(column)))
            .select("json_schema")
            .dropDuplicates()
        )
        if not (json_schema or distinct_schemas.count() > 0):
            raise RuntimeError("Cannot infer schema from empty DataFrame.")

        elif distinct_schemas.count() > 1:
            raise RuntimeError(f"There is more than one JSON schema in column {column}.")

        if json_schema is None:
            final_json_schema = distinct_schemas.collect()[0].json_schema
        else:
            final_json_schema = json_schema  # type: ignore

        df_decoded = df.withColumn(column, from_json(col(column), final_json_schema)).select(*df.columns, f"{column}.*")

        return df_decoded
