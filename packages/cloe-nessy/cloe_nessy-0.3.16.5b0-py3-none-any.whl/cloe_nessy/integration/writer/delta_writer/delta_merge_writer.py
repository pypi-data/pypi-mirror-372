from typing import Any, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pyspark.sql import DataFrame

from ....models import Table
from ....object_manager import table_log_decorator
from ....session import SessionManager
from .delta_table_operation_type import DeltaTableOperationType
from .delta_writer_base import BaseDeltaWriter


class DeltaMergeConfig(BaseModel):
    """Configuration for Merge options.

    Args:
        dataframe_columns: The columns of the DataFrame.
        key_columns: List of column names that form the key for the merge
            operation.
        when_matched_update: Flag to specify whether to perform an update
            operation when matching records are found in the target Delta table.
        when_matched_delete: Flag to specify whether to perform a delete
            operation when matching records are found in the target Delta table.
        when_not_matched_insert: Flag to specify whether to perform an insert
            operation when matching records are not found in the target Delta
            table.
        cols_to_exclude_from_update: List of column names to be excluded from
            the update in the target Delta table.
        use_partition_pruning: Flag to specify whether to use partition
            pruning to optimize the performance of the merge operation.
        partition_by: List of column names to partition by.
    """

    dataframe_columns: list[str]
    key_columns: list[str]
    cols_to_exclude_from_update: list[str] = Field(default_factory=list)
    when_matched_update: bool = True
    when_matched_delete: bool = False
    when_not_matched_insert: bool = True
    use_partition_pruning: bool = True
    partition_by: list[str] = Field(default_factory=list)
    cols_to_merge: list[str] = Field(default_factory=list, alias="_cols_to_merge")
    cols_to_update: set[str] = Field(default_factory=set, alias="_cols_to_update")
    cols_to_insert: set[str] = Field(default_factory=set, alias="_cols_to_insert")
    final_cols_to_update: dict[str, str] = Field(default_factory=dict)
    final_cols_to_insert: dict[str, str] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @model_validator(mode="before")
    @classmethod
    def _validate_update_delete(cls, config: Any):
        """Update and delete operations must be mutually exclusive."""
        if config.get("when_matched_update") and config.get("when_matched_delete"):
            raise ValueError("Update and delete operations cannot be used together.")
        return config

    @model_validator(mode="before")
    @classmethod
    def _validate_key_columns(cls, config: Any):
        """Key columns must exist in the data frame."""
        key_columns = config.get("key_columns")
        dataframe_columns = config.get("dataframe_columns")
        if not set(key_columns).issubset(set(dataframe_columns)):
            raise ValueError("Key columns must exist in the DataFrame columns.")
        return config

    @model_validator(mode="before")
    @classmethod
    def _derive_merge_columns(cls, config: Any):
        """Derive update and insert columns from the DataFrame columns."""
        dataframe_columns = config.get("dataframe_columns", [])
        config["_cols_to_merge"] = list(set(dataframe_columns))
        if config.get("cols_to_exclude_from_update"):
            config["_cols_to_update"] = set(config["_cols_to_merge"]) - set(config["cols_to_exclude_from_update"])
        else:
            config["_cols_to_update"] = set(config["_cols_to_merge"])

        config["_cols_to_insert"] = config["_cols_to_merge"]
        config["final_cols_to_update"] = {col: f"source.{col}" for col in config["_cols_to_update"]}
        config["final_cols_to_insert"] = {col: f"source.{col}" for col in config["_cols_to_insert"]}
        return config

    @model_validator(mode="after")
    @classmethod
    def _validate_partition_pruning(cls, config: Self):
        """If partition_pruning is set, the partition by columns must be known."""
        if config.use_partition_pruning is True and not config.partition_by:
            raise ValueError("Partition columns must be specified when using partition pruning.")
        return config

    @model_validator(mode="after")
    @classmethod
    def _validate_cols_exist(cls, config: Any):
        """If partition_pruning is set, the partition by columns must be known."""
        if any(col not in config.cols_to_merge for col in config.cols_to_update) or any(
            col not in config.cols_to_merge for col in config.cols_to_insert
        ):
            raise ValueError(
                "You specified column names for UPDATE or INSERT that either don't exist in the dataframe "
                "or are explicitly excluded from the MERGE.",
            )
        return config


class DeltaMergeWriter(BaseDeltaWriter):
    """A class for merging DataFrames to Delta tables."""

    def __init__(self):
        super().__init__()
        self._spark = SessionManager.get_spark_session()
        self._dbutils = SessionManager.get_utils()

    def _validate_table_inputs(
        self, table: Table | None, table_identifier: str | None, storage_path: str | None
    ) -> tuple[str, str]:
        """Validates and retrieves table identifier and storage path."""
        if table is None and (table_identifier is None or storage_path is None):
            raise ValueError("Either a Table object or table_identifier and storage_path must be provided.")
        if table is not None:
            table_identifier = table.identifier
            storage_path = str(table.storage_path)
        if not storage_path:
            raise ValueError("Storage path must be provided or extracted from the Table object.")
        assert table_identifier is not None, "Table identifier must be provided."
        return table_identifier, storage_path

    def _build_match_conditions(self, data_frame: DataFrame, config: DeltaMergeConfig) -> str:
        """Builds match conditions for the Delta table merge."""
        match_conditions = self._merge_match_conditions(config.key_columns)
        if config.use_partition_pruning:
            match_conditions_list = [match_conditions] + [
                self._partition_pruning_conditions(data_frame, config.partition_by),
            ]
            match_conditions = " AND ".join(match_conditions_list)
        return match_conditions

    def _build_merge_operations(
        self, delta_table, data_frame: DataFrame, config: DeltaMergeConfig, match_conditions: str
    ):
        """Builds the Delta table merge operations."""
        delta_table_merge = delta_table.alias("target").merge(
            source=data_frame.alias("source"),
            condition=match_conditions,
        )
        if config.when_matched_update:
            delta_table_merge = delta_table_merge.whenMatchedUpdate(set=config.final_cols_to_update)
        elif config.when_matched_delete:
            delta_table_merge = delta_table_merge.whenMatchedDelete()
        if config.when_not_matched_insert:
            delta_table_merge = delta_table_merge.whenNotMatchedInsert(values=config.final_cols_to_insert)
        return delta_table_merge

    @table_log_decorator(operation="merge")
    def write(
        self,
        data_frame: DataFrame,
        table: Table | None = None,
        table_identifier: str | None = None,
        storage_path: str | None = None,
        ignore_empty_df: bool = False,
        **kwargs: Any,
    ):
        """Merges the data in a spark DataFrame into a Delta table.

        This function performs a merge operation between a DataFrame and a Delta
        table. The function supports update, delete, and insert operations on
        the target Delta table based on conditions specified by the user. The
        function also supports partition pruning to optimize the performance of
        the merge operation.

        Args:
            table: The Table object representing the Delta table.
            table_identifier: The identifier of the Delta table in the format
                'catalog.schema.table'.
            storage_path: The location of the Delta table.
            data_frame: The DataFrame to be merged into the Delta table.
            ignore_empty_df: A flag indicating whether to ignore an empty source
                dataframe.
            kwargs: Passed to the
                [`DeltaMergeConfig`][cloe_nessy.integration.writer.delta_merge_writer.DeltaMergeConfig].

        Raises:
            ValueError: If both, table and table_identifier or storage_path are provided.
            EmptyDataframeException: If the source dataframe is empty and
                ignore_empty_df is False.
            ValueError: If the specified columns for update or insert do not
                exist in the DataFrame or are explicitly excluded from the
                merge operation.
            ValueError: If partition columns are not specified when using
                partition pruning.
        """
        if self._empty_dataframe_check(data_frame, ignore_empty_df):
            return
        table_identifier, storage_path = self._validate_table_inputs(table, table_identifier, storage_path)

        config = DeltaMergeConfig(dataframe_columns=data_frame.columns, **kwargs)

        delta_table = self.table_manager.get_delta_table(
            table=table,
            location=storage_path,
            spark=data_frame.sparkSession,
        )

        match_conditions = self._build_match_conditions(data_frame, config)

        delta_table_merge = self._build_merge_operations(delta_table, data_frame, config, match_conditions)
        delta_table_merge.execute()
        self._report_delta_table_operation_metrics(
            table_identifier,
            operation_type=DeltaTableOperationType.MERGE,
        )

    @table_log_decorator(operation="stream_merge")
    def write_stream(self):
        """Not implemented yet. See docs for more details."""
        raise NotImplementedError(
            "Streaming merge is not implemented yet. Please use the `write` method for batch merges."
        )
