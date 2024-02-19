from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbUserStats(BaseDatabaseModel):
    __tablename__ = "user_stats"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    users: Mapped[int] = mapped_column(Integer)
