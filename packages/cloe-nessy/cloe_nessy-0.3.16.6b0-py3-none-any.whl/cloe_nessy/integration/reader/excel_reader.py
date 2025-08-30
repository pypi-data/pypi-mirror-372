from collections.abc import Callable
from typing import Any

import pandas as pd
import pyspark.sql.functions as F
from pyspark.sql import DataFrame

from .reader import BaseReader


class ExcelDataFrameReader(BaseReader):
    """Utility class for reading an Excel file into a DataFrame.

    This class uses the Pandas API on Spark to read Excel files to a DataFrame.
    More information can be found in the [official
    documentation](https://spark.apache.org/docs/latest/api/python/reference/pyspark.pandas/index.html).
    """

    def __init__(self):
        """Initializes the ExcelDataFrameReader object."""
        super().__init__()

    def read_stream(self) -> DataFrame:
        """Currently not implemented."""
        raise NotImplementedError("Currently not implemented.")

    def read(
        self,
        location: str,
        *,
        sheet_name: str | int | list = 0,
        header: int | list[int] = 0,
        index_col: int | list[int] | None = None,
        usecols: int | str | list | Callable | None = None,
        true_values: list | None = None,
        false_values: list | None = None,
        nrows: int | None = None,
        na_values: list[str] | dict[str, list[str]] | None = None,
        keep_default_na: bool = True,
        parse_dates: bool | list | dict = False,
        date_parser: Callable | None = None,
        thousands: str | None = None,
        options: dict | None = None,
        load_as_strings: bool = False,
        add_metadata_column: bool = False,
        **kwargs: Any,
    ) -> DataFrame:
        """Reads Excel file on specified location and returns DataFrame.

        Args:
            location: Location of files to read.
            sheet_name: Strings are used for sheet names.
                Integers are used in zero-indexed sheet positions. Lists of
                strings/integers are used to request multiple sheets. Specify None
                to get all sheets.
            header: Row to use for column labels. If a
                list of integers is passed those row positions will be combined. Use
                None if there is no header.
            index_col: Column to use as the row labels of the
                DataFrame. Pass None if there is no such column. If a list is
                passed, those columns will be combined.
            usecols: Return a subset of the columns. If
                None, then parse all columns. If str, then indicates comma separated
                list of Excel column letters and column ranges (e.g. “A:E” or
                “A,C,E:F”). Ranges are inclusive of both sides. nIf list of int,
                then indicates list of column numbers to be parsed. If list of
                string, then indicates list of column names to be parsed. If
                Callable, then evaluate each column name against it and parse the
                column if the Callable returns True.
            true_values: Values to consider as True.
            false_values: Values to consider as False.
            nrows: Number of rows to parse.
            na_values: Additional strings to recognize as
                NA/NaN. If dict passed, specific per-column NA values.
            keep_default_na: If na_values are specified and
                keep_default_na is False the default NaN values are overridden,
                otherwise they're appended to.
            parse_dates: The behavior is as follows:
                - bool. If True -> try parsing the index.
                - list of int or names. e.g. If [1, 2, 3] -> try parsing columns 1, 2, 3 each as a separate date column.
                - list of lists. e.g. If [[1, 3]] -> combine columns 1 and 3 and parse as a single date column.
                - dict, e.g. {{"foo" : [1, 3]}} -> parse columns 1, 3 as date and call result "foo"
                If a column or index contains an unparseable date, the entire column or index will be returned unaltered as an object data type.
            date_parser: Function to use for converting a sequence of
                string columns to an array of datetime instances. The default uses
                dateutil.parser.parser to do the conversion.
            thousands: Thousands separator for parsing string columns to
                numeric. Note that this parameter is only necessary for columns
                stored as TEXT in Excel, any numeric columns will automatically be
                parsed, regardless of display format.
            options: Optional keyword arguments passed to
                pyspark.pandas.read_excel and handed to TextFileReader.
            load_as_strings: If True, converts all columns to string type to avoid datatype conversion errors in Spark.
            add_metadata_column: If True, adds a metadata column containing the file location and sheet name.
            **kwargs: Additional keyword arguments to maintain compatibility with the base class method.
        """
        if options is None:
            options = {}
        if ".xls" not in location:
            raise ValueError(
                "The excel reader can only be used for files with extension .xls. Use FileReader or some other reader instead."
            )
        try:
            df = pd.read_excel(  # type: ignore
                location,
                sheet_name=sheet_name,
                header=header,
                index_col=index_col,
                usecols=usecols,
                true_values=true_values,
                false_values=false_values,
                nrows=nrows,
                na_values=na_values,
                keep_default_na=keep_default_na,
                parse_dates=parse_dates,
                date_parser=date_parser,
                thousands=thousands,
                dtype="string" if load_as_strings else None,
                **options,
            )
            if isinstance(df, dict):
                # in case pandas.read_excel returns a dict, union to single df
                df = pd.concat(list(df.values()), ignore_index=True)

        except FileNotFoundError:
            self._console_logger.error(f"No xls(x) file was found at the specified location [ '{location}' ].")
            raise
        except Exception as e:
            self._console_logger.error(f"read file [ '{location}' ] failed. Error: {e}")
        else:
            self._console_logger.info(f"Read file [ '{location}' ] succeeded.")

        spark_df = self._spark.createDataFrame(df)
        if add_metadata_column:
            spark_df = self._add_metadata_column(df=spark_df, location=location, sheet_name=sheet_name)
        return spark_df

    def _add_metadata_column(self, df: DataFrame, location: str, sheet_name: str | int | list):
        """Adds a metadata column to a DataFrame.

        This method appends a column named `__metadata` to the given DataFrame, containing a map
        of metadata related to the Excel file read operation. The metadata includes the current
        timestamp, the location of the Excel file, and the sheet name(s) from which the data was read.

        Args:
            df: The DataFrame to which the metadata column will be added.
            location: The file path of the Excel file.
            sheet_name: The sheet name or sheet index used when reading the Excel file.

        Returns:
            DataFrame: The original DataFrame with an added `__metadata` column containing the Excel file metadata.
        """
        # Convert sheet_name to string if it is not already a string
        if isinstance(sheet_name, list):
            sheet_name = ", ".join(map(str, sheet_name))
        else:
            sheet_name = str(sheet_name)

        df = df.withColumn(
            "__metadata",
            F.create_map(
                F.lit("timestamp"),
                F.current_timestamp(),
                F.lit("file_location"),
                F.lit(location),
                F.lit("sheet_name"),
                F.lit(sheet_name),
            ),
        )
        return df
