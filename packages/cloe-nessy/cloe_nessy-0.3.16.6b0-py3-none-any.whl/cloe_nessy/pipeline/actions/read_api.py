from collections.abc import Mapping
from typing import Any, cast

from requests.auth import AuthBase, HTTPBasicAuth

from ...clients.api_client.auth import AzureCredentialAuth, ChainedAuth, EnvVariableAuth, SecretScopeAuth
from ...integration.reader import APIReader
from ..pipeline_action import PipelineAction
from ..pipeline_context import PipelineContext


def process_auth(
    auth: Mapping[str, str | Mapping[str, str] | list[Mapping[str, str]]] | AuthBase | None,
) -> AuthBase | None:
    """Processes the auth parameter to create an AuthBase object.

    Args:
        auth: The auth parameter to be processed.
    """
    result: AuthBase | None = None

    if isinstance(auth, list):
        auths = [process_auth(sub_auth) for sub_auth in auth]
        result = ChainedAuth(*auths)
    elif isinstance(auth, dict):
        match auth.get("type"):
            case "basic":
                result = HTTPBasicAuth(auth["username"], auth["password"])
            case "secret_scope":
                secret_scope_header_template: dict[str, str] = auth["header_template"]
                result = SecretScopeAuth(secret_scope_header_template, auth["secret_scope"])
            case "env":
                env_header_template: dict[str, str] = auth["header_template"]
                result = EnvVariableAuth(env_header_template)
            case "azure_oauth":
                result = AzureCredentialAuth(
                    scope=auth["scope"],
                    client_id=auth["client_id"],
                    client_secret=auth["client_secret"],
                    tenant_id=auth["tenant_id"],
                )
            case _:
                raise ValueError("Invalid auth type specified. Supported types are: basic, secret_scope, env")
    else:
        result = cast(AuthBase, auth)

    return result


class ReadAPIAction(PipelineAction):
    """Reads data from an API and loads it into a Spark DataFrame.

    This method uses the provided API parameters to make a request using the
    [`APIReader`][cloe_nessy.integration.reader.api_reader] and return a
    DataFrame containing the response data.

    Example:
        === "Basic Usage"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
            ```
        === "Usage with Parameters and Headers"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
                    method: GET
                    timeout: 90
                    headers:
                        key1: value1
                        key2: value2
                    params:
                        key1: value1
                        key2: value2
            ```
        === "Usage with Authentication"
            ```yaml
            Read API:
                action: READ_API
                options:
                    base_url: https://some_url.com/api/
                    endpoint: my/endpoint/
                    method: GET
                    timeout: 90
                    auth:
                        - type: basic
                          username: my_username
                          password: my_password
                        - type: secret_scope
                          secret_scope: my_secret_scope
                          header_template:
                            "header_key_1": "<ENVIRONMENT_VARIABLE_NAME>"
                        - type: secret_scope
                          secret_scope: my_secret_scope
                          header_template:
                            "header_key_2": "<SECRET_NAME>"
                        - type: secret_scope
                          secret_scope: my_other_secret_scope
                          header_template:
                            "header_key_3": "<SECRET_NAME>"
                        - type: azure_oauth
                          client_id: my_client_id
                          client_secret: my_client_secret
                          tenant_id: my_tenant_id
                          scope: <entra-id-client-id>
            ```

            The above example will combine the headers from the different auth types. The resulting header will look like this:

            ```json
            {
                "header_key_1": "value_from_environment_variable",
                "header_key_2": "value_from_secret",
                "header_key_3": "value_from_secret",
                "Authorization": "Bearer <access_token> (from azure_oauth)",
                "Authorization": "Basic am9obkBleGFtcGxlLmNvbTphYmMxMjM= (from basic)"
            }
            ```

    !!! warning "Secret information"
        Don't write sensitive information like passwords or tokens directly in the pipeline configuration.
        Use secret scopes or environment variables instead.
    """

    name: str = "READ_API"

    @staticmethod
    def run(
        context: PipelineContext,
        *,
        base_url: str | None = None,
        auth: AuthBase | dict[str, str] | None = None,
        default_headers: dict[str, str] | None = None,
        endpoint: str = "",  # www.neo4j.de/api/table/2020/01/01
        method: str = "GET",
        key: str | None = None,
        timeout: int = 30,
        params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        data: dict[str, str] | None = None,
        json: dict[str, str] | None = None,
        max_retries: int = 0,
        options: dict[str, str] | None = None,
        **_: Any,
    ) -> PipelineContext:
        """Utility class for reading an API into a DataFrame.

        This class uses an APIClient to fetch data from an API and load it into a Spark DataFrame.


        Args:
            context: The pipeline context containing information about the pipeline.
            base_url: The base URL for the API to be called.
            auth: The authentication credentials for the API.
            default_headers: Default headers to include in the API request.
            endpoint: The specific API endpoint to call.
            method: The HTTP method to use for the request (default is "GET").
            key: Key for accessing specific data in the response.
            timeout: Timeout for the API request in seconds (default is 30).
            params: URL parameters to include in the API request.
            headers: Additional headers to include in the request.
            data: Data to send with the request for POST methods.
            json: JSON data to send with the request for POST methods.
            max_retries: Maximum number of retries for the API request (default is 0).
            options: Additional options for the API request.

        Returns:
            The updated pipeline context containing the DataFrame with the API response data.

        Raises:
            ValueError: If the base_url is not specified.
        """
        if not options:
            options = dict()

        if base_url is None:
            raise ValueError("base_url must be specified to fetch data from API.")

        deserialized_auth = process_auth(auth)

        api_reader = APIReader(base_url=base_url, auth=deserialized_auth, default_headers=default_headers)

        df = api_reader.read(
            method=method,
            endpoint=endpoint,
            timeout=timeout,
            params=params,
            key=key,
            headers=headers,
            data=data,
            json=json,
            max_retries=max_retries,
            options=options,
        )

        return context.from_existing(data=df)
