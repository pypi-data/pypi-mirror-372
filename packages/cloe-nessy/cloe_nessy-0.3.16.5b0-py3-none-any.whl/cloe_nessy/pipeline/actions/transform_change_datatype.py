from typing import Any

import pyspark.sql.functions as F

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformChangeDatatypeAction(PipelineAction):
    """Changes the datatypes of specified columns in the given DataFrame.

    !!! note "Data Types"
        We make use of the PySpark `cast` function to change the data types of
        the columns. Valid data types can be found in the [PySpark
        documentation](https://spark.apache.org/docs/3.5.3/sql-ref-datatypes.html).

    Example:
        ```yaml
        Cast Columns:
            action: TRANSFORM_CHANGE_DATATYPE
            options:
                columns:
                    id: string
                    revenue: long
        ```
    """

    name: str = "TRANSFORM_CHANGE_DATATYPE"

    def run(
        self,
        context: PipelineContext,
        *,
        columns: dict[str, str] | None = None,
        **_: Any,  # define kwargs to match the base class signature
    ) -> PipelineContext:
        """Changes the datatypes of specified columns in the given DataFrame.

        Args:
            context: The context in which this Action is executed.
            columns: A dictionary where the key is the column
                name and the value is the desired datatype.

        Raises:
            ValueError: If no columns are provided.
            ValueError: If the data from context is None.

        Returns:
            The context after the execution of this Action, containing the DataFrame with updated column datatypes.
        """
        if not columns:
            raise ValueError("No columns provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data
        change_columns = {col: F.col(col).cast(dtype) for col, dtype in columns.items()}
        df = df.withColumns(change_columns)  # type: ignore

        return context.from_existing(data=df)  # type: ignore
