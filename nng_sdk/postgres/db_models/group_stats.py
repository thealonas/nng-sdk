from sqlalchemy import Integer, Date, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbGroupStats(BaseDatabaseModel):
    __tablename__ = "group_stats"

    id = mapped_column(Integer, primary_key=True)
    date = mapped_column(Date, index=True)
    total_users = mapped_column(Integer)
    total_managers = mapped_column(Integer)
    stats = mapped_column(ARRAY(JSONB))

    def to_dict(self) -> dict:
        return vars(self)
