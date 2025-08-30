from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from pyspark.sql import DataFrame

from ...logging import LoggerMixin


class BaseWriter(ABC, LoggerMixin):
    """BaseWriter class to write data."""

    def __init__(self):
        self._console_logger = self.get_console_logger()

    @abstractmethod
    def write_stream(self, **kwargs: Any):
        """Writes a DataFrame stream."""
        pass

    @abstractmethod
    def write(
        self,
        data_frame: DataFrame,
        **kwargs: Any,
    ):
        """Writes a DataFrame."""
        pass

    def log_operation(self, operation: str, identifier: str | Path, status: str, error: str = ""):
        """Logs the metrics for one operation on the given identifier.

        Args:
            operation: Describes the type of operation, e.g. 'read_api'.
            identifier: An identifier for the object that's being interacted with.
            status: The status of the operation. Must be one of "start", "failed", "succeeded".
            error: The error message, if any. Defaults to ''.
        """
        self._console_logger.info(
            "operation:%s | identifier:%s | status:%s | error:%s",
            operation,
            identifier,
            status,
            error,
        )

    def _get_checkpoint_location(self, location: str, checkpoint_location: str | None) -> str:
        """Generates the checkpoint location if not provided."""
        if checkpoint_location is None:
            location_path = Path(location)
            checkpoint_location = str(location_path.parent / f"_checkpoint_{location_path.name}").replace(
                "abfss:/", "abfss://"
            )
        return checkpoint_location
