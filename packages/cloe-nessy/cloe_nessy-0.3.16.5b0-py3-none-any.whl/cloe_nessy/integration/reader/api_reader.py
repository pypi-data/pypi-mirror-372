import json
from typing import Any

import pyspark.sql.functions as F
from pyspark.sql import DataFrame
from requests.auth import AuthBase

from cloe_nessy.clients.api_client.api_response import APIResponse

from ...clients.api_client import APIClient
from ...clients.api_client.exceptions import (
    APIClientConnectionError,
    APIClientError,
    APIClientHTTPError,
    APIClientTimeoutError,
)
from .reader import BaseReader


class APIReader(BaseReader):
    """Utility class for reading an API into a DataFrame.

    This class uses an APIClient to fetch data from an API and load it into a Spark DataFrame.

    Attributes:
        api_client: The client for making API requests.
    """

    def __init__(self, base_url: str, auth: AuthBase | None, default_headers: dict[str, str] | None = None):
        """Initializes the APIReader object.

        Args:
            base_url : The base URL for the API.
            auth: The authentication method for the API.
            default_headers: Default headers to include in requests.
        """
        super().__init__()
        self.api_client = APIClient(base_url, auth, default_headers)

    def read(
        self,
        *,
        endpoint: str = "",
        method: str = "GET",
        key: str | None = None,
        timeout: int = 30,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        json_body: dict[str, str] | None = None,
        max_retries: int = 0,
        options: dict[str, str] | None = None,
        add_metadata_column: bool = False,
        **kwargs: Any,
    ) -> DataFrame:
        """Reads data from an API endpoint and returns it as a DataFrame.

        Args:
            endpoint: The endpoint to send the request to.
            method: The HTTP method to use for the request.
            key: The key to extract from the JSON response.
            timeout: The timeout for the request in seconds.
            params: The query parameters for the request.
            headers: The headers to include in the request.
            data: The form data to include in the request.
            json_body: The JSON data to include in the request.
            max_retries: The maximum number of retries for the request.
            options: Additional options for the createDataFrame function.
            add_metadata_column: If set, adds a __metadata column containing metadata about the API response.
            **kwargs: Additional keyword arguments to maintain compatibility with the base class method.

        Returns:
            DataFrame: The Spark DataFrame containing the read data in the json_object column.

        Raises:
            RuntimeError: If there is an error with the API request or reading the data.
        """
        if options is None:
            options = {}
        try:
            response = self.api_client.request(
                method=method,
                endpoint=endpoint,
                timeout=timeout,
                params=params,
                headers=headers,
                data=data,
                json=json_body,
                max_retries=max_retries,
            )
            data_list = response.to_dict(key)
            json_string = json.dumps(data_list)
            df: DataFrame = self._spark.createDataFrame(data={json_string}, schema=["json_string"], **options)  # type: ignore
            row = df.select("json_string").head()
            if row is not None:
                schema = F.schema_of_json(row[0])
            else:
                raise RuntimeError("It was not possible to infer the schema of the JSON data.")
            df_result = df.withColumn("json_object", F.from_json("json_string", schema)).select("json_object")
            if add_metadata_column:
                df_result = self._add_metadata_column(df_result, response)
            return df_result

        except (APIClientHTTPError, APIClientConnectionError, APIClientTimeoutError) as e:
            raise RuntimeError(f"API request failed: {e}") from e
        except APIClientError as e:
            raise RuntimeError(f"An error occurred while reading the API data: {e}") from e
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {e}") from e

    def _add_metadata_column(self, df: DataFrame, response: APIResponse):
        """Adds a metadata column to a DataFrame.

        This method appends a column named `__metadata` to the given DataFrame, containing a map
        of metadata related to an API response. The metadata includes the current timestamp,
        the base URL of the API, the URL of the request, the HTTP status code, the reason phrase,
        and the elapsed time of the request in seconds.

        Args:
            df: The DataFrame to which the metadata column will be added.
            response: The API response object containing the metadata to be added.

        Returns:
            DataFrame: The original DataFrame with an added `__metadata` column containing the API response metadata.
        """
        df = df.withColumn(
            "__metadata",
            F.create_map(
                F.lit("timestamp"),
                F.current_timestamp(),
                F.lit("base_url"),
                F.lit(self.api_client.base_url),
                F.lit("url"),
                F.lit(response.url),
                F.lit("status_code"),
                F.lit(response.status_code),
                F.lit("reason"),
                F.lit(response.reason),
                F.lit("elapsed"),
                F.lit(response.elapsed),
            ),
        )
        return df
