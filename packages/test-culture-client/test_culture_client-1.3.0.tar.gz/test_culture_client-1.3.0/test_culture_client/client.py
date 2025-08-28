from typing import Optional, Union
from pydantic import BaseModel
from test_culture_client.endpoints.folder import FolderEndpoint
from test_culture_client.endpoints.test_case import TestCaseEndpoint
from test_culture_client.endpoints.test_cycle import TestCycleEndpoint
from test_culture_client.endpoints.test_run import TestRunEndpoint
from test_culture_client.endpoints.unit import UnitEndpoint
from test_culture_client.utils import assert_http_status, strip_trailing_slash

from requests import Session
from requests.cookies import RequestsCookieJar


class ApiClient:
    __session: Session
    __base_url: str
    __timeout: int

    def __init__(
        self,
        url: str,
        token: str = None,
        cookies: RequestsCookieJar = None,
        verify: bool = None,
        cert: str = None,
        timeout: int = None,
    ):

        self.__session = self._create_session(token, cookies, verify, cert)
        self.__base_url = strip_trailing_slash(url)
        self.__timeout = timeout

    def _create_session(
        self, token=None, cookies: RequestsCookieJar = None, verify=None, cert=None
    ) -> Session:
        """
        Configure the TestCulture API client
        """

        session = Session()
        if token:
            session.headers["Authorization"] = f"Bearer {token}"
        if cookies:
            session.cookies = cookies
        if verify is not None:
            session.verify = verify
        if cert is not None:
            session.cert = cert
        return session

    def request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
        json: Optional[Union[dict, BaseModel]] = None,
        timeout: int = None,
    ) -> dict | None:
        if json is not None:
            if isinstance(json, BaseModel):
                json = json.model_dump()

        response = self.__session.request(
            method,
            url=self.__base_url + path,
            params=params,
            data=data,
            json=json,
            timeout=timeout or self.__timeout,
        )
        assert_http_status(response)

        if response.text:
            return response.json()

    def get(self, path, params=None, data=None, json=None, timeout=None) -> dict | None:
        return self.request("GET", path, params, data, json, timeout)

    def post(
        self, path, params=None, data=None, json=None, timeout=None
    ) -> dict | None:
        return self.request("POST", path, params, data, json, timeout)

    def put(self, path, params=None, data=None, json=None, timeout=None) -> dict | None:
        return self.request("PUT", path, params, data, json, timeout)

    def patch(
        self, path, params=None, data=None, json=None, timeout=None
    ) -> dict | None:
        return self.request("PATCH", path, params, data, json, timeout)

    def delete(
        self, path, params=None, data=None, json=None, timeout=None
    ) -> dict | None:
        return self.request("DELETE", path, params, data, json, timeout)


class TestCultureClient:
    def __init__(
        self,
        url: str,
        token: str = None,
        cookies: RequestsCookieJar = None,
        verify: bool = None,
        cert: str = None,
        timeout: int = None,
    ):
        self._client = ApiClient(url, token, cookies, verify, cert, timeout)

    @property
    def units(self):
        return UnitEndpoint(self._client)

    @property
    def folders(self):
        return FolderEndpoint(self._client)

    @property
    def test_cases(self):
        return TestCaseEndpoint(self._client)

    @property
    def test_runs(self):
        return TestRunEndpoint(self._client)

    @property
    def test_cycles(self):
        return TestCycleEndpoint(self._client)
