from typing import Any

import pyspark.sql.functions as F

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformConcatColumnsAction(PipelineAction):
    """Concatenates the specified columns in the given DataFrame.

    Example:
        === "concat with separator"
            ```yaml
            Concat Columns:
                action: TRANSFORM_CONCAT_COLUMNS
                options:
                    name: address
                    columns:
                        - street
                        - postcode
                        - country
                    separator: ', '
            ```
        === "concat without separator"
            ```yaml
            Concat Column:
                action: TRANSFORM_CONCAT_COLUMNS
                options:
                    name: address
                    columns:
                        - street
                        - postcode
                        - country
            ```
            !!! warning "beware of null handling"
                The `separator` option is not provided, so the default behavior is to use `concat` which returns `NULL` if any of the concatenated values is `NULL`.
    """

    name: str = "TRANSFORM_CONCAT_COLUMNS"

    def run(
        self,
        context: PipelineContext,
        *,
        name: str = "",
        columns: list[str] | None = None,
        separator: str | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Concatenates the specified columns in the given DataFrame.

        !!!warning

            # Null Handling Behavior

            The behavior of null handling differs based on whether a `separator` is provided:

            - **When `separator` is specified**: The function uses Spark's
                `concat_ws`, which **ignores `NULL` values**. In this case, `NULL`
                values are treated as empty strings (`""`) and are excluded from the
                final concatenated result.
            - **When `separator` is not specified**: The function defaults to
                using Spark's `concat`, which **returns `NULL` if any of the
                concatenated values is `NULL`**. This means the presence of a `NULL`
                in any input will make the entire output `NULL`.

        Args:
            context: The context in which this Action is executed.
            name: The name of the new concatenated column.
            columns: A list of columns to be concatenated.
            separator: The separator used between concatenated column values.

        Raises:
            ValueError: If no name is provided.
            ValueError: If no columns are provided.
            ValueError: If the data from context is None.
            ValueError: If 'columns' is not a list.

        Returns:
            The context after the execution of this Action, containing the
                DataFrame with the concatenated column.
        """
        if not name:
            raise ValueError("No name provided.")
        if not columns:
            raise ValueError("No columns provided.")

        if context.data is None:
            raise ValueError("The data from context is required for the operation.")

        df = context.data

        if isinstance(columns, list):
            if separator:
                df = df.withColumn(name, F.concat_ws(separator, *columns))  # type: ignore
            else:
                df = df.withColumn(name, F.concat(*columns))  # type: ignore
        else:
            raise ValueError("'columns' should be a list, like ['col1', 'col2',]")

        return context.from_existing(data=df)  # type: ignore
