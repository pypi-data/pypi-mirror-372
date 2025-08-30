from pathlib import Path


def process_path(path: str | Path | None) -> Path | None:
    """Converts the input to a pathlib.Path object if it is a string, and returns the pathlib.Path object.

    Args:
        path: The file path, which can be a string or a pathlib.Path object.

    Raises:
        TypeError: If the input is neither a string nor a pathlib.Path object.
    """
    if not path:
        path = None
    elif isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise TypeError("path must be a string or a pathlib.Path object")
    return path
