import logging
from abc import ABC
from dataclasses import dataclass, field

from pyspark.sql import DataFrame, Row
from pyspark.sql.functions import col, concat, concat_ws, format_string, lit

from ....object_manager import TableManager
from ....session import SessionManager
from ..writer import BaseWriter
from .delta_table_operation_type import DeltaTableOperationType
from .exceptions import EmptyDataframeError


@dataclass
class DeltaWriterLogs:
    """Dataclass defining the delta writer logs table."""

    logger_name = "Tabular:DeltaWriter"
    log_type: str = "nessy_simple_logs"
    uc_table_name: str = "nessy_simple_logs"
    uc_table_columns: dict[str, str] = field(
        default_factory=lambda: {
            "message": "STRING",
        }
    )


@dataclass
class TableOperationMetricsLogs:
    """Dataclass defining the table operation metrics logs table."""

    logger_name = "Tabular:TableOperationMetrics"
    log_type: str = "nessy_table_operation_metrics"
    uc_table_name: str = "nessy_table_operation_metrics"
    uc_table_columns: dict[str, str] = field(
        default_factory=lambda: {
            "timestamp": "TIMESTAMP",
            "table_identifier": "STRING",
            "operation_type": "STRING",
            "metric": "STRING",
            "value": "STRING",
            "user_name": "STRING",
            "job_id": "STRING",
            "job_run_id": "STRING",
            "run_id": "STRING",
            "notebook_id": "STRING",
            "cluster_id": "STRING",
        }
    )


class BaseDeltaWriter(BaseWriter, ABC):
    """A class for writing DataFrames to Delta tables."""

    def __init__(
        self,
        tabular_logger: logging.Logger | None = None,
        table_operation_metrics_logger: logging.Logger | None = None,
    ):
        super().__init__()
        self._spark = SessionManager.get_spark_session()
        self._dbutils = SessionManager.get_utils()
        self._table_operation_metrics_logger = table_operation_metrics_logger or self.get_tabular_logger(
            **DeltaWriterLogs().__dict__
        )
        self.table_manager = TableManager()
        self._tabular_logger = tabular_logger or self.get_tabular_logger(**DeltaWriterLogs().__dict__)

    def _delta_operation_log(self, table_identifier: str, operation_type: DeltaTableOperationType) -> dict:
        """Returns a dictionary containing the most recent delta log of a Delta table for given operation type.

        Args:
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.
            operation_type: A DeltaTableOperationType
                object specifying the type of operation for which metrics should
                be retrieved (UPDATE, DELETE, MERGE or WRITE).

        Returns:
            dict: A dictionary containing the operation log.
        """
        delta_history = self._spark.sql(f"DESCRIBE HISTORY {table_identifier}")

        try:
            operation_log: dict = (
                delta_history.filter(col("operation") == operation_type.name.replace("_", " "))
                .orderBy("version", ascending=False)
                .collect()[0]
                .asDict()
            )
        except IndexError:
            operation_log = {}

        return operation_log

    def _report_delta_table_operation_metrics(
        self, table_identifier: str, operation_type: DeltaTableOperationType
    ) -> None:
        """Logs the most recent metrics of a Delta table for given operation type.

        Args:
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.
            operation_type: A DeltaTableOperationType object specifying the type
                of operation for which metrics should be retrieved (UPDATE, DELETE,
                MERGE or WRITE).
        """
        operation_log = self._delta_operation_log(table_identifier, operation_type)
        timestamp = operation_log.get("timestamp")
        user_name = operation_log.get("userName")
        job_id = (operation_log.get("job") or Row(jobId=None)).asDict().get("jobId")
        job_run_id = (operation_log.get("job") or Row(jobRunId=None)).asDict().get("jobRunId")
        run_id = (operation_log.get("job") or Row(runId=None)).asDict().get("runId")
        notebook_id = (operation_log.get("notebook") or Row(notebook_id=None)).asDict().get("notebookId")
        cluster_id = operation_log.get("clusterId")
        affected_rows = {
            k: v for k, v in operation_log.get("operationMetrics", {}).items() if k in operation_type.value
        }
        for metric, value in affected_rows.items():
            log_message = f"""timestamp: {timestamp} |
                                table_identifier: {table_identifier} |
                                operation_type: {operation_type.name} |
                                metric_name: {metric} |
                                metric_value: {value} |
                                user_name: {user_name} |
                                job_id: {job_id} |
                                job_run_id: {job_run_id} |
                                run_id: {run_id} |
                                notebook_id: {notebook_id} |
                                cluster_id: {cluster_id}
                            """
            self._table_operation_metrics_logger.info(log_message)

    @staticmethod
    def _merge_match_conditions(columns: list[str]) -> str:
        """Merges match conditions of the given columns into a single string.

        This function is used to generate an SQL query to match rows between two tables based on
        the specified columns.

        Args:
            columns: A list of strings representing the names of the columns to match.

        Returns:
            A string containing the match conditions, separated by " AND "

        Example:
            ```python
            _merge_match_conditions(["column1", "column2"]) # "target.column1 <=> source.column1 AND target.column2 <=> source.column2"
            ```
        """
        return " AND ".join([f"target.`{c}` <=> source.`{c}`" for c in columns])

    @staticmethod
    def _partition_pruning_conditions(df, partition_cols: list[str] | None) -> str:
        """Generates partition pruning conditions for an SQL query.

        This function is used to optimize the performance of an SQL query by only scanning the
        necessary partitions in a table, based on the specified partition columns and the data
        in a Spark dataframe.

        Args:
            df: A Spark dataframe containing the data to generate the partition pruning
                conditions from.
            partition_cols: A list of strings representing the names of the
                partition columns.

        Returns:
            A string, representing the partition pruning conditions.

        Example:
            ```python
            _partition_pruning_conditions(df, ["column1", "column2"])
            "(target.column1 = 'value1' AND target.column2 = 'value2') OR (target.column1 = 'value3'
                AND target.column2 = 'value4')"
            ```
        """
        if not partition_cols:
            return ""
        pruning_conditions = (
            df.select(*partition_cols)
            .distinct()
            .select([format_string("target.`%s` = '%s'", lit(c), col(c)).alias(c) for c in partition_cols])
            .withColumn("result", concat(lit("("), concat_ws(" AND ", *partition_cols), lit(")")))
            .select("result")
            .toPandas()
            .result.str.cat(sep=" OR ")
        )
        pruning_conditions = "(" + pruning_conditions + ")"

        return str(pruning_conditions)

    def _empty_dataframe_check(self, df: DataFrame, ignore_empty_df: bool) -> bool | None:
        """Checks if a DataFrame is empty and raises an exception if it is not expected to be empty.

        Args:
            df: The DataFrame to check for emptiness.
            ignore_empty_df: If True, the function will return without raising
                an exception if the DataFrame is empty. If False, an EmptyDataframeException
                will be raised.

        Raises:
            EmptyDataframeException: If the DataFrame is empty and ignore_empty_df is False.
        """
        if df.isEmpty():
            if ignore_empty_df:
                return True
            raise EmptyDataframeError(
                "EMPTY DATAFRAME, nothing to write. If this is expected, consider setting `ignore_empty_df` to True.",
            )
        return None
