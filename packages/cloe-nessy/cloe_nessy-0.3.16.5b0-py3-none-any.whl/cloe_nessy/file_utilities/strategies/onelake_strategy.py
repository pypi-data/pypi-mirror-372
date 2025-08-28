from .base_strategy import FileRetrievalStrategy
from .local_strategy import LocalDirectoryStrategy


class OneLakeStrategy(FileRetrievalStrategy):
    """Strategy for retrieving files from the OneLake."""

    @staticmethod
    def get_file_paths(
        location: str,
        extension: str | None = None,
        search_subdirs: bool = True,
        **kwargs,
    ) -> list:
        """Recursively retrieves all files with a specified extension from a given directory and its subdirectories.

        Args:
            location: Top-level directory to read from, e.g., '/Volumes/my_volume/landing/example_landing/'.
            extension: File extension, e.g., 'csv', 'json'. Input an empty string to get files without any
                                    extension, input None to get all files.
            search_subdirs: If True, function will also search within all subdirectories.
            kwargs: Additional keyword arguments.

        Returns:
            List: List of files in the directory and its subdirectories with the given extension.

        Raises:
            ValueError: If the location is not provided.
            Exception: For any other unexpected errors.
        """
        if not location:
            raise ValueError("location is required")

        file_paths = LocalDirectoryStrategy.get_file_paths(location, extension, search_subdirs)

        if kwargs.get("onelake_relative_paths", False) is True:
            file_paths = OneLakeStrategy._relative_file_paths(file_paths)

        return file_paths

    @staticmethod
    def _relative_file_paths(file_paths: list[str]) -> list[str]:
        """OneLake expects relative paths when working with spark.

        Note:
            Long Paths (in the format '/lakehouse/default/Files/my_file') are
            used, e.g., when working with Pandas or os.
        """
        relative_file_paths = [p.replace("/lakehouse/default/", "") for p in file_paths]
        return relative_file_paths
