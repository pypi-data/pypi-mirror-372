from typing import Any

from pyspark.sql import DataFrame, DataFrameWriter
from pyspark.sql.streaming import DataStreamWriter

from .writer import BaseWriter


class FileWriter(BaseWriter):
    """Utility class for writing a DataFrame to a file."""

    def __init__(self):
        super().__init__()

    def _get_writer(self, df: DataFrame) -> DataFrameWriter:
        """Returns a DataFrameWriter."""
        return df.write

    def _get_stream_writer(self, df: DataFrame) -> DataStreamWriter:
        """Returns a DataStreamWriter."""
        return df.writeStream

    def _log_operation(self, location: str, status: str, error: str | None = None):
        """Logs the status of an operation."""
        if status == "start":
            self._console_logger.info(f"Starting to write to {location}")
        elif status == "succeeded":
            self._console_logger.info(f"Successfully wrote to {location}")
        elif status == "failed":
            self._console_logger.error(f"Failed to write to {location}: {error}")

    def _validate_trigger(self, trigger_dict: dict[str, Any]):
        """Validates the trigger type."""
        triggers = ["processingTime", "once", "continuous", "availableNow"]
        if not any(trigger in trigger_dict for trigger in triggers):
            raise ValueError(f"Invalid trigger type. Supported types are: {', '.join(triggers)}")

    def write_stream(
        self,
        data_frame: DataFrame | None = None,
        location: str | None = None,
        format: str = "delta",
        checkpoint_location: str | None = None,
        partition_cols: list[str] | None = None,
        mode: str = "append",
        trigger_dict: dict | None = None,
        options: dict[str, Any] | None = None,
        await_termination: bool = False,
        **_: Any,
    ):
        """Writes a dataframe to specified location in specified format as a stream.

        Args:
            data_frame: The DataFrame to write.
            location: The location to write the DataFrame to.
            format: The format to write the DataFrame in.
            checkpoint_location: Location of checkpoint. If None, defaults
                to the location of the table being written, with '_checkpoint_'
                added before the name.
            partition_cols: Columns to partition by.
            mode: The write mode.
            trigger_dict: A dictionary specifying the trigger configuration for the streaming query.
                Supported keys include:

                - "processingTime": Specifies a time interval (e.g., "10 seconds") for micro-batch processing.
                - "once": Processes all available data once and then stops.
                - "continuous": Specifies a time interval (e.g., "1 second") for continuous processing.
                - "availableNow": Processes all available data immediately and then stops.

                If nothing is provided, the default is {"availableNow": True}.
            options: Additional options for writing.
            await_termination: If True, the function will wait for the streaming
                query to finish before returning. This is useful for ensuring that
                the data has been fully written before proceeding with other
                operations.
        """
        if not location or not data_frame:
            raise ValueError("Location and data_frame are required for streaming.")

        self._log_operation(location, "start")
        try:
            options = options or {}
            trigger_dict = trigger_dict or {"availableNow": True}
            checkpoint_location = self._get_checkpoint_location(location, checkpoint_location)
            self._validate_trigger(trigger_dict)
            stream_writer = self._get_stream_writer(data_frame)

            stream_writer.trigger(**trigger_dict)
            stream_writer.format(format)
            stream_writer.outputMode(mode)
            stream_writer.options(**options).option("checkpointLocation", checkpoint_location)
            if partition_cols:
                stream_writer.partitionBy(partition_cols)

            query = stream_writer.start(location)
            if await_termination is True:
                query.awaitTermination()
        except Exception as e:
            self._log_operation(location, "failed", str(e))
            raise e
        else:
            self._log_operation(location, "succeeded")

    def write(
        self,
        data_frame: DataFrame,
        location: str | None = None,
        format: str = "delta",
        partition_cols: list[str] | None = None,
        mode: str = "append",
        options: dict[str, Any] | None = None,
        **_: Any,
    ):
        """Writes a dataframe to specified location in specified format."""
        if not location:
            raise ValueError("Location is required for writing to file.")

        self._log_operation(location, "start")
        try:
            options = options or {}
            df_writer = self._get_writer(data_frame)
            df_writer.format(format)
            df_writer.mode(mode)
            if partition_cols:
                df_writer.partitionBy(partition_cols)
            df_writer.options(**options)
            df_writer.save(str(location))
        except Exception as e:
            self._log_operation(location, "failed", str(e))
            raise e
        else:
            self._log_operation(location, "succeeded")
