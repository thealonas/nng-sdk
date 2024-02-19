from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbSus(BaseDatabaseModel):
    __tablename__ = "sus"

    id: Mapped[int] = mapped_column(primary_key=True)
