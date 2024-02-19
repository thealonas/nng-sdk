import datetime
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.ticket import TicketType, TicketStatus, Ticket


class PutTicket(BaseModel):
    user_id: int
    type: TicketType
    text: str
    attachments: list[str] = []


class UpdateTicketStatus(BaseModel):
    status: TicketStatus


class UploadMessage(BaseModel):
    author_admin: bool
    message_text: str
    attachments: Optional[list[str]] = None


class PostAlgoliaQuery(BaseModel):
    query: str


class AlgoliaOutput(BaseModel):
    question: str
    answer: str
    attachment: Optional[str] = None
    action: Optional[list] = None


class TicketShort(BaseModel):
    ticket_id: int
    type: TicketType
    issuer: int
    opened: datetime.datetime


class TicketLogType(IntEnum):
    updated_status = 0
    admin_added_message = 1
    user_added_message = 2


class TicketWebsocketLog(BaseModel):
    log_type: TicketLogType
    ticket_id: int


class TicketsCategory(ApiCategory):
    def algolia_search(self, query: str) -> list[AlgoliaOutput]:
        return [
            AlgoliaOutput.model_validate(i)
            for i in self._post("tickets/algolia", vars(PostAlgoliaQuery(query=query)))
        ]

    def update_status(self, ticket_id: str, status: TicketStatus, silent: bool = False):
        return self._post(
            f"tickets/ticket/{ticket_id}/update/status?silent={silent}",
            vars(UpdateTicketStatus(status=status)),
        )

    def add_message(self, ticket_id: str, message: UploadMessage):
        return self._post(
            f"tickets/ticket/{ticket_id}/update/add_message", vars(message)
        )

    def add_ticket(self, ticket: PutTicket) -> Ticket:
        return Ticket.model_validate(self._put("tickets/upload", vars(ticket)))

    def get_user_tickets(self, user_id: int) -> list[TicketShort]:
        return [
            TicketShort.model_validate(i) for i in self._get(f"tickets/user/{user_id}")
        ]

    def get_ticket(self, ticket_id: str) -> Ticket:
        return Ticket.model_validate(self._get(f"tickets/ticket/{ticket_id}"))
