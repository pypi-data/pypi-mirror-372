import os
import time
from typing import Any

from azure.core.credentials import TokenCredential
from azure.identity import ClientSecretCredential
from requests import PreparedRequest
from requests.auth import AuthBase

from ...session import SessionManager


class AzureCredentialAuth(AuthBase):
    """This Auth can be used with requests and an Azure Credential."""

    def __init__(
        self,
        scope: str,
        credential: TokenCredential | ClientSecretCredential | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        tenant_id: str | None = None,
    ):
        """Initializes the AzureCredentialAuth with an Azure credential.

        The client can either be initialized with a TokenCredential object or with the client_id, client_secret, and tenant_id via an ClientSecretCredential.

        Args:
            scope: The scope for the token. E.g., the client ID of the Azure AD application.
            credential: The Azure credential object.
            client_id: The client ID for the Azure AD application.
            client_secret: The client secret for the Azure AD application.
            tenant_id: The tenant ID for the Azure AD application.
        """
        if credential is None:
            if client_id is None or client_secret is None or tenant_id is None:
                raise ValueError("Either a credential or client_id, client_secret, and tenant_id must be provided.")
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
            )
        self.credential = credential
        self.scope = scope
        self._token = None

    @property
    def token(self):
        """Get a valid token using the TokenCredential."""
        if self._token is None or self._token.expires_on < (int(time.time()) + 5):
            self._token = self.credential.get_token(self.scope)
        return self._token.token

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """Appends an Authorization header to the request using the provided Azure credential.

        Args:
            r (PreparedRequest): The request that needs to be sent.

        Returns:
            PreparedRequest: The same request object but with an added Authorization header.
        """
        r.headers["Authorization"] = f"Bearer {self.token}"
        return r


class SecretScopeAuth(AuthBase):
    """This Auth pulls Secrets from a Secret Scope."""

    def __init__(self, header_template: dict[str, str], secret_scope: str):
        """Initializes the SecretScopeAuth with a header template, secret scope, and secret key.

        Args:
            header_template: The template for the header that will use the secret.
                                   secret names are defined as placeholders in curly braces.
            secret_scope: The secret scope from where the secrets will be retrieved.

        Example:
        ```python
        header_template = {
            "jfrog-user-key": "jfrog-user",
            "jfrog-password-key": "jfrog-secret",
        }
        auth = SecretScopeAuth(header_template, "my_secret_scope")
        # given, that 'jfrog-user' and 'jfrog-secret' are secrets in 'my_secret_scope'
        ```
        """
        self.header_template = header_template
        self.secret_scope = secret_scope

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """The header is constructed using the template and the secret retrieved from the secret scope.

        Args:
            r: The request that needs to be sent.

        Returns:
            PreparedRequest: The same request object, but with an added header. The header
                             is constructed using the template and the secret retrieved from
                             the secret scope.
        """
        utils = SessionManager.get_utils()
        auth_header = {key: utils.secrets.get(self.secret_scope, ref) for key, ref in self.header_template.items()}
        r.headers.update(auth_header)
        return r


class ChainedAuth(AuthBase):
    """This Auth can be used to chain multiple Auths."""

    def __init__(self, *args: Any):
        """Initializes the ChainedAuth.

        Args:
            *args: One or more Auth objects that are chained to
                              construct the auth header.

        Example:
        ```python
        auth_1 = SecretScopeAuth({"secret": "key"}, "my_secret_scope")
        auth_2 = SecretScopeAuth({"secret": "key"}, "my_other_secret_scope")
        chained_auth = ChainedAuth(auth_1, auth_2)
        ```
        """
        self.auths = list(args)

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """The header is constructed using the template and the secret retrieved from the secret scope.

        Args:
            r: The request that needs to be sent.

        Returns:
            PreparedRequest: The same request object, but with an added header. The header
                                is constructed using the template and the secret retrieved from
                                the secret scope.
        """
        for auth in self.auths:
            r = auth(r)
        return r


class EnvVariableAuth(AuthBase):
    """This Auth can be used to create an auth header from environment variables."""

    def __init__(self, header_template: dict[str, str]):
        """Initializes the EnvVariableAuth with a header template.

        Args:
            header_template: The template for the header that will use the environment variables.
                                   variable names are defined as placeholders.

        Example:
        ```python
        header_template = {
            "user": "USER_NAME",
            "password": "USER_SECRET",
        }
        auth = EnvVariableAuth(header_template)
        # given, that "USER_NAME" and "USER_SECRET" are environment variables
        ```
        """
        self.header_template = header_template

    def __call__(self, r: PreparedRequest) -> PreparedRequest:
        """The header is constructed using the template and the secret retrieved from the secret scope.

        Args:
            r: The request that needs to be sent.

        Returns:
            PreparedRequest: The same request object, but with an added header. The header
                             is constructed using the template and the secret retrieved from
                             environment variables.
        """
        auth_header = {key: os.environ.get(value, "") for key, value in self.header_template.items()}
        r.headers.update(auth_header)
        return r
