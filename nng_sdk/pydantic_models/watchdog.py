import datetime
from typing import Optional

from nng_sdk.pydantic_models.base_model import BaseNngModel
from nng_sdk.pydantic_models.user import BanPriority


class Watchdog(BaseNngModel):
    watchdog_id: int = -1
    intruder: Optional[int] = None
    victim: Optional[int] = None
    group_id: int
    priority: BanPriority
    date: datetime.date
    reviewed: bool = False
