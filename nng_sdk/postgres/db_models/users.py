import datetime
from enum import StrEnum
from typing import Optional, List

from sqlalchemy import (
    Text,
    Boolean,
    Integer,
    Date,
    ForeignKey,
    Enum,
    ARRAY,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class ViolationType(StrEnum):
    warned = "warned"
    banned = "banned"


class BanPriority(StrEnum):
    green = "green"
    teal = "teal"
    orange = "orange"
    red = "red"


class DbUser(BaseDatabaseModel):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    admin: Mapped[bool] = mapped_column(Boolean)
    invited_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    join_date: Mapped[datetime.date] = mapped_column(Date)
    groups: Mapped[List[int]] = mapped_column(ARRAY(Integer))

    trust_info: Mapped["DbTrustInfo"] = relationship(
        "DbTrustInfo",
        back_populates="user",
        cascade="save-update, merge, delete, delete-orphan",
    )

    violations: Mapped[List["DbViolation"]] = relationship(
        "DbViolation",
        back_populates="user",
        cascade="save-update, merge, delete, delete-orphan",
    )

    def to_dict(self) -> dict:
        obj = vars(self)
        if type(self.trust_info) is dict:
            obj["trust_info"] = self.trust_info
        else:
            obj["trust_info"] = self.trust_info.to_dict()
        obj["violations"] = [v.to_dict() for v in self.violations]
        return obj


class DbTrustInfo(BaseDatabaseModel):
    __tablename__ = "trust_info"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
    )
    trust: Mapped[int] = mapped_column(Integer)
    toxicity: Mapped[float] = mapped_column(Float)

    registration_date: Mapped[Optional[datetime.date]] = mapped_column(
        Date, nullable=True
    )
    nng_join_date: Mapped[datetime.date] = mapped_column(Date)

    odd_groups: Mapped[bool] = mapped_column(Boolean)
    closed_profile: Mapped[bool] = mapped_column(Boolean)
    has_photo: Mapped[bool] = mapped_column(Boolean)
    has_wall_posts: Mapped[bool] = mapped_column(Boolean)
    has_friends: Mapped[bool] = mapped_column(Boolean)
    verified: Mapped[bool] = mapped_column(Boolean)
    joined_test_group: Mapped[bool] = mapped_column(Boolean)
    activism: Mapped[bool] = mapped_column(Boolean)
    has_violation: Mapped[bool] = mapped_column(Boolean)
    had_violation: Mapped[bool] = mapped_column(Boolean)
    has_warning: Mapped[bool] = mapped_column(Boolean)
    had_warning: Mapped[bool] = mapped_column(Boolean)
    used_nng: Mapped[bool] = mapped_column(Boolean)
    joined_main_group: Mapped[bool] = mapped_column(Boolean)
    donate: Mapped[bool] = mapped_column(Boolean)
    last_updated: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    user: Mapped[DbUser] = relationship(
        back_populates="trust_info",
        cascade="save-update, merge, delete",
    )

    def to_dict(self) -> dict:
        return vars(self)


class DbViolation(BaseDatabaseModel):
    __tablename__ = "violations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.user_id"))
    type: Mapped[ViolationType] = mapped_column(Enum(ViolationType))
    group_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    priority: Mapped[Optional[BanPriority]] = mapped_column(
        Enum(BanPriority), nullable=True
    )
    complaint: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    watchdog_ref: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_ref: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    active: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    user: Mapped[DbUser] = relationship(
        back_populates="violations", cascade="save-update, merge, delete"
    )

    def to_dict(self) -> dict:
        return vars(self)
