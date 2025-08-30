from typing import Any

from ...integration.writer import CatalogWriter
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class WriteCatalogTableAction(PipelineAction):
    """Writes a DataFrame to a specified catalog table using [CatalogWriter][cloe_nessy.integration.writer.CatalogWriter].

    Example:
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
            options: PySpark options for the DataFrame.saveAsTable operation (e.g. mergeSchema:true).

        Raises:
            ValueError: If the table name is not specified or cannot be inferred from
                the context.

        Returns:
            Context after the execution of this Action.
        """
        if not options:
            options = dict()
        if partition_by is None:
            if hasattr(context.table_metadata, "partition_by"):
                partition_by = context.table_metadata.partition_by  # type: ignore

        if (table_metadata := context.table_metadata) and table_identifier is None:
            table_identifier = table_metadata.identifier
        if table_identifier is None:
            raise ValueError("Table name must be specified or a valid Table object with identifier must be set.")

        writer = CatalogWriter()
        writer.write_table(
            df=context.data,  # type: ignore
            table_identifier=table_identifier,
            mode=mode,
            partition_by=partition_by,
            options=options,
        )
        return context.from_existing()
