import logging

from ..logging import LoggerMixin
from ..models import Volume
from ..session import SessionManager


class VolumeManager(LoggerMixin):
    """VolumeManager class for managing volumes."""

    def __init__(self, console_logger: logging.Logger | None = None):
        self._spark = SessionManager.get_spark_session()
        self._console_logger = console_logger or self.get_console_logger()

    def create_volume(self, volume: Volume):
        """Creates a Volume in the catalog.

        Args:
            volume: A Volume object representing the UC object.
        """
        self._console_logger.info(f"Creating volume: {volume.identifier}")
        self._spark.sql(f"USE CATALOG {volume.catalog};")
        self._spark.sql(f"USE SCHEMA {volume.schema_name};")
        for statement in volume.get_create_statement().split(";"):
            if statement and statement != "\n":
                self._spark.sql(statement)

    def drop_volume(self, volume: Volume, if_exists: bool = True):
        """Delete the volume.

        Args:
            volume: The volume to be deleted.
            if_exists: If False, an error will be raised if the volume does not exist.
        """
        self._console_logger.info(f"Deleting volume: [' {volume.identifier}' ]")
        self._spark.sql(f"DROP VOLUME {'IF EXISTS' if if_exists else ''} {volume.escaped_identifier};")
        self._console_logger.info(f"Volume [' {volume.identifier}' ] has been deleted.")

    def volume_exists(self, volume: Volume | None = None, volume_identifier: str | None = None) -> bool:
        """Check if the volume exists.

        Args:
            volume: The volume to check.
            volume_identifier: The identifier of the volume to check.

        Raises:
            ValueError: If both volume and volume_identifier are provided.

        Returns:
            True if the volume exists, False otherwise.
        """
        if volume and volume_identifier:
            raise ValueError("Only one of volume or volume_identifier should be provided.")
        if volume:
            volume_identifier = volume.identifier

        assert volume_identifier is not None

        if volume_identifier.count(".") != 2:
            raise ValueError("The identifier must be in the format 'catalog.schema.volume_name'.")
        catalog, volume_schema, table_name = volume_identifier.split(".")
        query_result = self._spark.sql(
            f"""
                SELECT 1 FROM {catalog}.information_schema.volumes
                WHERE volume_name = '{table_name}'
                AND volume_schema = '{volume_schema}'
                LIMIT 1""",
        )
        result = query_result.count() > 0
        return result is True
