from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformReplaceValuesAction(PipelineAction):
    """Replaces specified values in the given DataFrame.

    This method iterates over the specified `replace` dictionary, where each key is a column name
    and each value is another dictionary containing old values as keys and new values as the corresponding
    values. The method updates the DataFrame by replacing occurrences of the old values with the new ones
    in the specified columns.

    Example:
        ```yaml
        Replace Values:
            action: TRANSFORM_REPLACE_VALUES
            options:
                replace:
                    empl_function:
                        sales_employee: seller
        ```
    """

    name: str = "TRANSFORM_REPLACE_VALUES"

    def run(
        self,
        context: PipelineContext,
        *,
        replace: dict[str, dict[str, str]] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Replaces specified values in the given DataFrame.

        Args:
            context: Context in which this Action is executed.
            replace: A dictionary where each key is the column name
                and the corresponding value is another dictionary mapping old values to new values.

        Raises:
            ValueError: If no replace values are provided.
            ValueError: If the data from context is None.

        Returns:
            Context after the execution of this Action.
        """
        if not replace:
            raise ValueError("No replace values provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data
        for column, to_replace in replace.items():
            df = df.replace(to_replace=to_replace, subset=[column])  # type: ignore

        return context.from_existing(data=df)  # type: ignore
