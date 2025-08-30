from abc import ABC, abstractmethod
from typing import Any

from pyspark.sql import DataFrame, SparkSession

from ...logging.logger_mixin import LoggerMixin
from ...session import SessionManager


class BaseReader(ABC, LoggerMixin):
    """Abstract base class for reading data into a Spark DataFrame.

    This class provides a common interface for different types of data readers.

    Attributes:
        _spark: The Spark session used for creating DataFrames.
    """

    def __init__(self) -> None:
        self._spark: SparkSession = SessionManager.get_spark_session()
        self._console_logger = self.get_console_logger()

    @abstractmethod
    def read(self, *args: Any, **kwargs: Any) -> DataFrame:
        """Abstract method to return a batch data frame.

        Args:
            *args: Arbitrary non-keyword arguments for reading data.
            **kwargs: Arbitrary keyword arguments for reading data.

        Returns:
            DataFrame: The Spark DataFrame containing the read data.
        """
        pass
