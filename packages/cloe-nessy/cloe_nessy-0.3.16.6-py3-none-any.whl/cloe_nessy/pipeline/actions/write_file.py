from typing import Any

from ...integration.writer import FileWriter
from ...pipeline import PipelineAction, PipelineContext


class WriteFileAction(PipelineAction):
    """This class implements a Write action for an ETL pipeline.

    The WriteFileAction writes a Dataframe to a storage location defined in the
    options using the [`FileWriter`][cloe_nessy.integration.writer.FileWriter] class.

    Example:
        ```yaml
        Write to File:
            action: WRITE_FILE
            options:
                path: "path/to/location"
                format: "parquet"
                partition_cols: ["date"]
                mode: "append"
                is_stream: False
                options:
                    mergeSchema: "true"
        ```
    """

    name: str = "WRITE_FILE"

    def run(
        self,
        context: PipelineContext,
        *,
        path: str = "",
        format: str = "delta",
        partition_cols: list[str] | None = None,
        mode: str = "append",
        is_stream: bool = False,
        options: dict[str, str] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Writes a file to a location.

        Args:
            context: Context in which this Action is executed.
            path: Location to write data to.
            format: Format of files to write.
            partition_cols: Columns to partition on. If None, the writer will try to get the partition
                columns from the metadata. Default None.
            mode: Specifies the behavior when data or table already exists.
            is_stream: If True, use the `write_stream` method of the writer.
            options: Additional options passed to the writer.

        Raises:
            ValueError: If no path is provided.
            ValueError: If the table metadata is empty.

        Returns:
            Pipeline Context
        """
        if not path:
            raise ValueError("No path provided. Please specify path to write data to.")
        if not options:
            options = {}

        if context.data is None:
            raise ValueError("Data context is required for the operation.")

        if partition_cols is None:
            if context.table_metadata is None:
                partition_cols = []
            else:
                partition_cols = context.table_metadata.partition_by
        writer = FileWriter()
        if not is_stream:
            writer.write(
                data_frame=context.data,
                location=path,
                format=format,
                partition_cols=partition_cols,
                mode=mode,
                options=options,
            )
        else:
            writer.write_stream(
                data_frame=context.data,
                location=path,
                format=format,
                mode=mode,
                partition_cols=partition_cols,
                options=options,
            )

        return context.from_existing()
