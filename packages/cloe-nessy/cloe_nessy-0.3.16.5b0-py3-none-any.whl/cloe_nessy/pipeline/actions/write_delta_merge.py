from typing import Any

from ...integration.writer import DeltaMergeWriter
from ...models.adapter import UnityCatalogAdapter
from ...pipeline import PipelineAction, PipelineContext


class WriteDeltaMergeAction(PipelineAction):
    """This class implements a Merge action for an ETL pipeline.

    The MergeIntoDeltaAction merges a Dataframe to Delta Table.

    Returns:
        None.
    """

    name: str = "WRITE_DELTA_MERGE"

    def run(
        self,
        context: PipelineContext,
        *,
        table_identifier: str | None = None,
        key_columns: list[str] | None = None,
        cols_to_update: list[str] | None = None,
        cols_to_insert: list[str] | None = None,
        cols_to_exclude: list[str] | None = None,
        when_matched_update: bool = True,
        when_matched_deleted: bool = False,
        when_not_matched_insert: bool = True,
        use_partition_pruning: bool = True,
        ignore_empty_df: bool = False,
        create_if_not_exists: bool = True,
        refresh_table: bool = True,
        **_: Any,
    ) -> PipelineContext:
        """Merge the dataframe into the delta table.

        Args:
            context: Context in which this Action is executed.
            table_identifier: The identifier of the table. If passed, the
                UC Adapter will be used to create a table object. Otherwise the Table
                object will be created from the table metadata in the context.
            key_columns: List of column names that form the
                key for the merge operation.
            when_matched_update: Flag to specify whether to
                perform an update operation whenmatching records are found in
                the target Delta table.
            when_matched_deleted: Flag to specify whether to
                perform a delete operation when matching records are found in
                the target Delta table.
            when_not_matched_insert: Flag to specify whether to perform an
                insert operation when matching records are not found in the target
                Delta table.
            cols_to_update: List of column names to be
                updated in the target Delta table.
            cols_to_insert: List of column names to be
                inserted into the target Delta table.
            cols_to_exclude: List of column names to be
                excluded from the merge operation.
            use_partition_pruning: Flag to specify whether to use partition
                pruning to optimize the performance of the merge operation.
            ignore_empty_df: A flag indicating whether to ignore an empty source dataframe.
            create_if_not_exists: Create the table if it not exists.
            refresh_table: Refresh the table after the transaction.

        Raises:
            ValueError: If the table does not exist.
            ValueError: If the data is not set in the pipeline context.
            ValueError: If the table metadata is empty.

        Returns:
            Pipeline Context
        """
        delta_merge_writer = DeltaMergeWriter()

        if context.data is None:
            raise ValueError("Data is required for the merge operation.")
        if context.table_metadata is None and table_identifier is None:
            raise ValueError("Table metadata or a table identifier are required for the merge operation.")

        if table_identifier is not None:
            context.table_metadata = UnityCatalogAdapter().get_table_by_name(table_identifier)
        else:
            if context.table_metadata is None:
                raise ValueError("Table metadata is required.")

        if context.table_metadata is None:
            raise ValueError("Table metadata is required.")

        if create_if_not_exists:
            delta_merge_writer.table_manager.create_table(table=context.table_metadata, ignore_if_exists=True)

        if not delta_merge_writer.table_manager.table_exists(context.table_metadata):
            raise ValueError(f"Table {context.table_metadata.name} does not exist.")

        assert key_columns is not None, "Key columns must be provided."

        delta_merge_writer.write(
            table_identifier=context.table_metadata.identifier,
            table=context.table_metadata,
            storage_path=str(context.table_metadata.storage_path),
            data_frame=context.data,
            key_columns=key_columns,
            cols_to_update=cols_to_update,
            cols_to_insert=cols_to_insert,
            cols_to_exclude=cols_to_exclude,
            when_matched_update=when_matched_update,
            when_matched_deleted=when_matched_deleted,
            when_not_matched_insert=when_not_matched_insert,
            use_partition_pruning=use_partition_pruning,
            partition_by=context.table_metadata.partition_by,
            ignore_empty_df=ignore_empty_df,
        )

        if refresh_table:
            delta_merge_writer.table_manager.refresh_table(table_identifier=context.table_metadata.identifier)

        return context.from_existing()
