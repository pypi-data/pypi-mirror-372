from typing import Any

from pyspark.errors.exceptions.base import IllegalArgumentException
from pyspark.sql import functions as F

from ...pipeline import PipelineAction, PipelineContext


class TransformConvertTimestampAction(PipelineAction):
    """This class implements a Transform action for an ETL pipeline.

    This action performs timestamp based conversions.

    Example:
        ```yaml
        Convert Timestamp:
            action: TRANSFORM_CONVERT_TIMESTAMP
            options:
                column: my_timestamp_column
                source_format: unixtime
                target_format: yyyy-MM-dd HH:mm:ss
        ```
    """

    name: str = "TRANSFORM_CONVERT_TIMESTAMP"

    def run(
        self,
        context: PipelineContext,
        *,
        column: str = "",
        source_format: str = "",
        target_format: str = "",
        **_: Any,
    ) -> PipelineContext:
        """Converts a column from a given source format to a new format.

        Args:
            context: Context in which this Action is executed.
            column: The column that should be converted.
            source_format: Initial format type of the column.
            target_format: Desired format type of the column. This also supports
            passing a format string like 'yyyy-MM-dd HH:mm:ss'.

        Raises:
            ValueError: If no column, source_format and target_format are provided.
            ValueError: If source_format or target_format are not supported.

        Returns:
            PipelineContext: Context after the execution of this Action.
        """
        if not column:
            raise ValueError("No column provided.")
        if not source_format:
            raise ValueError("No source_format provided.")
        if not target_format:
            raise ValueError("No target_format provided.")
        if context.data is None:
            raise ValueError("Context DataFrame is required.")
        df = context.data

        match source_format:
            # convert always to timestamp first
            case "unixtime":
                df = df.withColumn(column, F.from_unixtime(F.col(column)))
            case "unixtime_ms":
                df = df.withColumn(column, F.to_timestamp(F.col(column) / 1000))
            case "string":
                df = df.withColumn(column, F.to_timestamp(F.col(column)))
            case "timestamp":
                pass
            case _:
                raise ValueError(f"Unknown source_format {source_format}")

        match target_format:
            # convert from timestamp to desired output format
            case "timestamp":
                pass
            case "unixtime":
                df = df.withColumn(column, F.to_unix_timestamp(F.col(column)))
            case _:
                try:
                    df = df.withColumn(column, F.date_format(F.col(column), target_format))
                except IllegalArgumentException as e:
                    raise ValueError(f"Invalid target_format {target_format}") from e

        return context.from_existing(data=df)
