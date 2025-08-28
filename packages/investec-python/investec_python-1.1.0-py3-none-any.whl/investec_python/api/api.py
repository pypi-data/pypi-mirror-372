import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

import requests
from requests import RequestException
from requests.auth import HTTPBasicAuth

from investec_python.exception import InvestecError, InvestecAuthenticationError


class API:
    _api_url: str = "https://openapi.investec.com"

    _use_sandbox: bool = False

    _client_id: str
    _secret: str
    _api_key: str

    _token: str
    _token_expires_at: datetime

    _debug: bool = False

    def __init__(
        self,
        use_sandbox: bool,
        client_id: str = "",
        secret: str = "",
        api_key: str = "",
        debug: bool = False,
    ):
        self._use_sandbox = use_sandbox
        self._client_id = client_id
        self._secret = secret
        self._api_key = api_key
        self._debug = debug

        if use_sandbox:
            self._setup_client_for_sandbox()

        if self._client_id == "":
            raise InvestecError(
                "You chose not to use the sandbox, but did not provide a client_id"
            )

        if self._secret == "":
            raise InvestecError(
                "You chose not to use the sandbox, but did not provide a secret"
            )

        if self._api_key == "":
            raise InvestecError(
                "You chose not to use the sandbox, but did not provide a api_key"
            )

        self._refresh_token()

    def _setup_client_for_sandbox(self):
        self._api_url = "https://openapisandbox.investec.com"
        self._client_id = "yAxzQRFX97vOcyQAwluEU6H6ePxMA5eY"
        self._secret = "4dY0PjEYqoBrZ99r"
        self._api_key = "eUF4elFSRlg5N3ZPY3lRQXdsdUVVNkg2ZVB4TUE1ZVk6YVc1MlpYTjBaV010ZW1FdGNHSXRZV05qYjNWdWRITXRjMkZ1WkdKdmVBPT0="

    def _refresh_token(self):
        try:
            response = requests.post(
                f"{self._api_url}/identity/v2/oauth2/token",
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "x-api-key": self._api_key,
                },
                auth=HTTPBasicAuth(self._client_id, self._secret),
                data={"grant_type": "client_credentials"},
            )

            if response.status_code >= 400:
                raise InvestecAuthenticationError("Failed to authenticate")

            response_data = response.json()
            if (
                "access_token" not in response_data.keys()
                or "expires_in" not in response_data.keys()
            ):
                raise InvestecAuthenticationError("Failed to authenticate")

            self._token = response_data["access_token"]
            self._token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=response_data["expires_in"]
            )

        except RequestException:
            raise InvestecAuthenticationError("Failed to authenticate")

    def _is_token_valid(self):
        return self._token is not None and self._token_expires_at > datetime.now(timezone.utc)

    def _get_token(self) -> str:
        if not self._is_token_valid():
            self._refresh_token()

        return self._token

    def _get_headers(self) -> Dict:
        token = self._get_token()
        return {"Authorization": f"Bearer {token}"}

    @property
    def api_url(self) -> str:
        return self._api_url

    def get(self, resource_path: str, params: Optional[dict] = None) -> Dict:
        headers = self._get_headers()

        try:
            full_path = f"{self._api_url}/{resource_path}"
            if self._debug:
                print(f"GET {full_path}")
            if not params:
                params = {}
            response = requests.get(full_path, headers=headers, params=params)
            if self._debug:
                print(f"STATUS {response.status_code}")
                print(f"RESPONSE {json.dumps(response.json(), indent=2)}")
            if response.status_code >= 400:
                raise InvestecError(f"Failed to get resource at {resource_path}")
            return response.json()
        except RequestException:
            raise InvestecError(f"Failed to get resource at {resource_path}")


class APIMixin:
    _api: API

    @classmethod
    def build(cls, api: API):
        cls._api = api

    @property
    def api(self) -> API:
        return self._api
