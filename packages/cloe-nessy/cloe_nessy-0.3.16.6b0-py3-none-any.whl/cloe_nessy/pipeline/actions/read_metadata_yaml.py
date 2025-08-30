import pathlib
from typing import Any

from ...models import Schema
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class ReadMetadataYAMLAction(PipelineAction):
    """Reads schema metadata from a yaml file using the [`Schema`][cloe_nessy.models.schema] model.

    Example:
        ```yaml
        Read Schema Metadata:
            action: READ_METADATA_YAML_ACTION
            options:
                path: excel_file_folder/excel_files_june/
                file_name: sales_schema.yml
                table_name: sales
        ```
    """

    name: str = "READ_METADATA_YAML_ACTION"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        path: str | None = None,
        file_name: str | None = None,
        table_name: str | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Reads schema metadata from a yaml file using the [`Schema`][cloe_nessy.models.schema] model.

        Args:
            context: The context in which this Action is executed.
            path: The path to the data contract directory.
            file_name: The name of the file that defines the schema.
            table_name: The name of the table for which to retrieve metadata.

        Raises:
            ValueError: If any issues occur while reading the schema, such as an invalid schema,
                missing file, or missing path.

        Returns:
            The context after the execution of this Action, containing the table metadata.
        """
        if not path:
            raise ValueError("No path provided. Please specify path to schema metadata.")
        if not file_name:
            raise ValueError("No file_name provided. Please specify file name.")
        if not table_name:
            raise ValueError("No table_name provided. Please specify table name.")

        path_obj = pathlib.Path(path)

        schema, errors = Schema.read_instance_from_file(path_obj / file_name)
        if errors:
            raise ValueError(f"Errors while reading schema metadata: {errors}")
        if not schema:
            raise ValueError("No schema found in metadata.")

        table = schema.get_table_by_name(table_name=table_name)

        return context.from_existing(table_metadata=table)
