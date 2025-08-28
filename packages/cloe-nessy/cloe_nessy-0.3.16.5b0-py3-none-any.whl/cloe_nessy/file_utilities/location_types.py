from enum import Enum


class LocationType(Enum):
    """Enum representing different types of locations.

    Attributes:
        LOCAL: Represents a local location.
        VOLUME: Represents a volume location.
        ABFS: Represents an Azure Blob File System (ABFS) location.
        ONELAKE: Represents a OneLake location.
    """

    LOCAL = "local"
    VOLUME = "volumes"
    ABFS = "abfs"
    S3 = "s3"
    ONELAKE = "onelake"

    @staticmethod
    def list() -> list[str]:
        """Returns a list of all location type values.

        This method provides a list of strings, each representing a location type.

        Returns:
            list of str: A list of all the values of the LocationType enum.
        """
        return list(map(lambda location: location.value, LocationType))
