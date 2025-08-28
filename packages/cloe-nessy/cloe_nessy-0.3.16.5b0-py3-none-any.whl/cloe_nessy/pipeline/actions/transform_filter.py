from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformFilterAction(PipelineAction):
    """Filters the DataFrame in the given context based on a specified condition.

    Example:
        ```yaml
        Filter Columns:
            action: TRANSFORM_FILTER
            options:
                condition: city="Hamburg"
        ```
    """

    name: str = "TRANSFORM_FILTER"

    def run(
        self,
        context: PipelineContext,
        *,
        condition: str = "",
        **_: Any,
    ) -> PipelineContext:
        """Filters the DataFrame in the given context based on a specified condition.

        Args:
            context: Context in which this Action is executed.
            condition: A SQL-like expression used to filter the DataFrame.

        Raises:
            ValueError: If no condition is provided.
            ValueError: If the data from the context is None.

        Returns:
            Context after the execution of this Action, containing the filtered DataFrame.
        """
        if not condition:
            raise ValueError("No condition provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data

        df_filtered = df.filter(condition=condition)

        return context.from_existing(data=df_filtered)  # type: ignore
