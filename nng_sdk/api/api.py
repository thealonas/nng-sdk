import os
from typing import Optional

import requests

from nng_sdk.api.editor_category import EditorCategory
from nng_sdk.api.groups_category import GroupsCategory
from nng_sdk.api.invites_category import InvitesCategory
from nng_sdk.api.requests_category import RequestsCategory
from nng_sdk.api.tg_users_category import TgUsersCategory
from nng_sdk.api.tickets_category import TicketsCategory
from nng_sdk.api.users_category import UsersCategory
from nng_sdk.api.utils_category import UtilsCategory
from nng_sdk.api.watchdog_category import WatchdogCategory


class NngApi:
    class NngApiException(Exception):
        pass

    def __init__(self, service_name: str, credential: str, url: Optional[str] = None):
        self.token = ""
        self.url = url
        if not self.url:
            self.url = os.environ.get("NNG_API_URL")

        self.auth(service_name, credential)

        self.editor = EditorCategory(self.token, self.url)
        self.users = UsersCategory(self.token, self.url)
        self.groups = GroupsCategory(self.token, self.url)
        self.invites = InvitesCategory(self.token, self.url)
        self.requests = RequestsCategory(self.token, self.url)
        self.tickets = TicketsCategory(self.token, self.url)
        self.utils = UtilsCategory(self.token, self.url)
        self.watchdog = WatchdogCategory(self.token, self.url)
        self.telegram = TgUsersCategory(self.token, self.url)

    def auth(self, service_name: str, credential: str):
        req = requests.post(
            f"{self.url}/auth",
            json={"service_name": service_name, "credential": credential},
        )

        req.raise_for_status()
        self.token = req.json()["token"]
