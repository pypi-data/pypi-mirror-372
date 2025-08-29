import json
import os
import requests
from http import HTTPMethod


class DtaRequest:
    """
    Base class for defining base Request in the DTA API.
    """
    method: str = HTTPMethod.GET
    path: str = ''
    data: dict = None
    headers: dict = {}
    args: dict = {}

    def __init__(self,
                 method: str = HTTPMethod.GET,
                 path: str = None,
                 data: dict = None,
                 headers: dict = None,
                 args: dict = None):
        """
        Initialize the DtaRequest with optional parameters.

        Parameters:
            method (str): The HTTP method (GET, POST, etc.).
            path (str): The endpoint path.
            data (dict): Optional data for the request.
            headers (dict): Optional headers for the request.
            args (dict): Optional arguments for the request.
        """
        self.method = str(method).upper() or self.method
        self.path = path or self.path
        self.data = data or self.data
        self.headers = headers or self.headers
        self.args = args or self.args

        if self.method in [HTTPMethod.GET, HTTPMethod.DELETE]:
            self.data = None
        elif self.method in [HTTPMethod.POST,
                             HTTPMethod.PUT,
                             HTTPMethod.PATCH]:
            self.headers['Content-Type'] = 'application/json'
            if self.data is None:
                self.data = {}
            self.data = json.dumps(self.data)
        else:
            raise ValueError(f"Unsupported DTA Request method: {self.method}")


class DtaBaseApi:
    _last_response: requests.models.Response = None

    def __init__(self, **kwargs):
        """
        Initialize the DtaBase client class with optional keyword arguments.

        Parameters:
            **kwargs: Optional keyword arguments to initialize the class.
        """
        self.organization = kwargs.get('organization', None)
        self.project = kwargs.get('project', None)
        self.authorization = kwargs.get('authorization', None)
        self.dta_authorization = kwargs.get('dta_authorization', None)
        self._base_url = os.environ.get('DTA_BASE_URL', '')

    def build_url(self, dta_request: DtaRequest):
        """
        Build the full URL by appending the path to the base URL.

        Parameters:
            path (str): The endpoint path to append to the base URL.

        Returns:
            str: The full URL.
        """
        if self.organization:
            self._base_url = self._base_url.replace(
                '{DTA_ORGANIZATION}', self.organization
            )
        path = dta_request.path
        if self._base_url.endswith('/') and path.startswith('/'):
            path = path[1:]
        elif not self._base_url.endswith('/') and not path.startswith('/'):
            path = '/' + path
        args = ''
        if dta_request.args:
            args = '?' + '&'.join(
                [f'{key}={value}' for key, value in dta_request.args.items()]
            )
        return self._base_url + path + args

    def call(self, dta_request: DtaRequest):
        """
        Make an HTTP request to the specified path with the given method,
        parameters, and headers.

        Parameters:
            dta_request (DtaRequest): The DTARequest class instance

        Returns:
            Response data from the requests library.
        """
        headers = {
            'Accept': 'application/json',
            'x-dta-service': os.environ.get('DTA_SERVICE', 'DtaUtils'),
        }
        if self.authorization:
            authorization = f'Bearer {self.authorization}' if (
                not self.authorization.startswith('Bearer')
            ) else self.authorization
            headers['Authorization'] = authorization
        else:
            headers['x-dta-authorization'] = self.dta_authorization or ''

        headers.update(dta_request.headers or {})
        response = requests.request(dta_request.method,
                                    self.build_url(dta_request),
                                    data=dta_request.data,
                                    headers=headers)
        self._last_response = response
        return response


class DtaProxy(DtaBaseApi):

    def __init__(self, **kwargs):
        """
        Initialize the DtaProxy class with optional keyword arguments.
        Parameters:
            **kwargs: Optional keyword arguments to initialize the class.
        """
        super().__init__(
            organization=kwargs.get('organization', None),
            project=kwargs.get('project', None),
            authorization=kwargs.get('authorization', None),
            dta_authorization=kwargs.get('dta_authorization', None),
        )

    def create_key(self, key_alias: str, metadata: dict = None,
                   langfuse_autotrace: bool = False,
                   pii: bool = False, models: list = [],
                   cache: bool = True):
        """
        Create a new proxy key.

        Parameters:
            key_alias (str): The alias for the key.
            metadata (dict): Optional metadata for the key.
            langfuse_autotrace (bool): Optional flag for Langfuse autotrace.
            pii (bool): Optional flag for PII.
            models (list): List of models to associate with the key.
            cache (bool): Optional flag to enable or disable caching.

        Returns:
            dict: The response from the API call.
        """
        metadata = metadata or {}
        metadata.update({"cache": {"no-cache": not cache}})
        payload = {
            "team_id": self.project,
            "key_alias": key_alias,
            "metadata": metadata,
            "langfuse_autotrace": langfuse_autotrace,
            "permissions": {"pii": pii},
            "models": models
        }
        if os.environ.get('DTA_BASE_VERSION') == 'deprecated':
            self.call(DtaRequest(
                method='POST',
                path=f'/proxy/projects/{self.project}/keys',
                data=payload
            ))
        else:
            self.call(DtaRequest(
                method='POST',
                path=f'/tenants/{self.project}/proxy-keys',
                data=payload
            ))

        if self._last_response.status_code == 200:
            return self._last_response.json()

    def delete_key(self, token_key: str):
        if os.environ.get('DTA_BASE_VERSION') == 'deprecated':
            self.call(DtaRequest(
                method='POST',
                path=f'/proxy/projects/{self.project}/keys/{token_key}/delete',
            ))
        else:
            self.call(DtaRequest(
                method='POST',
                path=f'/tenants/{self.project}/proxy-keys/{token_key}/delete',
            ))

        if self._last_response.status_code == 200:
            return self._last_response.json()

    def get_key(self, token_key: str):
        if os.environ.get('DTA_BASE_VERSION') == 'deprecated':
            self.call(DtaRequest(
                path=f'/proxy/projects/{self.project}/keys/{token_key}',
            ))
        else:
            self.call(DtaRequest(
                path=f'/tenants/{self.project}/proxy-keys/{token_key}',
            ))

        if self._last_response.status_code == 200:
            return self._last_response.json()
