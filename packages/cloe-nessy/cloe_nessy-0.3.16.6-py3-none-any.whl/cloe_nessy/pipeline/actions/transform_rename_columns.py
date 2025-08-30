from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformRenameColumnsAction(PipelineAction):
    """Renames the specified columns in the DataFrame.

    This method updates the DataFrame in the provided context by renaming columns according
    to the mapping defined in the `columns` dictionary, where each key represents an old column
    name and its corresponding value represents the new column name.

    Example:
        ```yaml
        Rename Column:
            action: TRANSFORM_RENAME_COLUMNS
            options:
                columns:
                    a_very_long_column_name: shortname
        ```
    """

    name: str = "TRANSFORM_RENAME_COLUMNS"

    def run(
        self,
        context: PipelineContext,
        *,
        columns: dict[str, str] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Renames the specified columns in the DataFrame.

        Args:
            context: Context in which this Action is executed.
            columns: A dictionary where the key is the old column name
                and the value is the new column name.

        Raises:
            ValueError: If no columns are provided.
            ValueError: If the data from context is None.

        Returns:
            Context after the execution of this Action.
        """
        if not columns:
            raise ValueError("No columns provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data

        if isinstance(columns, dict):
            df = df.withColumnsRenamed(columns)
        else:
            raise ValueError("'columns' should be a dict, like {'old_name_1':'new_name_1', 'old_name_2':'new_name_2'}")

        return context.from_existing(data=df)  # type: ignore
