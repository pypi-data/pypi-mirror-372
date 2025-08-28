from typing import Any

import requests

from .exceptions import APIClientError


class APIResponse:
    """An abstracted response to implement parsing.

    This class provides methods to parse the response from an API request.

    Attributes:
        response: The original response object.
        headers: The headers of the response.
        status_code: The status code of the response.
        content_type: The content type of the response.
    """

    def __init__(self, response: requests.Response):
        """Initializes the APIResponse object.

        Args:
            response: The response object from an API request.
        """
        self.response = response
        self.headers = self.response.headers
        self.status_code = self.response.status_code
        self.url = self.response.url
        self.reason = self.response.reason
        self.elapsed = self.response.elapsed
        self.content_type = self.headers.get("Content-Type", "").lower()

    def to_dict(self, key: str | None = None) -> dict[str, Any]:
        """Parses the values from the response into a dictionary.

        Args:
            key: The key to return from the dictionary. If specified, the method
                will return the value associated with this key from the parsed dictionary.

        Returns:
            The response parsed to a dictionary. If a key is specified,
                the method returns the value associated with this key.

        Raises:
            KeyError: If the specified key is not found in the response.
            ValueError: If there is an error parsing the JSON response.
            Exception: For any other unexpected errors.
        """
        dict_response = {}
        try:
            if "application/json" in self.content_type:
                dict_response = self.response.json()
            else:
                # Handling of other response types can be added below.
                dict_response = {"value": self.response.text}

            if key:
                dict_response = dict_response[key]
        except KeyError as err:
            raise KeyError(
                f"The key '{err.args[0]}' was not found in the response. Status code: {self.status_code}, Headers: {self.headers}, Response: {dict_response}"
            ) from err
        except ValueError as err:
            raise ValueError(
                f"Error parsing JSON response: {err}. Status code: {self.status_code}, Headers: {self.headers}, Response content: {self.response.text}"
            ) from err
        except Exception as err:
            raise APIClientError(
                f"An unexpected error occurred: {err}. Status code: {self.status_code}, Headers: {self.headers}, Response content: {self.response.text}"
            ) from err
        return dict_response
