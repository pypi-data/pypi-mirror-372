from typing import Any

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, DataFrameReader
from pyspark.sql.streaming import DataStreamReader
from pyspark.sql.types import StructType

from ...file_utilities import get_file_paths
from .reader import BaseReader


class FileReader(BaseReader):
    """Utility class for reading a file into a DataFrame.

    This class reads data from files and loads it into a Spark DataFrame.
    """

    def __init__(self):
        """Initializes the FileReader object."""
        super().__init__()

    def _get_reader(self) -> DataFrameReader:
        """Returns a DataFrameReader."""
        return self._spark.read

    def _get_stream_reader(self) -> DataStreamReader:
        """Returns a DataFrameReader."""
        return self._spark.readStream

    def read(
        self,
        location: str,
        *,
        spark_format: str | None = None,
        extension: str | None = None,
        schema: str | None = None,
        search_subdirs: bool = True,
        options: dict | None = None,
        add_metadata_column: bool = False,
        **kwargs: Any,
    ) -> DataFrame:
        """Reads files from a specified location and returns a DataFrame.

        Arguments:
            location: Location of files to read.
            spark_format: Format of files to read. If not provided, it will be inferred from the extension.
            extension: File extension (csv, json, parquet, txt). Used if spark_format is not provided.
            schema: Schema of the file. If None, schema will be inferred.
            search_subdirs: Whether to include files in subdirectories.
            options: Spark DataFrame reader options.
            add_metadata_column: Whether to include __metadata column in the DataFrame.
            **kwargs: Additional keyword arguments to maintain compatibility with the base class method.

        Raises:
            ValueError: If neither spark_format nor extension is provided.
            ValueError: If the provided extension is not supported.
            Exception: If there is an error while reading the files.

        Note:
            - The `spark_format` parameter is used to specify the format of the files to be read.
            - If `spark_format` is not provided, the method will try to infer it from the `extension`.
            - The `extension` parameter is used to specify the file extension (e.g., 'csv', 'json', etc.).
            - If both `spark_format` and `extension` are provided, `spark_format` will take precedence.
            - The method will raise an error if neither `spark_format` nor `extension` is provided.

        Returns:
            A DataFrame containing the data from the files.
        """
        if options is None:
            options = {}

        if not spark_format and not extension:
            raise ValueError("Either spark_format or extension must be provided.")
        self._console_logger.debug(f"Reading files from [ '{location}' ] ...")
        extension_to_datatype_dict = {
            "csv": "csv",
            "json": "json",
            "parquet": "parquet",
            "txt": "text",
            "xml": "xml",
        }

        if extension and not spark_format:
            if extension not in extension_to_datatype_dict:
                raise ValueError(f"Unsupported file extension: {extension}")
            spark_format = extension_to_datatype_dict[extension]
        self._console_logger.debug(f"Reading files with format: {spark_format}")
        if extension:
            file_paths = get_file_paths(location, extension, search_subdirs, onelake_relative_paths=True)
        else:
            file_paths = [location]
        self._console_logger.debug(f"Found {len(file_paths)} files to read")
        self._console_logger.debug(f"File paths: {file_paths}")
        assert spark_format is not None

        reader = self._get_reader().format(spark_format)
        if schema:
            reader.schema(schema)
        else:
            options["inferSchema"] = True

        self._console_logger.debug(f"Setting options: {options}")
        reader.options(**options)

        try:
            self._console_logger.debug("Loading files into DataFrame")
            df = reader.load([str(p) for p in file_paths])
            self._console_logger.debug("Successfully loaded files into DataFrame")
            if add_metadata_column:
                df = self._add_metadata_column(df)
        except Exception as e:
            self._console_logger.error(f"Failed to read files from [ '{location}' ]: {e}")
            raise
        else:
            self._console_logger.info(f"Successfully read files from [ '{location}' ]")
            return df

    def read_stream(
        self,
        location: str = "",
        schema: StructType | str | None = None,
        format: str = "delta",
        add_metadata_column: bool = False,
        options: dict[str, Any] | None = None,
        **_: Any,
    ) -> DataFrame:
        """Reads specified location as a stream and returns streaming DataFrame.

        Arguments:
            location : Location of files to read.
            format: Format of files to read.
            schema: Schema of the file.
            add_metadata_column: Whether to include __metadata column in the DataFrame.
            options: Spark DataFrame reader options.

        Raises:
            ValueError: If location is not provided.

        Returns:
            A Streaming DataFrame
        """
        if not location:
            raise ValueError("Location is required for streaming.")
        self._console_logger.debug(f"Reading files from [ '{location}' ] ...")
        try:
            if options is None:
                options = {}
            reader = self._get_stream_reader()
            reader.format(format)
            reader.option("rescuedDataColumn", "_rescued_data")
            if schema is None:
                options["inferSchema"] = True
            else:
                reader.schema(schema)
            reader.options(**options)
            df = reader.load(location)
            if add_metadata_column:
                df = self._add_metadata_column(df)
        except Exception as e:
            self._console_logger.error(f"Failed to read files from [ '{location}' ]: {e}")
            raise
        else:
            self._console_logger.info(f"Successfully read files from [ '{location}' ]")
            return df

    def _add_metadata_column(self, df: DataFrame) -> DataFrame:
        """Add all metadata columns to the DataFrame."""
        metadata_columns = df.select("_metadata.*").columns

        entries = [(F.lit(field), F.col(f"_metadata.{field}")) for field in metadata_columns]
        flat_list = [item for tup in entries for item in tup]

        df = df.withColumn("__metadata", F.create_map(flat_list))

        return df
