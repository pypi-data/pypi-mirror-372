import os
import requests
from http import HTTPMethod, HTTPStatus
from typing import Any, Tuple, Text, Dict


class DtaServiceHeader:

    def __init__(self,
                 organization: str,
                 project: str,
                 authorization: str) -> None:
        self.project = project
        self._authorization = None
        self.authorization = authorization
        self.organization = organization

    def get(self) -> Dict[str, str]:
        """
        Retrieve a dictionary containing authorization and project information.

        Returns:
            Dict[str, str]: A dictionary with keys "Authorization" and
                            "x-dta-project", containing the respective
                            authorization token and project identifier. If no
                            authorization token is provided, it attempts to
                            retrieve it from the environment variable
                            "DTA_AUTHORIZATION".
        """
        _header = {
            "x-dta-project": self.project
        }
        if self.organization:
            _header.update({"x-dta-override-organization": self.organization})

        # If no Authorization token provided, try internal native integration
        _header.update({
            "x-dta-authorization": os.environ.get("DTA_AUTHORIZATION", ''),
        }) if self.authorization is None else _header.update({
            "Authorization": self.authorization
        })
        return _header

    @property
    def authorization(self) -> str:
        return self._authorization

    @authorization.setter
    def authorization(self, value: str) -> None:
        """
        Sets the authorization token with a "Bearer " prefix if not already
        present.

        Args:
            value (str): The authorization token to be set.

        Raises:
            ValueError: If the provided value is not a string.
        """
        if value and not str(value).startswith("Bearer "):
            value = f"Bearer {str(value)}"
        self._authorization = value


class DTASecretsCache:

    def __init__(self):
        self.cache = {}

    def has(self, key: str) -> bool:
        """
        Check if the given key exists in the cache.

        Args:
            key (str): The key to check in the cache.

        Returns:
            bool: True if the key exists in the cache, False otherwise.
        """
        return key in self.cache

    def get(self, key: str) -> Any:
        """
        Retrieve a value from the cache using the provided key.

        Args:
            key (str): The key for the value to retrieve from the cache.

        Returns:
            Any: The value associated with the provided key, or None if the key
                 is not found.
        """
        return self.cache.get(key)

    def _set_batch(self, data: dict) -> None:
        """
        Sets multiple key-value pairs in the instance.

        This method takes a dictionary of key-value pairs and sets each
        key-value pair in the instance using the `_set` method.

        Args:
            data (dict): A dictionary containing key-value pairs to be set.
        """
        if data:
            for key, value in data.items():
                self._set(key, value)

    def _set(self, key: str, value: Any) -> None:
        """
        Sets a value in the cache for the given key.

        Args:
            key (str): The key for the value to be set in the cache.
            value (Any): The value to be stored in the cache.
        """
        self.cache[key] = value

    def _all(self) -> Dict[str, Any]:
        """
        Retrieve all cached secrets.

        Returns:
            Dict[str, Any]: A dictionary containing all cached secrets.
        """
        return self.cache


class DtaSecrets:

    def __init__(self,
                 authorization: str = None,
                 organization: str = None,
                 project: str = None,
                 raise_exception: bool = False,
                 autoload: bool = True) -> None:
        self.authorization = authorization
        self.raise_exception = raise_exception
        self.is_production = os.getenv("DTA_ENVIRONMENT") == "production"
        self.env_prefix = "production" if self.is_production else "development"
        self.dta_project = project
        self.dta_organization = organization
        self.cache = None
        self.set_project(project)
        if autoload:
            self.load_all()

    def load_all(self):
        """
        Loads all secrets and caches them.

        This method initializes a new DTASecretsCache instance and assigns it
        to the cache attribute. It then retrieves all secrets without using
        caching and sets them in the cache.
        """
        self.cache = DTASecretsCache()
        all_secrets = self.get_all(caching=False)
        self.cache._set_batch(all_secrets)

    def get_all(self, project: str = None,
                caching: bool = True) -> dict:
        """
        Retrieve all secrets for the specified project.

        Args:
            project (str | None): The name of the project to retrieve secrets
                                  for. If None, the current project is used.
            caching (bool): Whether to use cached data if available. Defaults
                            to True.

        Returns:
            dict: A dictionary containing all the secrets for the specified
                  project.

        Raises:
            Exception: If there is an error retrieving the secrets.
        """
        self.set_project(project)
        if caching and self.cache:
            return self.cache._all()
        get_data = self.__ask(f"/retrieve/{self.env_prefix}/all")
        if get_data.status_code == HTTPStatus.OK:
            return get_data.json()

    def get(self,
            secret_name: str,
            fallback: any = None,
            project: str = None,
            version: int = None) -> str | int | None:
        """
        Retrieve a secret value from the secret management system.

        Args:
            secret_name (str): The name of the secret to retrieve.
            project (str | None, optional): The project associated with the
                                            secret. Defaults to None.
            version (int | None, optional): The version of the secret to
                                            retrieve. Defaults to None.

        Returns:
            str | int | None: The value of the secret, or None if the secret
                              is not found.
        """
        self.set_project(project)
        if not version and self.cache and self.cache.has(secret_name):
            return self.cache.get(secret_name)
        get_data = self.__ask(
            f"/retrieve/{self.env_prefix}/{secret_name}/versions/{
                self.get_version(version)
            }"
        )
        if get_data.status_code == 200:
            return get_data.json().get("value")
        return fallback

    def set_project(self, project: str) -> None:
        """
        Sets the project name for the current instance.

        Parameters:
        project (str): The name of the project to be set. If the project name
                       is not empty, it will be assigned to the instance
                       variable `dta_project`.
        """
        if project:
            self.dta_project = project

    def get_version(self, version: int) -> str | int:
        """
        Retrieve the version as an integer if it is a valid digit, otherwise
        return "latest".

        Args:
            version (int): The version number to be checked.

        Returns:
            str | int: The integer version if valid, otherwise the string
                       "latest".
        """
        if version and str(version).isdigit():
            return int(version)
        return "latest"

    def set(self,
            name: str,
            value: str,
            description: str,
            origin_id: str = None,
            project: str = None) -> dict:
        """
        Creates or updates a secret in the DTA Secrets Manager via HTTP API.

        Args:
            name (str): The name of the secret to be created.
            value (str): The value of the secret to be stored.
            origin_id (str, optional): The ID of the entity
                                        associated with the secret.
            project (str, optional): The project associated with the
                                        secret. Defaults to None.

        Returns:
            dict: The response JSON from the API on successful
                    creation or update.

        Raises:
            DtaSecretsError: If the request to create the secret fails.
        """
        self.set_project(project)
        payload = {
            "name": name,
            "value": value,
            "description": description
        }
        if origin_id:
            payload["origin_id"] = origin_id

        service_url, headers = self.__service_builder()

        response = requests.post(
            url=f"{service_url}/secrets?environment={self.env_prefix}",
            json=payload,
            headers=headers
        )

        if response.status_code not in (200, 201):
            raise DtaSecretsError(f"Erro ao criar segredo: {response.text}")

        if self.cache:
            self.cache._set(name, value)

        return response.json()

    def destroy(self,
                secret_id: str,
                project: str = None) -> dict:
        """
        Deletes a secret by its name from the DTA Secrets Manager via HTTP API.

        Args:
            name (str): The name of the secret to be created.
            project (str, optional): The project associated with the
                secret. Defaults to None.
        Returns:
            dict: The response JSON from the API if the deletion
                was successful.

        Raises:
            DtaSecretsError: If the request fails or the secret cannot
                be deleted.
        """
        self.set_project(project)
        service_url, headers = self.__service_builder()

        response = requests.delete(
            url=f"{service_url}/secrets/{secret_id}?environment={self.env_prefix}",
            headers=headers
        )

        if response.status_code != 200:
            raise DtaSecretsError(f"Failed to delete secret: {response.text}")

        if self.cache and self.cache.has(secret_id):
            del self.cache.cache[secret_id]

        return response.json()

    def __ask(self, resource: str, payload: dict = {}) -> Any:
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
        secret_response = requests.request(HTTPMethod.GET,
                                           service_url + resource,
                                           headers=headers, data=payload)
        return secret_response

    def __service_builder(self) -> Tuple[Text, Dict]:
        """
        This method constructs the service URL from the environment variable
        `DTA_SECRETS_URL` and creates the necessary headers using the
        `DtaServiceHeader` class.

        Raises:
            DtaSecretsError: If the `DTA_SECRETS_URL` environment variable is
                             not set or is an empty string.
        """
        headers = DtaServiceHeader(organization=self.dta_organization,
                                   project=self.dta_project,
                                   authorization=self.authorization)
        service_url = os.environ.get("DTA_SECRETS_URL")
        if not service_url or not isinstance(service_url, str):
            raise DtaSecretsError(
                "`DTA_SECRETS_URL` is not set or it has an invalid value."
            )
        if service_url.endswith("/"):
            service_url = service_url[:-1]
        return service_url, headers.get()


class DtaSecretsError(Exception):

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
