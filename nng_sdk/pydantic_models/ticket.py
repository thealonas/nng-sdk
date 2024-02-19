import datetime
from enum import StrEnum
from typing import Optional

from nng_sdk.pydantic_models.base_model import BaseNngModel


class TicketStatus(StrEnum):
    unreviewed = "unreviewed"
    in_review = "in_review"
    closed = "closed"


class TicketType(StrEnum):
    question = "question"
    new_feature = "new_feature"


class TicketMessage(BaseNngModel):
    author_admin: bool
    message_text: str
    attachments: list[str] = []
    added: datetime.datetime


class Ticket(BaseNngModel):
    ticket_id: int
    type: TicketType
    status: TicketStatus
    issuer: int
    dialog: list[TicketMessage]
    opened: datetime.datetime
    closed: Optional[datetime.datetime] = None

    def sort_dialogs(self):
        self.dialog.sort(key=lambda message: message.added)

    @property
    def is_closed(self):
        return self.status == TicketStatus.closed
