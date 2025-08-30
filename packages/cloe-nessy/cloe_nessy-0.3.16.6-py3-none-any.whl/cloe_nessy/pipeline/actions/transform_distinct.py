from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformDistinctAction(PipelineAction):
    """Selects distinct rows from the DataFrame in the given context.

    If a subset is given these columns are used for duplicate comparison. If no subset is given all columns are used.

    Example:
        ```yaml
        Distinct Columns:
            action: TRANSFORM_DISTINCT
            options:
                subset:
                    - first_name
                    - last_name
        ```
    """

    name: str = "TRANSFORM_DISTINCT"

    def run(
        self,
        context: PipelineContext,
        *,
        subset: list[str] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Selects distinct rows from the DataFrame in the given context.

        Args:
            context: The context in which this Action is executed.
            subset: List of column names to use for duplicate comparison (default All columns).

        Raises:
            ValueError: If the data from the context is None.

        Returns:
            The context after the execution of this Action, containing the DataFrame with distinct rows.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        # check if all columns that are part of the subset are actually part of the dataframe.
        if subset is not None:
            subset_columns_not_in_dataframe = set(subset) - set(context.data.columns)
            if len(subset_columns_not_in_dataframe) != 0:
                raise ValueError(
                    f"The following subset columns are not part of the dataframe: {subset_columns_not_in_dataframe}"
                )

        df = context.data.dropDuplicates(subset=subset)

        return context.from_existing(data=df)  # type: ignore
