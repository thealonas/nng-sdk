import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.user import BanPriority
from nng_sdk.pydantic_models.watchdog import Watchdog


class WatchdogWebsocketLogType(StrEnum):
    new_warning = "new_warning"
    new_ban = "new_ban"


class WatchdogWebsocketLog(BaseModel):
    type: WatchdogWebsocketLogType
    priority: BanPriority
    group: int
    send_to_user: int


class WatchdogAdditionalInfo(BaseModel):
    intruder: Optional[int] = None
    group_id: Optional[int] = None
    victim: Optional[int] = None
    date: Optional[datetime.date] = None
    reviewed: Optional[bool] = None


class PutWatchdog(BaseModel):
    intruder: Optional[int] = None
    victim: Optional[int] = None
    group_id: int
    priority: BanPriority
    date: datetime.date
    reviewed: bool = False


class WatchdogCategory(ApiCategory):
    def get_watchdog_logs(self) -> list[Watchdog]:
        return [Watchdog.model_validate(i) for i in self._get("watchdog/list")]

    def get_watchdog_by_id(self, watchdog_id: int) -> Watchdog:
        return Watchdog.model_validate(self._get(f"watchdog/get/{watchdog_id}"))

    def post_watchdog_additional_info(
        self, watchdog_id: int, data: WatchdogAdditionalInfo
    ):
        return self._post(
            f"watchdog/update/{watchdog_id}", data.model_dump(mode="json")
        )

    def add_watchdog_log(self, data: PutWatchdog) -> Watchdog:
        return Watchdog.model_validate(
            self._put("watchdog/add", data.model_dump(mode="json"))
        )

    def notify_watchdog_log(self, data: WatchdogWebsocketLog):
        return self._post("watchdog/notify_user", data.model_dump(mode="json"))
