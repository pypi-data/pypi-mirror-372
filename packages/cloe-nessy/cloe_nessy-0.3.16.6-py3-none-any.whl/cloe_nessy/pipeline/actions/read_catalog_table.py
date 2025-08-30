from typing import Any

from ...integration.reader import CatalogReader
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class ReadCatalogTableAction(PipelineAction):
    """Reads a table from Unity Catalog using a specified table identifier and optional reader configurations.

    This function retrieves data from a catalog table using the
    [`CatalogReader`][cloe_nessy.integration.reader.catalog_reader] identified
    by either the `table_identifier` parameter or the `table_metadata` from the
    provided `PipelineContext` of a previous step. The retrieved data is loaded
    into a DataFrame and returned as part of an updated `PipelineContext`.

    Example:
        ```yaml
        Read Sales Table:
            action: READ_CATALOG_TABLE
            options:
                table_identifier: my_catalog.business_schema.sales_table
                options: <options for the CatalogReader read method>
        ```
    """

    name: str = "READ_CATALOG_TABLE"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        table_identifier: str | None = None,
        options: dict[str, str] | None = None,
        **_: Any,  # define kwargs to match the base class signature
    ) -> PipelineContext:
        """Reads a table from Unity Catalog using a specified table identifier and optional reader configurations.

        Args:
            context: The pipeline's context, which contains
                metadata and configuration for the action.
            table_identifier: The identifier of the catalog table to
                read. If not provided, the function will attempt to use the table
                identifier from the `table_metadata` in the `context`.
            options: A dictionary of options for customizing
                the [`CatalogReader`][cloe_nessy.integration.reader.catalog_reader]
                behavior, such as filters or reading modes. Defaults to None.

        Raises:
            ValueError: If neither `table_identifier` nor `table_metadata.identifier` in the `context` is provided.

        Returns:
        An updated pipeline context containing the data read from the catalog table as a DataFrame.
        """
        if not options:
            options = dict()

        if (table_metadata := context.table_metadata) and table_identifier is None:
            table_identifier = table_metadata.identifier
        if table_identifier is None:
            raise ValueError("Table name must be specified or a valid Table object with identifier must be set.")

        table_reader = CatalogReader()
        df = table_reader.read(table_identifier=table_identifier, options=options)
        return context.from_existing(data=df)
