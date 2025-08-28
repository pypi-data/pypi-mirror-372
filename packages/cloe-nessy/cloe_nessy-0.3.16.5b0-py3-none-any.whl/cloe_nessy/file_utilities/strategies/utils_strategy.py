from ...session import SessionManager
from ..exceptions import FileUtilitiesError
from .base_strategy import FileRetrievalStrategy


class UtilsStrategy(FileRetrievalStrategy):
    """Strategy for retrieving files using DButils (in Databricks) and mssparkutils (in Fabric).

    This strategy implements the file retrieval logic using utils, including
    recursive search through directories and filtering by file extension.
    """

    @staticmethod
    def get_file_paths(
        location: str,
        extension: str | None = None,
        search_subdirs: bool = True,
        **kwargs,  # noqa: ARG004
    ) -> list:
        """Recursively retrieves all files with a specified extension from a given directory and its subdirectories.

        Args:
            location: Top-level directory to read from, e.g., '/Volumes/my_volume/landing/example_landing/'.
            extension: File extension, e.g., 'csv', 'json'. Input an empty string to get files without any
                                    extension, input None to get all files.
            search_subdirs: If True, function will also search within all subdirectories.
            kwargs: Additional keyword arguments. Used in the OneLakeStrategy.

        Returns:
            List: List of files in the directory and its subdirectories with the given extension.

        Raises:
            ValueError: If the location is not provided.
            Exception: For any other unexpected errors.
        """
        if not location:
            raise ValueError("location is required")

        utils = SessionManager.get_utils()

        def _inner_loop(directory: str) -> list:
            """Inner loop that recursively traverses directories to find all files with a given extension.

            Args:
                directory: The directory to start searching in.

            Returns:
                List: List of all files in the directory and its subdirectories with the given extension.
            """
            try:
                dirs = utils.fs.ls(directory)
            except Exception as err:
                raise FileUtilitiesError(
                    f"An error occurred while listing files in directory '{directory}': {err}"
                ) from err

            file_list = [file for file in dirs if FileRetrievalStrategy._matches_extension(file.name, extension)]

            if search_subdirs:
                for p in dirs:
                    if p.isDir() and p.path != directory:
                        try:
                            sub_dir_files = _inner_loop(p.path)
                            file_list.extend(sub_dir_files)
                        except Exception as err:
                            raise FileUtilitiesError(
                                f"An error occurred while processing subdirectory '{p.path}': {err}"
                            ) from err

            return file_list

        try:
            file_list = _inner_loop(location)
        except Exception as err:
            raise FileUtilitiesError(f"An error occurred while retrieving file paths: {err}") from err

        file_list = [p.path for p in file_list if not p.isDir()]
        return file_list
