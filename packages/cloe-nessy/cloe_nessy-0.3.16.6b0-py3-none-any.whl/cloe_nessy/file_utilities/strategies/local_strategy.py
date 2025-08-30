import os

from ..exceptions import FileUtilitiesError
from .base_strategy import FileRetrievalStrategy


class LocalDirectoryStrategy(FileRetrievalStrategy):
    """Strategy for retrieving files from a local directory.

    This strategy implements the file retrieval logic for local directories, including
    optional recursive search through subdirectories and filtering by file extension.
    """

    @staticmethod
    def get_file_paths(
        location: str,
        extension: str | None = None,
        search_subdirs: bool = True,
        **kwargs,  # noqa: ARG004
    ) -> list[str]:
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
            FileUtilitiesError: For any other unexpected errors.
        """
        if not location:
            raise ValueError("location is required")

        if not os.path.isdir(location):
            raise FileUtilitiesError(f"The provided path '{location}' is not a valid directory.")

        file_list = []

        try:
            for root, _, files in os.walk(location):
                if not search_subdirs and root != location:
                    continue

                for file_name in files:
                    if FileRetrievalStrategy._matches_extension(file_name, extension):
                        file_list.append(os.path.join(root, file_name))

        except Exception as err:
            raise FileUtilitiesError(f"An error occurred while retrieving file paths: {err}") from err

        return file_list
