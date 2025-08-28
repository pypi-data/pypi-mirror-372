from functools import reduce
from typing import Any

from pyspark.sql.dataframe import DataFrame

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext
from ..pipeline_step import PipelineStep


class TransformUnionAction(PipelineAction):
    """Unions multiple DataFrames together.

    This method takes the current DataFrame from the context and unites it with
    additional DataFrames specified in the `union_data` argument. All DataFrames
    must have the same schema. If any DataFrame in `union_data` is None or
    empty, a ValueError will be raised.

    Example:
        ```yaml
        Union Tables:
            action: TRANSFORM_UNION
            options:
                union_data:
                    - ((step:Filter First Table))
                    - ((step:SQL Transform Second Table))
        ```
        !!! note "Referencing a DataFrame from another step"
            The `union_data` parameter is a reference to the DataFrame from another step.
            The DataFrame is accessed using the `result` attribute of the PipelineStep. The syntax
            for referencing the DataFrame is `((step:Step Name))`, mind the double parentheses.
    """

    name: str = "TRANSFORM_UNION"

    def run(
        self,
        context: PipelineContext,
        *,
        union_data: list[PipelineStep] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Unions multiple DataFrames together.

        Args:
            context: Context in which this Action is executed.
            union_data: A list of PipelineSteps that define the DataFrames
                to union with the current context.

        Raises:
            ValueError: If no union_data is provided.
            ValueError: If the data from context is None.
            ValueError: If the data from any of the union_data is None.

        Returns:
            Context after the execution of this Action.
        """
        if not union_data:
            raise ValueError("No union_data provided.")

        # Check that all union_data contexts have valid data
        result_contexts = []
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        for ctx in union_data:
            if ctx.result is None or ctx.result.data is None:
                raise ValueError(f"Data from the context of step '{ctx.name}' is required for the operation.")
            result_contexts.append(ctx.result.data)

        # Union all DataFrames
        union_dfs = [context.data] + result_contexts
        df = reduce(DataFrame.unionAll, union_dfs)  # type: ignore

        return context.from_existing(data=df)  # type: ignore
