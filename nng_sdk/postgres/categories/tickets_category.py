import datetime

from sqlalchemy import update, select, or_

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.ticket import DbTicket, DbTicketMessage, TicketStatus
from nng_sdk.postgres.exceptions import ItemNotFoundException
from nng_sdk.pydantic_models.ticket import Ticket, TicketMessage, TicketType


class TicketsCategory(DbCategory):
    def upload_or_update_ticket(self, ticket: Ticket) -> Ticket:
        with self.begin_session() as session:
            existing_ticket = (
                session.query(DbTicket)
                .filter(DbTicket.ticket_id == ticket.ticket_id)
                .all()
            )

            if existing_ticket:
                ticket_dict = vars(ticket)
                ticket_id = ticket.ticket_id
                del ticket_dict["ticket_id"]
                del ticket_dict["dialog"]

                session.execute(
                    update(DbTicket)
                    .filter(DbTicket.ticket_id == ticket_id)
                    .values(ticket_dict)
                )
            else:
                db_ticket = DbTicket(
                    type=ticket.type,
                    status=ticket.status,
                    issuer=ticket.issuer,
                    opened=ticket.opened,
                    closed=ticket.closed,
                )
                session.add(db_ticket)
                session.commit()

                session.refresh(db_ticket)
                ticket_id = db_ticket.ticket_id

                ticket.sort_dialogs()

                for message in ticket.dialog:
                    session.add(
                        DbTicketMessage(
                            ticket_id=ticket_id,
                            author_admin=message.author_admin,
                            message_text=message.message_text,
                            attachments=message.attachments,
                            added=message.added,
                        )
                    )

            session.commit()

            return Ticket.model_validate(
                session.query(DbTicket)
                .where(DbTicket.ticket_id == ticket_id)
                .first()
                .to_dict()
            )

    def get_ticket(self, ticket_id: int) -> Ticket:
        with self.begin_session() as session:
            ticket = (
                session.query(DbTicket)
                .where(DbTicket.ticket_id == ticket_id)
                .join(DbTicketMessage)
                .all()
            )

            if not ticket:
                raise ItemNotFoundException("Ticket not found")

            return Ticket.model_validate(ticket[0].to_dict())

    def get_all_tickets(self) -> list[Ticket]:
        with self.begin_session() as session:
            query = select(DbTicket).join(DbTicketMessage)
            result = list(session.scalars(query).unique())
            return [Ticket.model_validate(i.to_dict()) for i in result]

    def get_user_tickets(self, user_id: int) -> list[Ticket]:
        with self.begin_session() as session:
            query = (
                select(DbTicket)
                .where(DbTicket.issuer == user_id)
                .where(DbTicket.type == TicketType.question)
                .join(DbTicketMessage)
            )

            user_tickets = list(session.scalars(query).unique())
            return [Ticket.model_validate(i.to_dict()) for i in user_tickets]

    def get_opened_tickets(self) -> list[Ticket]:
        with self.begin_session() as session:
            query = (
                select(DbTicket)
                .join(DbTicketMessage)
                .where(
                    or_(
                        DbTicket.status == TicketStatus.unreviewed,
                        DbTicket.status == TicketStatus.in_review,
                    )
                )
            )

            opened_tickets = list(session.scalars(query).unique())
            return [Ticket.model_validate(i.to_dict()) for i in opened_tickets]

    def add_message(self, ticket_id: int, message: TicketMessage):
        with self.begin_session() as session:
            session.add(
                DbTicketMessage(
                    ticket_id=ticket_id,
                    author_admin=message.author_admin,
                    message_text=message.message_text,
                    attachments=message.attachments,
                    added=message.added or datetime.date.today(),
                )
            )

            session.commit()
