from pathlib import Path
from typing import Any

from ...models import Table
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class ReadMetadataYAMLAction(PipelineAction):
    """Reads table metadata from a yaml file using the [`Table`][cloe_nessy.models.table] model.

    Example:
        === "Managed Table"
            ```yaml
            Read Table Metadata:
                action: READ_METADATA_YAML_ACTION
                options:
                    file_path: metadata/schemas/bronze/sales_table.yml
                    catalog_name: production
                    schema_name: sales_data
            ```
        === "External Table"
            ```yaml
            Read Table Metadata:
                action: READ_METADATA_YAML_ACTION
                options:
                    file_path: metadata/schemas/bronze/sales_table.yml
                    catalog_name: production
                    schema_name: sales_data
                    storage_path: abfs://external_storage/sales_data/sales_table
            ```
    """

    name: str = "READ_METADATA_YAML_ACTION"

    def run(
        self,
        context: PipelineContext,
        *,
        file_path: str | None = None,
        catalog_name: str | None = None,
        schema_name: str | None = None,
        storage_path: str | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Reads table metadata from a yaml file using the [`Table`][cloe_nessy.models.table] model.

        Args:
            context: The context in which this Action is executed.
            file_path: The path to the file that defines the table.
            catalog_name: The name of the catalog for the table.
            schema_name: The name of the schema for the table.
            storage_path: The storage path for the table, if applicable. If not
                provided, the table will be considered a managed table.

        Raises:
            ValueError: If any issues occur while reading the table metadata, such as an invalid table,
                missing file, missing path, or missing catalog/schema names.

        Returns:
            The context after the execution of this Action, containing the table metadata.
        """
        missing_params = []
        if not file_path:
            missing_params.append("file_path")
        if not catalog_name:
            missing_params.append("catalog_name")
        if not schema_name:
            missing_params.append("schema_name")

        if missing_params:
            raise ValueError(
                f"Missing required parameters: {', '.join(missing_params)}. Please specify all required parameters."
            )

        final_file_path = Path(file_path) if file_path else Path()

        table, errors = Table.read_instance_from_file(
            final_file_path,
            catalog_name=catalog_name,
            schema_name=schema_name,
        )
        if errors:
            raise ValueError(f"Errors while reading table metadata: {errors}")
        if not table:
            raise ValueError("No table found in metadata.")

        if not table.storage_path and storage_path:
            self._console_logger.info(f"Setting storage path for table [ '{table.name}' ] to [ '{storage_path}' ]")
            table.storage_path = storage_path
            table.is_external = True

        self._console_logger.info(f"Table [ '{table.name}' ] metadata read successfully from [ '{file_path}' ]")
        return context.from_existing(table_metadata=table)
