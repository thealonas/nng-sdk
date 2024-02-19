import datetime

from sqlalchemy import Integer, Enum, Date, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel
from nng_sdk.postgres.db_models.users import BanPriority


class DbWatchdog(BaseDatabaseModel):
    __tablename__ = "watchdog"

    watchdog_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    intruder: Mapped[int] = mapped_column(Integer, nullable=True)
    victim: Mapped[int] = mapped_column(Integer, nullable=True)
    group_id: Mapped[int] = mapped_column(Integer)
    priority: Mapped[BanPriority] = mapped_column(Enum(BanPriority))
    date: Mapped[datetime.date] = mapped_column(Date)
    reviewed: Mapped[bool] = mapped_column(Boolean)

    def to_dict(self) -> dict:
        return {
            "watchdog_id": self.watchdog_id,
            "intruder": self.intruder,
            "victim": self.victim,
            "group_id": self.group_id,
            "priority": self.priority,
            "date": self.date,
            "reviewed": self.reviewed,
        }
