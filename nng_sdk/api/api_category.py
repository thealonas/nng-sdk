import os
from typing import Optional

import requests
from requests import Response


class ApiCategory:
    url: str
    token: Optional[str] = None

    def __init__(self, token: str, url: Optional[str] = None):
        self.token = token
        self.url = url
        if not self.url:
            self.url = os.environ.get("NNG_API_URL")

    def __construct_headers(self) -> dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        headers["Content-Type"] = "application/json"
        return headers

    @staticmethod
    def _handle_request(response: Response, raise_for_status: bool):
        if raise_for_status:
            response.raise_for_status()

        return response.json()

    def make_path(self, path: str) -> str:
        return f"{self.url}/{path}"

    def _raw_post(self, path: str, data: dict):
        return requests.post(
            self.make_path(path), json=data, headers=self.__construct_headers()
        )

    def _post(self, path: str, data: dict, raise_for_status: bool = True):
        return self._handle_request(self._raw_post(path, data), raise_for_status)

    def _raw_get(self, path: str):
        return requests.get(self.make_path(path), headers=self.__construct_headers())

    def _get(self, path: str, raise_for_status: bool = True):
        return self._handle_request(self._raw_get(path), raise_for_status)

    def _raw_put(self, path: str, data: dict):
        return requests.put(
            self.make_path(path), json=data, headers=self.__construct_headers()
        )

    def _put(self, path: str, data: dict, raise_for_status: bool = True):
        return self._handle_request(self._raw_put(path, data), raise_for_status)
