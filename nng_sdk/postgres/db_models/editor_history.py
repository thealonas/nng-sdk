import datetime

from sqlalchemy import Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbEditorHistory(BaseDatabaseModel):
    __tablename__ = "editor_history"

    history_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)
    group_id: Mapped[int] = mapped_column(Integer)
    granted: Mapped[bool] = mapped_column(Boolean)
    date: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    wip: Mapped[bool] = mapped_column(Boolean)

    def to_dict(self) -> dict:
        return vars(self)
