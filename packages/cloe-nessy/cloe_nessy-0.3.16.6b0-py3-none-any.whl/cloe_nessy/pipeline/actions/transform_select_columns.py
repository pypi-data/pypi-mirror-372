from typing import Any

from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformSelectColumnsAction(PipelineAction):
    """Selects specified columns from the given DataFrame.

    This method allows you to include or exclude specific columns from the
    DataFrame. If `include_columns` is provided, only those columns will be
    selected. If `exclude_columns` is provided, all columns except those will be
    selected. The method ensures that the specified columns exist in the
    DataFrame before performing the selection.

    Example:
        Example Input Data:

        | id | name   | coordinates          | attributes                |
        |----|--------|----------------------|---------------------------|
        | 1  | Alice  | [10.0, 20.0]         | {"age": 30, "city": "NY"} |
        | 2  | Bob    | [30.0, 40.0]         | {"age": 25, "city": "LA"} |
        === "Include Columns"
            ```yaml
            Select Columns:
                action: TRANSFORM_SELECT_COLUMNS
                options:
                    include_columns:
                        - id
                        - name
                        - coordinates
            ```
            Example Output Data:

            | id | name   | coordinates          |
            |----|--------|----------------------|
            | 1  | Alice  | [10.0, 20.0]         |
            | 2  | Bob    | [30.0, 40.0]         |

        === "Exclude Columns"
            ```yaml
            Select Columns:
                action: TRANSFORM_SELECT_COLUMNS
                options:
                    exclude_columns:
                        - coordinates
            ```
            Example Output Data:

            | id | name   | attributes                |
            |----|--------|---------------------------|
            | 1  | Alice  | {"age": 30, "city": "NY"} |
            | 2  | Bob    | {"age": 25, "city": "LA"} |

    """

    name: str = "TRANSFORM_SELECT_COLUMNS"

    def run(
        self,
        context: PipelineContext,
        *,
        include_columns: list[str] | None = None,
        exclude_columns: list[str] | None = None,
        raise_on_non_existing_columns: bool = True,
        **_: Any,
    ) -> PipelineContext:
        """Selects specified columns from the given DataFrame.

        Args:
            context: Context in which this Action is executed.
            include_columns: A list of column names that should be included.
                If provided, only these columns will be selected.
            exclude_columns: A list of column names that should be excluded.
                If provided, all columns except these will be selected.
            raise_on_non_existing_columns: If True, raise an error if a specified
                column is not found in the DataFrame. If False, ignore the column
                and continue with the selection.

        Raises:
            ValueError: If a specified column is not found in the DataFrame.
            ValueError: If neither include_columns nor exclude_columns are provided,
                or if both are provided.

        Returns:
            Context after the execution of this Action.
        """
        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        df = context.data

        if (not include_columns and not exclude_columns) or (include_columns and exclude_columns):
            raise ValueError("Please define either 'include_columns' or 'exclude_columns'.")

        def check_missing_columns(df, columns, raise_on_non_existing_columns):
            if raise_on_non_existing_columns:
                missing_columns = [col for col in columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Columns not found in DataFrame: {missing_columns}")

        try:
            if include_columns:
                check_missing_columns(df, include_columns, raise_on_non_existing_columns)
                df_selected = df.select(*include_columns)
            elif exclude_columns:
                check_missing_columns(df, exclude_columns, raise_on_non_existing_columns)
                df_selected = df.drop(*exclude_columns)
        except Exception as e:
            raise ValueError(f"Column selection error: {e}") from e

        return context.from_existing(data=df_selected)  # type: ignore
