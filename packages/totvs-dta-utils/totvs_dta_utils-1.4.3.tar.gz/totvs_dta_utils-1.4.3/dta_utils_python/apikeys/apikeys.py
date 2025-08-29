import os
import requests
from http import HTTPMethod, HTTPStatus
from typing import Any, Dict, Optional, Text, Tuple


class DtaApiKeys:

    def __init__(self, project: str = None, organization: str = None) -> None:
        self.project = project
        self.organization = organization

    def validate(self, apikey: str, scope: str,
                 related_id: Optional[str] = None) -> bool:
        """
        Validates an API key against a specific scope.

        Args:
            apikey (str): The API key to validate.
            scope (str): The scope to validate against.
            related_id (Optional[str], optional): An optional related ID.

        Returns:
            bool: True if the API key is valid for the specified scope,
                False otherwise.
        """
        if not self.project or not apikey or not scope:
            return False

        json_payload = {"related_id": related_id} if related_id else {}

        validate_data = self.__ask(
            (
                f"/tenants/{self.project}/apikeys/{apikey}/"
                f"scopes/{scope}/validate"
            ),
            json=json_payload,
            method=HTTPMethod.POST
        )
        if validate_data.status_code == HTTPStatus.OK:
            return True
        return False

    def __ask(self, resource: str, payload: dict = None,
              json: dict = None, method: str = HTTPMethod.GET) -> Any:
        """
        Makes a request to a specified resource with an optional payload.

        Args:
            resource (str): The resource endpoint to request.
            payload (dict, optional): The data to send with the request.
                                      Defaults to an empty dictionary.

        Returns:
            Any: The response from the request.

        Notes:
            If the instance is in production mode, '/production' is appended
            to the resource URL.
        """
        service_url, headers = self.__service_builder()
        secret_response = requests.request(
            method, service_url + resource, headers=headers, data=payload,
            json=json
        )
        return secret_response

    def __service_builder(self) -> Tuple[Text, Dict]:
        """
        This method constructs the service URL from the environment variable
        `DTA_SECRETS_URL` and creates the necessary headers using the
        `DtaServiceHeader` class.

        Raises:
            DtaSecretsError: If the `DTA_INTEGRATION_URL` environment variable
                             is not set or is an empty string.
        """
        headers = {
            "Content-Type": "application/json",
        }
        service_url = os.environ.get("DTA_INTEGRATION_URL",
                                     os.environ.get("DTA_URL"))
        if not service_url or not isinstance(service_url, str):
            raise DtaApiKeyError(
                "`DTA_INTEGRATION_URL` is not set or it has an invalid value."
            )
        if service_url.endswith("/"):
            service_url = service_url[:-1]
        if self.organization:
            service_url = service_url.replace('{DTA_ORGANIZATION}',
                                              self.organization)
        return service_url, headers


class DtaApiKeyError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class DTAScopes:
    """
    This class is a base class for the scopes used in the DTA API keys."""
    pass


# Services scopes

class FlowScope(DTAScopes):
    ALIAS: str = "flow"
    PREFIX: str = f"{ALIAS}:"

    RUN: str = f"{PREFIX}run"
    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"


class KBScope(DTAScopes):
    ALIAS: str = "kb"
    PREFIX: str = f"{ALIAS}:"

    RUN: str = f"{PREFIX}run"
    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"


class AgentScope(DTAScopes):
    ALIAS: str = "agent"
    PREFIX: str = f"{ALIAS}:"

    RUN: str = f"{PREFIX}run"
    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"


# API Base scopes

class ApiKeyScope(DTAScopes):
    ALIAS: str = "api_key"
    PREFIX: str = f"{ALIAS}:"

    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"


class DtaKeyScope(DTAScopes):
    ALIAS: str = "dta_key"
    PREFIX: str = f"{ALIAS}:"

    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"


class DtaPlanScope(DTAScopes):
    ALIAS: str = "plan"
    PREFIX: str = f"{ALIAS}:"

    READ: str = f"{PREFIX}read"


class ProjectScope(DTAScopes):
    ALIAS: str = "project"
    PREFIX: str = f"{ALIAS}:"

    READ: str = f"{PREFIX}read"


class UserScope(DTAScopes):
    ALIAS: str = "user"
    PREFIX: str = f"{ALIAS}:"

    CREATE: str = f"{PREFIX}create"
    READ: str = f"{PREFIX}read"
    UPDATE: str = f"{PREFIX}update"
    DELETE: str = f"{PREFIX}delete"
