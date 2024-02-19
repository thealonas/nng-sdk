import datetime
from enum import StrEnum
from typing import Optional

from nng_sdk.pydantic_models.base_model import BaseNngModel


class RequestType(StrEnum):
    unblock = "unblock"
    complaint = "complaint"


class Request(BaseNngModel):
    request_id: int = -1
    request_type: RequestType
    created_on: datetime.date
    user_id: int
    intruder: Optional[int] = None
    user_message: str
    vk_comment: Optional[str] = None
    answer: Optional[str] = None
    decision: bool
    answered: bool
