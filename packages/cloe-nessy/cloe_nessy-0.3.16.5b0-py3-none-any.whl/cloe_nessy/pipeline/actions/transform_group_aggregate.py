from typing import Any

import pyspark.sql.functions as F

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformGroupAggregate(PipelineAction):
    """Performs aggregation operations on grouped data within a DataFrame.

    This class allows you to group data by specified columns and apply various aggregation functions
    to other columns. The aggregation functions can be specified as a dictionary where keys are column names
    and values are either a single aggregation function or a list of functions.

    The output DataFrame will contain the grouped columns and the aggregated columns with the aggregation
    function as a prefix to the column name.

    Example:
        ```yaml
        Transform Group Aggregate:
            action: TRANSFORM_GROUP_AGGREGATE
            options:
                grouping_columns:
                    - column1
                    - column2
                aggregations:
                    column3:
                        - sum
                        - avg
                    column4: max
        ```

        This example groups the DataFrame by `column1` and `column2` and aggregates `column3` by sum and average
        and `column4` by max. The resulting DataFrame will contain the grouped columns `column1` and `column2`
        and the aggregated columns `sum_column3`, `avg_column3`, and `max_column4`.
    """

    name: str = "TRANSFORM_GROUP_AGGREGATE"

    def run(
        self,
        context: PipelineContext,
        *,
        grouping_columns: list[str] | None = None,
        aggregations: dict[str, str | list] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Executes the aggregation on the grouped data.

        Args:
            context: The context in which this action is executed.
            grouping_columns: A list of columns to group by.
            aggregations: A dictionary where keys are column names and values are either a single
                aggregation function or a list of functions.

        Raises:
            ValueError: If the context data is None.
            ValueError: If no aggregations are provided.
            ValueError: If invalid aggregation operations are provided.
            ValueError: If columns with unsupported data types are included in the aggregations.

        Returns:
            PipelineContext: The context after the execution of this action.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        if grouping_columns is None:
            raise ValueError("Please provide at least one grouping column")
        if aggregations is None:
            raise ValueError("Please provide aggregations.")

        valid_operations = ["avg", "max", "min", "mean", "sum", "count"]

        for operation in aggregations.values():
            if isinstance(operation, list):
                if not set(operation).issubset(valid_operations):
                    raise ValueError(f"Please provide valid operations. Valid operations are {valid_operations}")
            elif isinstance(operation, str):
                if operation not in valid_operations:
                    raise ValueError(f"Please provide valid operations. Valid operations are {valid_operations}")
            else:
                raise ValueError("OPERATION DATATYPE INVALID")

        aggregation_list = []
        for column_name, aggregation in aggregations.items():
            if isinstance(aggregation, list):
                for subaggregation in aggregation:
                    aggregation_list.append(
                        getattr(F, subaggregation)(column_name).alias(f"{subaggregation}_{column_name}")
                    )
            else:
                aggregation_list.append(getattr(F, aggregation)(column_name).alias(f"{aggregation}_{column_name}"))

        df = context.data.groupBy(grouping_columns).agg(*aggregation_list)

        return context.from_existing(data=df)
