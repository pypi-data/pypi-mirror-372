import os

from ..logging.logger_mixin import LoggerMixin
from .factory import FileRetrievalFactory
from .location_types import LocationType


def get_file_paths(
    location: str,
    file_name_pattern: str | None = None,
    search_subdirs: bool = True,
    **kwargs,
) -> list[str]:
    """Retrieves file paths from a specified location based on the provided criteria.

    This function determines the type of location (e.g., local directory, blob storage),
    retrieves the appropriate file retrieval strategy using a factory, and then uses
    that strategy to get a list of file paths that match the given file_name_pattern and search options.

    Args:
        location: The location to search for files. This could be a path to a local directory or a URI for blob storage.
        file_name_pattern: The file file_name_pattern to filter by as string. None retrieves all files regardless of file_name_pattern.
        search_subdirs: Whether to include files from subdirectories in the search.
        kwargs: Additional keyword arguments.

    Returns:
        A list of file paths that match the specified criteria. The paths are returned as strings.

    Raises:
        ValueError: If the `location` argument is empty or None.
        FileUtilitiesError: If an error occurs while determining the location type, retrieving the strategy, or getting file paths.
    """
    logger = LoggerMixin().get_console_logger()
    if not location:
        raise ValueError("location is required")

    logger.debug("location", location)
    logger.debug("Getting location type")
    location_type = get_location_type(location=location)
    logger.debug("location_type", location_type)
    strategy = FileRetrievalFactory.get_strategy(location_type)
    logger.debug("strategy", strategy)
    logger.info(
        f"Retrieving file paths from location [  '{location}'  ] with strategy [  '{strategy.__class__.__name__}'  ]"
    )
    paths = strategy.get_file_paths(location, file_name_pattern, search_subdirs, **kwargs)
    logger.debug("paths:", paths)
    return paths


def get_location_type(location: str) -> LocationType:
    """Get the location type based on the given location string.

    Args:
        location: The location string to check.

    Returns:
        LocationType: The determined location type.
    """
    location_mapping = {
        "abfss://": LocationType.ABFS,
        "/Volumes/": LocationType.VOLUME,
        "s3://": LocationType.S3,
        "/lakehouse/default/": LocationType.ONELAKE,
    }

    for prefix, loc_type in location_mapping.items():
        if location.startswith(prefix):
            return loc_type

    if os.path.isdir(location):
        return LocationType.LOCAL

    raise NotImplementedError(
        f"Could not determine Location type of location [  '{location}'  ]."
        f"Ensure that the provided path is valid."
        f"Available Location type implementations are: [  {', '.join(LocationType.list())}  ].",
    )
