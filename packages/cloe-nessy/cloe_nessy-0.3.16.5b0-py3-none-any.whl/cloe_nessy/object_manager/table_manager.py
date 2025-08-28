import functools
import logging
from dataclasses import dataclass, field

from delta import DeltaTable  # type: ignore

from ..logging import LoggerMixin
from ..models import Table
from ..session import SessionManager


@dataclass
class TableManagerLogs:
    """Dataclass defining the table manager logs table."""

    logger_name = "Tabular:TableManager"
    log_type: str = "nessy_simple_logs"
    uc_table_name: str = "nessy_simple_logs"
    uc_table_columns: dict[str, str] = field(
        default_factory=lambda: {
            "message": "STRING",
        }
    )


def table_log_decorator(operation: str):
    """Creates a decorator that logs the start, failure (if any), and completion of a table operation.

    The created decorator wraps a function that performs an operation on a table. The decorator logs
    the start of the operation, calls the original function, logs if there was an exception, and logs
    the completion of the operation. Functions that are wrapped must support the self._table_logger
    attribute.

    Args:
        operation: The name of the operation to be logged. This will be included in the log messages.

    Returns:
        inner_decorator: A decorator that can be used to wrap a function that performs an operation on a table.

    Example:
        ```python
        @table_log_decorator(operation='delete_physical_data_for_table')
        def _delete_physical_data(self, table_identifier: str):
            self._dbutils.fs.rm(table_location, recurse=True)
        ```
    """

    def inner_decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            table_identifier = kwargs.get("table_identifier") or kwargs.get("table") or args[0]
            if isinstance(table_identifier, Table):
                table_identifier = table_identifier.identifier
            self._tabular_logger.info(
                "operation:%s | identifier:%s | status:start | error:''",
                operation,
                table_identifier,
            )
            try:
                func(self, *args, **kwargs)
            except Exception as e:
                self._tabular_logger.error(
                    "operation:%s | identifier:%s | status:failed | error:%s",
                    operation,
                    table_identifier,
                    e,
                )
                raise e
            else:
                self._tabular_logger.info(
                    "operation:%s | identifier:%s | status:completed | error:''",
                    operation,
                    table_identifier,
                )

        return wrapper

    return inner_decorator


class TableManager(LoggerMixin):
    """TableManager class for managing tables."""

    def __init__(self, tabular_logger: logging.Logger | None = None):
        self._spark = SessionManager.get_spark_session()
        self._console_logger = self.get_console_logger()
        self._console_logger.debug("TableManager initialized...")
        self._tabular_logger = tabular_logger or self.get_tabular_logger(**TableManagerLogs().__dict__)
        self._tabular_logger.debug("message:TableManager initialized.")

    @table_log_decorator(operation="create")
    def create_table(
        self,
        table: Table,
        ignore_if_exists: bool = False,
        replace: bool = False,
    ) -> None:
        """Creates a Table in the catalog.

        Args:
            table: A Table object representing the Delta table.
            ignore_if_exists: If set to True, the function will return early
                without doing anything if the table already exists.
            replace: If set to True, the function will replace the table if it
                already exists.
        """
        if ignore_if_exists and self.table_exists(table):
            return
        self._console_logger.info(f"Creating table: {table.identifier}")
        self._spark.sql(f"USE CATALOG {table.catalog};")
        self._spark.sql(f"USE SCHEMA {table.schema};")
        for statement in table.get_create_statement(replace=replace).split(";"):
            if statement and statement != "\n":
                self._spark.sql(statement)

    def drop_table(
        self,
        table: Table | None = None,
        storage_location: str | None = None,
        table_identifier: str | None = None,
        delete_physical_data: bool = False,
    ):
        """Deletes a Table. For security reasons you are forced to pass the table_name.

        If delete_physical_data is True the actual physical data on the ADLS will be deleted.
        Use with caution!

        Args:
            table: The Table object representing the Delta table.
            storage_location: The location of the Delta table on the ADLS.
            table_identifier: The table identifier in the catalog. Must be in the format 'catalog.schema.table'.
            delete_physical_data: If set to True, deletes not only the metadata
                                  within the Catalog but also the physical data.

        Raises:
            ValueError: If neither table nor table_identifier is provided, or if both are provided.
            ValueError: If the table storage path is not provided by the table object.
        """
        self._console_logger.info(f"Deleting table [ '{table_identifier}' ] ...")
        if table is not None and (table_identifier is not None or storage_location is not None):
            raise ValueError("Either table or table_identifier and storage_location must be provided, but not both.")
        if table is not None:
            table_identifier = table.identifier
            storage_location = str(table.storage_path)
        if delete_physical_data:
            self._delete_physical_data(location=storage_location)
        self.drop_table_from_catalog(table_identifier=table_identifier)

    def drop_table_from_catalog(self, table_identifier: str | None = None, table: Table | None = None) -> None:
        """Removes a table from the catalog. Physical data is retained.

        Args:
            table_identifier: The table identifier in the catalog. Must be in the format 'catalog.schema.table'.
            table: The Table object representing the Delta table.

        Raises:
            ValueError: If neither table nor table_identifier is provided, or if both are provided.
        """
        if (table is None and table_identifier is None) or (table is not None and table_identifier is not None):
            raise ValueError("Either table or table_identifier must be provided, but not both.")
        if table is not None:
            table_identifier = table.identifier
        self._console_logger.info(f"... deleting table [ '{table_identifier}' ] from Catalog.")
        self._spark.sql(f"DROP TABLE IF EXISTS {table_identifier};")

    def _delete_physical_data(self, table: Table | None = None, location: str | None = None):
        """Removes the physical data on the ADLS for the location of this table.

        Args:
            table: The Table object representing the Delta table to be deleted.
            location: The location of the Delta table to be deleted.

        Raises:
            ValueError: If neither table nor location is provided, or if both are provided.
            ValueError: If the table storage path is not provided by the table object.
        """
        if (table is None and location is None) or (table is not None and location is not None):
            raise ValueError("Either table or location must be provided, but not both.")
        if table is not None:
            if table.storage_path is None:
                raise ValueError("Table storage path must be provided.")
            location = str(table.storage_path)
        SessionManager.get_utils().fs.rm(location, recurse=True)
        self._console_logger.info("... deleting physical data.")

    def get_delta_table(self, table: Table | None = None, location: str | None = None, spark=None) -> DeltaTable:
        """Get the DeltaTable object from the Table objects location or a location string.

        For managed tables, uses the table identifier to access the DeltaTable.
        For external tables or when a location is provided, uses the storage path.

        Args:
            table: A Table object representing the Delta table.
            location: A string representing the table location.
            spark: An optional Spark session. If not provided, the current Spark session will be used.

        Returns:
            The DeltaTable object corresponding to the given Table object or location string.

        Raises:
            ValueError: If neither table nor location is provided.
        """
        if table is None and location is None:
            self._console_logger.error("Invalid parameters: both table and location are None")
            raise ValueError("Either table or location must be provided.")

        spark_session = spark or self._spark

        if table is not None and location is not None:
            self._console_logger.info(
                f"Both table ({table.identifier}) and location ({location}) provided. Using table object as priority."
            )

        if table is not None:
            if table.is_external is False:
                self._console_logger.info(f"Getting DeltaTable object for managed table: {table.identifier}")
                return DeltaTable.forName(spark_session, table.identifier)

            table_location = str(table.storage_path)
            self._console_logger.info(f"Getting DeltaTable object for external table location: {table_location}")
            return DeltaTable.forPath(spark_session, table_location)

        self._console_logger.info(f"No table object provided, using location: {location}")
        if location is None:
            self._console_logger.error("Location is None - this should not happen!")
            raise ValueError("Location cannot be None when no table object is provided")
        self._console_logger.info(f"Getting DeltaTable object for location: {location}")
        return DeltaTable.forPath(spark_session, str(location))

    def table_exists(self, table: Table | None = None, table_identifier: str | None = None) -> bool:
        """Checks if a table exists in the catalog.

        Args:
            table: A Table object representing the Delta table.
            table_identifier: A string representing the table identifier in the format 'catalog.schema.table'.

        Returns:
            True if the table exists, else False.

        Raises:
            ValueError: If neither table nor table_identifier is provided, or if both are provided.
            ValueError: If the table_identifier is not in the format 'catalog.schema.table'.
        """
        if (table is None and table_identifier is None) or (table is not None and table_identifier is not None):
            raise ValueError("Either table or table_identifier must be provided, but not both.")

        if table is not None:
            catalog = table.catalog
            schema = table.schema
            table_name = table.name
        else:
            assert table_identifier is not None, "table_identifier must be provided."
            catalog, schema, table_name = table_identifier.split(".")
            if not all([catalog, schema, table_name]):
                raise ValueError("Invalid table identifier format. Expected 'catalog.schema.table'.")

        query_result = self._spark.sql(
            # Using both upper and lower case to ensure compatibility with case changes in Databricks
            f"""
                SELECT 1 FROM {catalog}.information_schema.tables
                WHERE table_name in ('{table_name}', '{table_name.lower()}')
                AND table_schema = '{schema}'
                LIMIT 1""",
        )
        result = query_result.count() > 0
        self._console_logger.info(f"Table [ '{catalog}.{schema}.{table_name}' ] exists: {result}")
        return result is True

    @table_log_decorator(operation="refresh")
    def refresh_table(self, table: Table | None = None, table_identifier: str | None = None):
        """Refreshes the metadata of a Delta table.

        Args:
            table: A Table object representing the Delta table.
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.

        Raises:
            ValueError: If neither table nor table_identifier is provided, or if both are provided.
        """
        if (table is None and table_identifier is None) or (table is not None and table_identifier is not None):
            raise ValueError("Either table or table_identifier must be provided, but not both.")

        if table is not None:
            table_identifier = f"{table.catalog}.{table.schema}.{table.name}"

        self._console_logger.info(f"Refreshing table: {table_identifier}")
        self._spark.sql(f"REFRESH TABLE {table_identifier};")

    @table_log_decorator(operation="truncate")
    def truncate_table(
        self,
        table: Table | None = None,
        table_identifier: str | None = None,
    ):
        """Truncates a table.

        Args:
            table: A Table object representing the Delta table.
            table_identifier: The identifier of the Delta table in the format 'catalog.schema.table'.

        Raises:
            ValueError: If neither table nor table_identifier is provided, or if both are provided.
        """
        if (table is None and table_identifier is None) or (table is not None and table_identifier is not None):
            raise ValueError("Either table or table_identifier must be provided, but not both.")

        if table is not None:
            table_identifier = table.escaped_identifier

        self._console_logger.info(f"Truncating table: {table_identifier}")
        self._spark.sql(f"TRUNCATE TABLE {table_identifier};")
