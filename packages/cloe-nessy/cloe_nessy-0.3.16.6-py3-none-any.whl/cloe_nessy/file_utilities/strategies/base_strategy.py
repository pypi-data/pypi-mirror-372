from abc import ABC, abstractmethod


class FileRetrievalStrategy(ABC):
    """Abstract base class for file retrieval strategies.

    This class defines the interface for strategies that retrieve file paths
    based on certain criteria. Concrete implementations of this class should
    provide the logic for retrieving file paths.
    """

    @staticmethod
    @abstractmethod
    def get_file_paths(
        location: str,
        extension: str | None = None,
        search_subdirs: bool = True,
        **kwargs,
    ) -> list[str]:
        """Retrieves a list of file paths based on the specified criteria.

        Args:
            location: The location to search for files.
            extension: The file extension to filter by. If None, no extension filtering is applied.
                If an empty string, it matches files with no extension.
            search_subdirs: Whether to search in subdirectories.
            kwargs: Additional keyword arguments that may be used by concrete implementations

        Returns:
            list[str]: A list of file paths that match the specified criteria.
        """
        raise NotImplementedError("Concrete implementations must provide the logic for retrieving file paths.")

    @staticmethod
    def _matches_extension(file_name: str, extension: str | None) -> bool:
        """Determines if a file name ends with the specified extension.

        This method checks whether the provided file name matches the given file extension. The comparison is case-insensitive.

        If the `extension` is an empty string, it checks if the file name either does not contain a dot or ends with a dot,
        which indicates a file with no extension. If the `extension` is `None`, it matches any file name regardless of extension.

        If the `extension` contains a dot (e.g., ".txt"), it is compared directly against the end of the file name. Otherwise,
        a dot is prefixed to the `extension` to create the expected file extension format (e.g., "txt" becomes ".txt").

        Args:
            file_name: The name of the file to check. This is converted to lowercase for case-insensitive comparison.
            extension: The extension to match against. Can be a string with or without a leading dot.

        Returns:
            bool: True if the file name ends with the specified extension, False otherwise.
        """
        file_name_lower = file_name.lower()
        matches = False

        if extension == "":
            matches = "." not in file_name_lower or file_name.endswith(".")
        elif extension is None:
            matches = True
        elif "." in extension:
            matches = file_name_lower.endswith(extension.lower())
        else:
            matches = file_name_lower.endswith(f".{extension.lower()}")

        return matches
