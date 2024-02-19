import datetime

from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbStartup(BaseDatabaseModel):
    __tablename__ = "startups"

    service_name: Mapped[str] = mapped_column(Text, primary_key=True)
    time_log: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

    def to_dict(self) -> dict:
        return vars(self)
