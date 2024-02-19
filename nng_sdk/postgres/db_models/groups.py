from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbGroup(BaseDatabaseModel):
    __tablename__ = "groups"

    group_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    screen_name: Mapped[str] = mapped_column(Text)

    def to_dict(self) -> dict:
        return vars(self)
