import random
import string
from typing import Any

import pyspark.sql.functions as F
import pyspark.sql.types as T
from pyspark.sql import Window

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformDeduplication(PipelineAction):
    """Deduplicates the data from the given DataFrame.

    This method deduplicates the data where the key columns are the same
    and keeps the entry with the highest values in the order_by_columns
    (can be changed to lowest by setting the parameter descending to false).

    Example:
        ```yaml
        Deduplicate Columns:
            action: TRANSFORM_DEDUPLICATION
            options:
                key_columns:
                    - id
                order_by_columns:
                    - source_file_modification_time
        ```
    """

    name: str = "TRANSFORM_DEDUPLICATION"

    def run(
        self,
        context: PipelineContext,
        *,
        key_columns: list[str] | None = None,
        order_by_columns: list[str] | None = None,
        descending: bool = True,
        **_: Any,
    ) -> PipelineContext:
        """Deduplicates the data based on key columns and order by columns.

        Args:
            context: The context in which this Action is executed.
            key_columns: A list of the key column names. The returned data only keeps one
                line of data with the same key columns.
            order_by_columns: A list of order by column names. The returned data keeps the
                first line of data with the same key columns ordered by these columns.
            descending: Whether to sort descending or ascending.

        Raises:
            ValueError: If no key_columns are specified.
            ValueError: If no order_by_columns are specified.
            ValueError: If the data from context is None.
            ValueError: If key_columns and order_by_columns overlap.
            ValueError: If key_columns or order_by_columns contain Nulls.

        Returns:
            The context after the execution of this Action, containing the DataFrame with the deduplicated data.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")
        if key_columns is None:
            raise ValueError("Please provide at least one key column.")
        if order_by_columns is None:
            raise ValueError("Please provide at least one order by column.")

        # check if the key_columns and order_by_columns are the same
        if len(set(key_columns) & set(order_by_columns)) != 0:
            raise ValueError("The key_columns and order_by_columns cannot contain the same column")

        # check if the key_columns and order_by_columns are not null
        df_nulls = context.data.filter(F.greatest(*[F.col(c).isNull() for c in key_columns + order_by_columns]) == 1)
        if df_nulls.head(1):  # if the filteredDataFrame is not empty
            raise ValueError(
                "The key_columns and order_by_columns cannot be null. Please check the quality of the provided columns (null handling)"
            )

        # check if the order_by columns have the preferred data types
        recommended_order_by_data_types = [
            T.TimestampType(),
            T.TimestampNTZType(),
            T.DataType(),
            T.IntegerType(),
            T.LongType(),
            T.DoubleType(),
            T.FloatType(),
            T.DecimalType(),
        ]

        for c in context.data.schema:
            if c.name in order_by_columns and c.dataType not in recommended_order_by_data_types:
                log_message = (
                    f"action_name : {self.name} | message : order_by_column `{c.name}` is of type {c.dataType}; "
                    "recommended data types are {recommended_order_by_data_types}"
                )
                self._console_logger.warning(log_message)
                self._tabular_logger.warning(log_message)

        # sort the order_by columns in the preferred order
        if descending:
            order_by_list = [F.col(col_name).desc() for col_name in order_by_columns]
        else:
            order_by_list = [F.col(col_name).asc() for col_name in order_by_columns]

        # create the window specification
        window_specification = Window.partitionBy(key_columns).orderBy(order_by_list)

        # generate a column name that is not in the input dataframe
        def generate_random_string(length):
            return "".join(random.choice(string.ascii_uppercase) for _ in range(length))

        row_number_col_name = generate_random_string(20)
        while row_number_col_name in context.data.columns:
            row_number_col_name = generate_random_string(20)

        # drop the duplicates
        df = (
            context.data.withColumn(row_number_col_name, F.row_number().over(window_specification))
            .filter(F.col(row_number_col_name) == 1)
            .drop(row_number_col_name)
        )
        return context.from_existing(data=df)
