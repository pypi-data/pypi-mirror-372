from collections.abc import Callable
from functools import reduce

from pyspark.sql import DataFrame

from ...file_utilities import get_file_paths
from ...integration.reader import ExcelDataFrameReader
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


class ReadExcelAction(PipelineAction):
    """Reads data from an Excel file or directory of Excel files and returns a DataFrame.

    The function reads Excel files using the
    [`ExcelDataFrameReader`][cloe_nessy.integration.reader.excel_reader] either
    from a single file or a directory path. It can read specific sheets, handle
    file extensions, and offers various options to customize how the data is
    read, such as specifying headers, index columns, and handling missing
    values. The resulting data is returned as a DataFrame, and metadata about
    the read files can be included in the context.

    Example:
        ```yaml
        Read Excel Table:
            action: READ_EXCEL
            options:
                file: excel_file_folder/excel_files_june/interesting_excel_file.xlsx
                usecols:
                    - key_column
                    - interesting_column
                options: <options for the ExcelDataFrameReader read method>
        ```

    !!! note "More Options"
        The `READ_EXCEL` action supports additional options that can be passed to the
        run method. For more information, refer to the method documentation.
    """

    name: str = "READ_EXCEL"

    def run(
        self,
        context: PipelineContext,
        *,
        file: str | None = None,
        path: str | None = None,
        extension: str = "xlsx",
        recursive: bool = False,
        sheet_name: str | int | list = 0,
        sheet_name_as_column: bool = False,
        header: int | list[int] = 0,
        index_col: int | list[int] | None = None,
        usecols: int | str | list | Callable | None = None,
        dtype: str | None = None,
        fillna: str | dict[str, list[str]] | dict[str, str] | None = None,
        true_values: list | None = None,
        false_values: list | None = None,
        nrows: int | None = None,
        na_values: list[str] | dict[str, list[str]] | None = None,
        keep_default_na: bool = True,
        parse_dates: bool | list | dict = False,
        date_parser: Callable | None = None,
        thousands: str | None = None,
        include_index: bool = False,
        options: dict | None = None,
        add_metadata_column: bool = True,
        load_as_strings: bool = False,
        **_,
    ) -> PipelineContext:
        """Reads data from an Excel file or directory of Excel files and returns a DataFrame.

        Args:
            context: The context in which the action is executed.
            file: The path to a single Excel file. Either `file` or `path` must be specified.
            path: The directory path containing multiple Excel files. Either `file` or `path` must be specified.
            extension: The file extension to look for when reading from a directory.
            recursive: Whether to include subdirectories when reading from a directory path.
            sheet_name: The sheet name(s) or index(es) to read from the Excel file.
            sheet_name_as_column: Whether to add a column with the sheet name to the DataFrame.
            header: Row number(s) to use as the column labels.
            index_col: Column(s) to use as the index of the DataFrame.
            usecols: Subset of columns to parse. Can be an integer, string, list,
                or function.
            dtype: Data type for the columns.
            fillna: Method or value to use to fill NaN values.
            true_values: Values to consider as True.
            false_values: Values to consider as False.
            nrows: Number of rows to parse.
            na_values: Additional strings to recognize as NaN/NA.
            keep_default_na: Whether to append default NaN values when custom `na_values` are specified.
            parse_dates: Options for parsing date columns.
            date_parser: Function to use for converting strings to datetime objects.
            thousands: Thousands separator to use when parsing numeric columns.
            include_index: Whether to include an index column in the output DataFrame.
            options: Additional options to pass to the DataFrame reader.
            add_metadata_column: Whether to add a metadata column with file information to the DataFrame.
            load_as_strings: Whether to load all columns as strings.

        Raises:
            ValueError: Raised if both `file` and `path` are specified, or if neither is provided.

        Returns:
            The updated context, with the read data as a DataFrame.
        """
        if not options:
            options = dict()

        if file is not None and path is not None:
            self._tabular_logger.error("message: Only one of file or path have to be specified.")
            raise ValueError("Only one of file or path have to be specified.")

        excel_reader = ExcelDataFrameReader()
        if file is not None:
            df = excel_reader.read(
                location=file,
                sheet_name=sheet_name,
                sheet_name_as_column=sheet_name_as_column,
                header=header,
                index_col=index_col,
                usecols=usecols,
                true_values=true_values,
                false_values=false_values,
                nrows=nrows,
                dtype=dtype,
                fillna=fillna,
                na_values=na_values,
                keep_default_na=keep_default_na,
                parse_dates=parse_dates,
                date_parser=date_parser,
                thousands=thousands,
                include_index=include_index,
                options=options,
                add_metadata_column=add_metadata_column,
                load_as_strings=load_as_strings,
            )
        elif path is not None:
            file_list = get_file_paths(path, extension, recursive)
            df_dict: dict = {}
            for path in file_list:
                df_dict[path] = excel_reader.read(
                    location=path,
                    sheet_name=sheet_name,
                    sheet_name_as_column=sheet_name_as_column,
                    header=header,
                    index_col=index_col,
                    usecols=usecols,
                    dtype=dtype,
                    fillna=fillna,
                    true_values=true_values,
                    false_values=false_values,
                    nrows=nrows,
                    na_values=na_values,
                    keep_default_na=keep_default_na,
                    parse_dates=parse_dates,
                    date_parser=date_parser,
                    thousands=thousands,
                    include_index=include_index,
                    options=options,
                    add_metadata_column=add_metadata_column,
                    load_as_strings=load_as_strings,
                )
            df = reduce(DataFrame.unionAll, list(df_dict.values()))

        else:
            self._tabular_logger.error("action_name: READ_EXCEL | message: Either file or path have to be specified.")
            raise ValueError("Either file or path have to be specified.")

        runtime_info = context.runtime_info

        if add_metadata_column:
            read_files_list = list(set([x.file_path for x in df.select("__metadata.file_path").collect()]))
            if runtime_info is None:
                runtime_info = {"read_files": read_files_list}
            else:
                try:
                    runtime_info["read_files"] = list(set(runtime_info["read_files"] + read_files_list))
                except KeyError:
                    runtime_info["read_files"] = read_files_list

        return context.from_existing(data=df)
