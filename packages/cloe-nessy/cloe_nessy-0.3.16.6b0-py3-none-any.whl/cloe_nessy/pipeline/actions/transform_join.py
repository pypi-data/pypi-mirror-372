from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext
from ..pipeline_step import PipelineStep


class TransformJoinAction(PipelineAction):
    """Joins the current DataFrame with another DataFrame defined in joined_data.

    The join operation is performed based on specified columns and the type of
    join indicated by the `how` parameter. Supported join types can be taken
    from [PySpark
    documentation](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.join.html)

    Example:
        ```yaml
        Join Tables:
            action: TRANSFORM_JOIN
            options:
                joined_data: ((step:Transform First Table))
                join_on: id
                how: anti
        ```

        !!! note "Referencing a DataFrame from another step"
            The `joined_data` parameter is a reference to the DataFrame from another step.
            The DataFrame is accessed using the `result` attribute of the PipelineStep. The syntax
            for referencing the DataFrame is `((step:Step Name))`, mind the double parentheses.
    """

    name: str = "TRANSFORM_JOIN"

    def run(
        self,
        context: PipelineContext,
        *,
        joined_data: PipelineStep | None = None,
        join_on: list[str] | str | dict[str, str] | None = None,
        how: str = "inner",
        **_: Any,
    ) -> PipelineContext:
        """Joins the current DataFrame with another DataFrame defined in joined_data.

        Args:
            context: Context in which this Action is executed.
            joined_data: The PipelineStep context defining the DataFrame
                to join with as the right side of the join.
            join_on: A string for the join column
                name, a list of column names, or a dictionary mapping columns from the
                left DataFrame to the right DataFrame. This defines the condition for the
                join operation.
            how: The type of join to perform. Must be one of: inner, cross, outer,
                full, fullouter, left, leftouter, right, rightouter, semi, anti, etc.

        Raises:
            ValueError: If no joined_data is provided.
            ValueError: If no join_on is provided.
            ValueError: If the data from context is None.
            ValueError: If the data from the joined_data is None.

        Returns:
            Context after the execution of this Action, containing the result of the join operation.
        """
        if joined_data is None or joined_data.result is None or joined_data.result.data is None:
            raise ValueError("No joined_data provided.")
        if not join_on:
            raise ValueError("No join_on provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df_right = joined_data.result.data.alias("right")  # type: ignore
        df_left = context.data.alias("left")  # type: ignore

        if isinstance(join_on, str):
            join_condition = [join_on]
        elif isinstance(join_on, list):
            join_condition = join_on
        else:
            join_condition = [
                df_left[left_column] == df_right[right_column]  # type: ignore
                for left_column, right_column in join_on.items()
            ]

        df = df_left.join(df_right, on=join_condition, how=how)  # type: ignore

        return context.from_existing(data=df)  # type: ignore
