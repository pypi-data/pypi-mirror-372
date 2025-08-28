from http import HTTPStatus
from time import sleep
from typing import Any
from urllib.parse import urljoin

import requests
from requests.auth import AuthBase

from .api_response import APIResponse
from .exceptions import APIClientConnectionError, APIClientError, APIClientHTTPError, APIClientTimeoutError


class APIClient:
    """A standardized client for the interaction with APIs.

    This class handles the communication with an API, including retries for specific status codes.

    Attributes:
        RETRY_CODES: List of HTTP status codes that should trigger a retry.
        MAX_SLEEP_TIME: Maximum time to wait between retries, in seconds.
        base_url: The base URL for the API.
        session: The session object for making requests.
    """

    RETRY_CODES: list[int] = [
        HTTPStatus.TOO_MANY_REQUESTS,
        HTTPStatus.SERVICE_UNAVAILABLE,
        HTTPStatus.GATEWAY_TIMEOUT,
    ]

    MAX_SLEEP_TIME: int = 180  # seconds

    def __init__(
        self,
        base_url: str,
        auth: AuthBase | None = None,
        default_headers: dict[str, str] | None = None,
    ):
        """Initializes the APIClient object.

        Args:
            base_url: The base URL for the API.
            auth: The authentication method for the API.
            default_headers: Default headers to include in requests.
        """
        if not base_url.endswith("/"):
            base_url += "/"
        self.base_url = base_url
        self.session = requests.Session()
        if default_headers:
            self.session.headers.update(default_headers)
        self.session.auth = auth

    def _make_request(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        params: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        max_retries: int = 0,
    ) -> APIResponse:
        """Makes a request to the API endpoint.

        Args:
            method: The HTTP method to use for the request.
            endpoint: The endpoint to send the request to.
            timeout: The timeout for the request in seconds.
            params: The query parameters for the request.
            data: The form data to include in the request.
            json: The JSON data to include in the request.
            headers: The headers to include in the request.
            max_retries: The maximum number of retries for the request.

        Returns:
            APIResponse: The response from the API.

        Raises:
            APIClientError: If the request fails.
        """
        url = urljoin(self.base_url, endpoint.strip("/"))
        params = params or {}
        data = data or {}
        json = json or {}
        headers = headers or {}

        for attempt in range(max_retries + 1):
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=timeout,
                    params=params,
                    data=data,
                    json=json,
                    headers=headers,
                )
                if response.status_code not in APIClient.RETRY_CODES:
                    response.raise_for_status()
                    return APIResponse(response)
            except requests.exceptions.HTTPError as err:
                raise APIClientHTTPError(f"HTTP error occurred: {err}") from err
            except requests.exceptions.ConnectionError as err:
                if attempt < max_retries:
                    sleep_time = min(2**attempt, APIClient.MAX_SLEEP_TIME)
                    sleep(sleep_time)
                    continue
                raise APIClientConnectionError(f"Connection error occurred: {err}") from err
            except requests.exceptions.Timeout as err:
                raise APIClientTimeoutError(f"Timeout error occurred: {err}") from err
            except requests.exceptions.RequestException as err:
                raise APIClientError(f"An error occurred: {err}") from err
        raise APIClientError(f"The maximum configured retries of [ '{max_retries}' ] have been exceeded")

    def get(self, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a GET request to the specified endpoint.

        Args:
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method="GET", endpoint=endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a POST request to the specified endpoint.

        Args:
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method="POST", endpoint=endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a PUT request to the specified endpoint.

        Args:
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method="PUT", endpoint=endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a DELETE request to the specified endpoint.

        Args:
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method="DELETE", endpoint=endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a PATCH request to the specified endpoint.

        Args:
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method="PATCH", endpoint=endpoint, **kwargs)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> APIResponse:
        """Sends a request to the specified endpoint with the specified method.

        Args:
            method: The HTTP method to use for the request.
            endpoint: The endpoint to send the request to.
            **kwargs: Additional arguments to pass to the request.

        Returns:
            APIResponse: The response from the API.
        """
        return self._make_request(method=method, endpoint=endpoint, **kwargs)
