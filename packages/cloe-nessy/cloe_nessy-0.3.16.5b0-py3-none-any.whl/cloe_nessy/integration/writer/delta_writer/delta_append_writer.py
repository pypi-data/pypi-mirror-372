from pyspark.sql import DataFrame

from ....object_manager import table_log_decorator
from ....session import SessionManager
from ..file_writer import FileWriter
from .delta_table_operation_type import DeltaTableOperationType
from .delta_writer_base import BaseDeltaWriter


class DeltaAppendWriter(BaseDeltaWriter):
    """A class for appending DataFrames to Delta tables."""

    def __init__(self):
        super().__init__()
        self._spark = SessionManager.get_spark_session()
        self._dbutils = SessionManager.get_utils()

    @table_log_decorator(operation="append")
    def write(
        self,
        table_identifier: str,
        table_location: str,
        data_frame: DataFrame,
        ignore_empty_df: bool = False,
        options: dict[str, str] | None = None,
    ):
        """Appends the provided DataFrame to a Delta table.

        Args:
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.
            table_location: The location of the Delta table.
            data_frame: The DataFrame to append to the table.
            ignore_empty_df: If True, the function returns early without
                doing anything if the DataFrame is empty.
            options: Additional keyword arguments that will be passed to the 'write' method of the
                FileDataFrameWriter instance. These can be any parameters accepted by the 'write'
                method, which could include options for configuring the write operation, such as
                'checkpointLocation' for specifying the path where checkpoints will be stored, or
                'path' for specifying the path where the output data will be written.
        """
        if self._empty_dataframe_check(data_frame, ignore_empty_df):
            return
        writer = FileWriter()
        writer.write(
            data_frame=data_frame,
            location=table_location,
            format="DELTA",
            mode="APPEND",
            options=options,
        )
        self._report_delta_table_operation_metrics(
            table_identifier=table_identifier, operation_type=DeltaTableOperationType.WRITE
        )

    @table_log_decorator(operation="stream_append")
    def write_stream(
        self,
        table_identifier: str,
        table_location: str,
        data_frame: DataFrame,
        checkpoint_location: str | None = None,
        trigger_dict: dict | None = None,
        options: dict[str, str] | None = None,
        await_termination: bool = False,
    ):
        """Appends the provided DataFrame to a Delta table.

        Args:
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.
            table_location: The location of the Delta table.
            data_frame: The DataFrame to append to the table.
            checkpoint_location: Location of checkpoint. If None, defaults
                to the location of the table being written, with '_checkpoint_'
                added before name. Default None.
            trigger_dict: A dictionary specifying the trigger configuration for the streaming query.
                Supported keys include:

                - "processingTime": Specifies a time interval (e.g., "10 seconds") for micro-batch processing.
                - "once": Processes all available data once and then stops.
                - "continuous": Specifies a time interval (e.g., "1 second") for continuous processing.
                - "availableNow": Processes all available data immediately and then stops.

                If nothing is provided, the default is {"availableNow": True}.
            options: Additional keyword arguments that will be passed to the
                'write' method of the FileDataFrameWriter instance. These can be
                any parameters accepted by the 'write' method, which could
                include options for configuring the write operation.
            await_termination: If True, the function will wait for the streaming
                query to finish before returning. This is useful for ensuring that
                the data has been fully written before proceeding with other
                operations.

        Returns:
            None.
        """
        writer = FileWriter()
        writer.write_stream(
            data_frame=data_frame,
            location=table_location,
            format="DELTA",
            checkpoint_location=checkpoint_location,
            mode="APPEND",
            trigger_dict=trigger_dict,
            options=options,
        )
        self._report_delta_table_operation_metrics(
            table_identifier=table_identifier, operation_type=DeltaTableOperationType.WRITE
        )
