from pyspark.sql import DataFrame


class CatalogWriter:
    """A writer for Catalog tables."""

    @staticmethod
    def write_table(
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
