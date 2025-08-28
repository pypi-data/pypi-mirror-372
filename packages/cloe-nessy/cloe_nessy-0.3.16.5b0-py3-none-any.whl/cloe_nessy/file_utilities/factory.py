from .location_types import LocationType
from .strategies.local_strategy import LocalDirectoryStrategy
from .strategies.onelake_strategy import OneLakeStrategy
from .strategies.utils_strategy import UtilsStrategy


class FileRetrievalFactory:
    """Factory for creating file retrieval strategies based on location type.

    This factory class is responsible for returning the appropriate strategy
    implementation for retrieving files based on the specified location type.
    """

    _strategy_map = {
        LocationType.LOCAL: LocalDirectoryStrategy,
        LocationType.VOLUME: LocalDirectoryStrategy,
        LocationType.ABFS: UtilsStrategy,
        LocationType.S3: UtilsStrategy,
        LocationType.ONELAKE: OneLakeStrategy,
    }

    @staticmethod
    def get_strategy(location_type: LocationType) -> LocalDirectoryStrategy | OneLakeStrategy | UtilsStrategy:
        """Returns the appropriate file retrieval strategy for the given location type.

        Depending on the provided location type, this method returns an instance
        of either `LocalDirectoryStrategy` or `UtilsStrategy`. If the
        location type is not recognized, a `ValueError` is raised.

        Args:
            location_type: The location type for which to get the retrieval strategy.

        Returns:
            FileRetrievalStrategy: An instance of the appropriate file retrieval strategy.

        Raises:
            ValueError: If the provided location type is unknown or unsupported.
        """
        strategy_class = FileRetrievalFactory._strategy_map.get(location_type)
        if not strategy_class:
            raise ValueError(f"Unknown location type: {location_type}")
        return strategy_class()  # type: ignore
