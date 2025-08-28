import uuid
from typing import Any

from ...session import SessionManager
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class TransformSqlAction(PipelineAction):
    """Executes a SQL statement on a DataFrame within the provided context.

    A temporary view is created from the current DataFrame, and the SQL
    statement is executed on that view. The resulting DataFrame is returned.

    Example:
        ```yaml
        SQL Transform:
            action: TRANSFORM_SQL
            options:
                sql_statement: select city, revenue, firm from {DATA_FRAME} where product="Databricks"
        ```
        !!! note
            The SQL statement should reference the DataFrame as "{DATA_FRAME}".
            This nessy specific placeholder will be replaced with your input
            DataFrame from the context. If your pipeline is defined as an
            f-string, you can escape the curly braces by doubling them, e.g.,
            "{{DATA_FRAME}}".
    """

    name: str = "TRANSFORM_SQL"

    def run(
        self,
        context: PipelineContext,
        *,
        sql_statement: str = "",
        **kwargs: Any,
    ) -> PipelineContext:
        """Executes a SQL statement on a DataFrame within the provided context.

        Args:
            context: Context in which this Action is executed.
            sql_statement: A string containing the SQL statement to be
                executed. The source table should be referred to as "{DATA_FRAME}".
            **kwargs: Additional keyword arguments are passed as placeholders to the
                SQL statement.

        Raises:
            ValueError: If "{DATA_FRAME}" is not included in the SQL statement.
            ValueError: If no SQL statement is provided.
            ValueError: If the data from the context is None.

        Returns:
            Context after the execution of this Action, containing the DataFrame resulting from the SQL statement.
        """
        if not sql_statement:
            raise ValueError("No SQL statement provided.")

        if context.data is None:
            raise ValueError("Data from the context is required for the operation.")

        _spark = SessionManager.get_spark_session()

        temp_view_name = str(uuid.uuid1()).replace("-", "_")
        context.data.createTempView(temp_view_name)

        if "FROM {DATA_FRAME}".casefold() not in sql_statement.casefold():
            raise ValueError("Please use 'FROM {DATA_FRAME}' in your SQL statement.")

        df = _spark.sql(sql_statement.format(DATA_FRAME=temp_view_name, **kwargs))

        return context.from_existing(data=df)
