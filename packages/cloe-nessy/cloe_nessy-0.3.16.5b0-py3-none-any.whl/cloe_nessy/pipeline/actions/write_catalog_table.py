from typing import Any

from ...integration.writer import CatalogWriter
from ...object_manager import TableManager
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class WriteCatalogTableAction(PipelineAction):
    """Writes a DataFrame to a specified catalog table using [CatalogWriter][cloe_nessy.integration.writer.CatalogWriter].

    Examples:
        === "Batch Write"
            ```yaml
            Write Table to Catalog:
                action: WRITE_CATALOG_TABLE
                options:
                    table_identifier: my_catalog.business_schema.sales_table
                    mode: append
                    partition_by: day
                    options:
                        mergeSchema: true
            ```
        === "Streaming Write"
            ```yaml
            Write Table to Catalog Stream:
                action: WRITE_CATALOG_TABLE
                options:
                    table_identifier: my_catalog.business_schema.sales_table
                    mode: append
                    checkpoint_location: /path/to/checkpoint
                    trigger_dict:
                        processingTime: 10 seconds
                    options:
                        mergeSchema: true
            ```
    """

    name: str = "WRITE_CATALOG_TABLE"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        table_identifier: str | None = None,
        mode: str = "append",
        partition_by: str | list[str] | None = None,
        options: dict[str, str] | None = None,
        checkpoint_location: str | None = None,
        trigger_dict: dict | None = None,
        await_termination: bool = False,
        **_: Any,
    ) -> PipelineContext:
        """Writes a DataFrame to a specified catalog table.

        Args:
            context: Context in which this Action is executed.
            table_identifier: The table identifier in the unity catalog in the
                format 'catalog.schema.table'. If not provided, attempts to use the
                context's table metadata.
            mode: The write mode. One of 'append', 'overwrite', 'error',
                'errorifexists', or 'ignore'.
            partition_by: Names of the partitioning columns.
            checkpoint_location: Location for checkpointing.
            trigger_dict: A dictionary specifying the trigger configuration for the streaming query.
            await_termination: If True, the function will wait for the streaming
                query to finish before returning.
            options: Additional options for the DataFrame write operation.

        Raises:
            ValueError: If the table name is not specified or cannot be inferred from
                the context.

        Returns:
            Context after the execution of this Action.
        """
        if not options:
            options = dict()
        streaming = context.runtime_info and context.runtime_info.get("streaming")
        if streaming and not checkpoint_location:
            raise ValueError("Checkpoint location must be specified for streaming writes.")
        if partition_by is None:
            if (
                context.table_metadata is not None
                and hasattr(context.table_metadata, "partition_by")
                and not context.table_metadata.liquid_clustering
            ):
                partition_by = context.table_metadata.partition_by  # type: ignore

        if (table_metadata := context.table_metadata) and table_identifier is None:
            table_identifier = table_metadata.identifier
        if table_identifier is None:
            raise ValueError("Table name must be specified or a valid Table object with identifier must be set.")

        if table_metadata:
            manager = TableManager()
            manager.create_table(table=table_metadata, ignore_if_exists=True, replace=False)

        writer = CatalogWriter()

        if streaming:
            writer.write_stream(
                df=context.data,  # type: ignore
                table_identifier=table_identifier,
                checkpoint_location=checkpoint_location,
                trigger_dict=trigger_dict,
                options=options,
                mode=mode,
                await_termination=await_termination,
            )
        else:
            writer.write(
                df=context.data,  # type: ignore
                table_identifier=table_identifier,
                mode=mode,
                partition_by=partition_by,
                options=options,
            )
        return context.from_existing()
