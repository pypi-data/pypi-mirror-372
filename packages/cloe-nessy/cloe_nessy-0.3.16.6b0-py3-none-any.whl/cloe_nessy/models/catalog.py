from dataclasses import dataclass


@dataclass
class Catalog:
    """A class representing a Unity Catalog - Catalog."""

    name: str
    owner: str = ""
    comment: str = ""
