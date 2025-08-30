class ReaderError(Exception):
    """Base class for reader exceptions."""

    pass


class ReadOperationFailedError(ReaderError):
    """Exception raised for general Read Operation errors."""

    pass
