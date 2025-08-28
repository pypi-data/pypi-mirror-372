class APIClientError(Exception):
    """Base class for API client exceptions."""

    pass


class APIClientHTTPError(APIClientError):
    """Exception raised for HTTP errors."""

    pass


class APIClientConnectionError(APIClientError):
    """Exception raised for connection errors."""

    pass


class APIClientTimeoutError(APIClientError):
    """Exception raised for timeout errors."""

    pass
