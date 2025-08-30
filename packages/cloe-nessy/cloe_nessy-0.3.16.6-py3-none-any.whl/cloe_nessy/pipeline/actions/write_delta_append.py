from typing import Any

from ...integration.writer import DeltaAppendWriter
from ...models.adapter import UnityCatalogAdapter
from ...pipeline import PipelineAction, PipelineContext


class WriteDeltaAppendAction(PipelineAction):
    """This class implements an Append action for an ETL pipeline.

    The WriteDeltaAppendAction appends a Dataframe to Delta Table.

    Returns:
        None.
    """

    name: str = "WRITE_DELTA_APPEND"

    def run(
        self,
        context: PipelineContext,
        *,
        table_identifier: str | None = None,
        ignore_empty_df: bool = False,
        options: dict[str, Any] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Merge the dataframe into the delta table.

        Args:
            context: Context in which this Action is executed.
            table_identifier: The identifier of the table. If passed, the
                UC Adapter will be used to create a table object. Otherwise the Table
                object will be created from the table metadata in the context.
            ignore_empty_df: A flag indicating whether to ignore an empty source dataframe.
            options: Additional options for the append writer.

        Raises:
            ValueError: If the table does not exist.
            ValueError: If the data is not set in the pipeline context.
            ValueError: If the table metadata is empty.

        Returns:
            Pipeline Context
        """
        delta_append_writer = DeltaAppendWriter()

        if context.data is None:
            raise ValueError("Data is required for the append operation.")
        if context.table_metadata is None and table_identifier is None:
            raise ValueError("Table metadata or a table identifier are required for the append operation.")

        if table_identifier is not None:
            context.table_metadata = UnityCatalogAdapter().get_table_by_name(table_identifier)
        else:
            if context.table_metadata is None:
                raise ValueError("Table metadata is required.")

        if context.table_metadata is None:
            raise ValueError("Table metadata is required.")

        delta_append_writer.write(
            table_identifier=context.table_metadata.identifier,
            table_location=context.table_metadata.storage_path,
            data_frame=context.data,
            ignore_empty_df=ignore_empty_df,
            options=options,
        )
        return context.from_existing()
