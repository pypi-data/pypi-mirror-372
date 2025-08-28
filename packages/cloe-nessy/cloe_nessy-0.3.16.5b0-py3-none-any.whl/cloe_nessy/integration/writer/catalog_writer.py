from pyspark.sql import DataFrame


class CatalogWriter:
    """A writer for Catalog tables."""

    @staticmethod
    def write(
        df: DataFrame | None,
        table_identifier: str | None,
        partition_by: str | list[str] | None = None,
        options: dict[str, str] | None = None,
        mode: str = "append",
    ) -> None:
        """Write a table to the unity catalog.

        Args:
            df: The DataFrame to write.
            table_identifier: The table identifier in the unity catalog in the
                              format 'catalog.schema.table'.
            mode: The write mode. One of append, overwrite, error, errorifexists, ignore.
            partition_by: Names of the partitioning columns.
            options: PySpark options for the DataFrame.saveAsTable operation (e.g. mergeSchema:true).

        Notes:
            append: Append contents of this DataFrame to existing data.
            overwrite: Overwrite existing data.
            error or errorifexists: Throw an exception if data already exists.
            ignore: Silently ignore this operation if data already exists.

        Raises:
            ValueError: If the mode is not one of append, overwrite, error, errorifexists, ignore.
            ValueError: If the table_identifier is not a string or not in the format 'catalog.schema.table'.
            ValueError: If the DataFrame is None.
        """
        if mode not in ("append", "overwrite", "error", "errorifexists", "ignore"):
            raise ValueError("mode must be one of append, overwrite, error, errorifexists, ignore")
        if not table_identifier:
            raise ValueError("table_identifier is required")
        elif not isinstance(table_identifier, str):
            raise ValueError("table_identifier must be a string")
        elif len(table_identifier.split(".")) != 3:
            raise ValueError("table_identifier must be in the format 'catalog.schema.table'")
        if not df:
            raise ValueError("df is required, but was None.")
        if options is None:
            options = {}
        df.write.saveAsTable(table_identifier, mode=mode, partitionBy=partition_by, **options)

    @staticmethod
    def write_stream(
        df: DataFrame | None,
        table_identifier: str | None,
        checkpoint_location: str | None = None,
        trigger_dict: dict | None = None,
        options: dict[str, str] | None = None,
        mode: str = "append",
        await_termination: bool = False,
    ) -> None:
        """Write a streaming DataFrame to a Unity Catalog table.

        Args:
            df: The streaming DataFrame to write.
            table_identifier: The table identifier in the Unity Catalog in the
                              format 'catalog.schema.table'.
            checkpoint_location: Location for checkpointing. Required for stream recovery.
            trigger_dict: A dictionary specifying the trigger configuration for the streaming query.
                Supported keys include:
                - "processingTime": Specifies a time interval (e.g., "10 seconds") for micro-batch processing.
                - "once": Processes all available data once and then stops.
                - "continuous": Specifies a time interval (e.g., "1 second") for continuous processing.
                - "availableNow": Processes all available data immediately and then stops.
                If nothing is provided, the default is {"availableNow": True}.
            options: PySpark options for the DataFrame streaming write operation.
            mode: The write mode. For streaming, typically "append".
            await_termination: If True, the function will wait for the streaming
                query to finish before returning.

        Raises:
            ValueError: If the mode is not supported for streaming operations.
            ValueError: If the table_identifier is not a string or not in the format 'catalog.schema.table'.
            ValueError: If the DataFrame is None.
            ValueError: If checkpoint_location is not provided.
        """
        if mode not in ("append", "complete", "update"):
            raise ValueError("mode must be one of append, complete, update for streaming operations")
        if not table_identifier:
            raise ValueError("table_identifier is required")
        elif not isinstance(table_identifier, str):
            raise ValueError("table_identifier must be a string")
        elif len(table_identifier.split(".")) != 3:
            raise ValueError("table_identifier must be in the format 'catalog.schema.table'")
        if not df:
            raise ValueError("df is required, but was None.")
        if not checkpoint_location:
            raise ValueError("checkpoint_location is required for streaming operations")

        if options is None:
            options = {}
        if trigger_dict is None:
            trigger_dict = {"availableNow": True}

        stream_writer = df.writeStream.format("delta").outputMode(mode)
        stream_writer.options(**options).option("checkpointLocation", checkpoint_location)
        stream_writer.trigger(**trigger_dict)

        query = stream_writer.toTable(table_identifier)

        if await_termination:
            query.awaitTermination()
