import datetime
from enum import StrEnum

from sqlalchemy import Integer, Enum, Date, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class RequestType(StrEnum):
    unblock = "unblock"
    complaint = "complaint"


class DbRequest(BaseDatabaseModel):
    __tablename__ = "requests"

    request_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_type: Mapped[RequestType] = mapped_column(Enum(RequestType))
    created_on: Mapped[datetime.date] = mapped_column(Date)
    user_id: Mapped[int] = mapped_column(Integer)
    user_message: Mapped[str] = mapped_column(Text)
    vk_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    intruder: Mapped[int | None] = mapped_column(Integer, nullable=True)
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    decision: Mapped[bool] = mapped_column(Boolean)
    answered: Mapped[bool] = mapped_column(Boolean)

    def to_dict(self) -> dict:
        return vars(self)
