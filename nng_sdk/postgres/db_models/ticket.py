import datetime
from enum import StrEnum

from sqlalchemy import Boolean, Integer, Text, ARRAY, DateTime, Enum, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class TicketStatus(StrEnum):
    unreviewed = "unreviewed"
    in_review = "in_review"
    closed = "closed"


class TicketType(StrEnum):
    question = "question"
    new_feature = "new_feature"


class DbTicketMessage(BaseDatabaseModel):
    __tablename__ = "ticket_messages"

    message_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(Integer, ForeignKey("tickets.ticket_id"))
    author_admin: Mapped[bool] = mapped_column(Boolean)
    message_text: Mapped[str] = mapped_column(Text)
    attachments: Mapped[list[str]] = mapped_column(ARRAY(Text))
    added: Mapped[datetime.datetime] = mapped_column(DateTime)

    ticket: Mapped["DbTicket"] = relationship(
        "DbTicket",
        back_populates="dialog",
    )

    def to_dict(self) -> dict:
        return vars(self)


class DbTicket(BaseDatabaseModel):
    __tablename__ = "tickets"

    ticket_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[TicketType] = mapped_column(Enum(TicketType))
    status: Mapped[TicketStatus] = mapped_column(Enum(TicketStatus))
    issuer: Mapped[int] = mapped_column(Integer)
    dialog: Mapped[list["DbTicketMessage"]] = relationship(
        "DbTicketMessage", back_populates="ticket"
    )

    opened: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    closed: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    def to_dict(self) -> dict:
        obj = vars(self)
        obj["dialog"] = [m.to_dict() for m in self.dialog]
        return obj
