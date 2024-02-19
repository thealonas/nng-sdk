import datetime

from sqlalchemy import Integer, DateTime, Text, ARRAY, Float
from sqlalchemy.orm import Mapped, mapped_column

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class DbComment(BaseDatabaseModel):
    __tablename__ = "comments"

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer)
    target_group_id: Mapped[int] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(Integer)
    post_id: Mapped[int] = mapped_column(Integer)
    comment_vk_id: Mapped[int] = mapped_column(Integer)
    posted_on: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    text: Mapped[str] = mapped_column(Text, nullable=True)
    attachments: Mapped[list[str]] = mapped_column(ARRAY(Text))
    toxicity: Mapped[float] = mapped_column(Float)

    def to_dict(self) -> dict:
        return vars(self)
