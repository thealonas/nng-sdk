import datetime

from sqlalchemy import update

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.request import DbRequest
from nng_sdk.postgres.exceptions import ItemNotFoundException
from nng_sdk.pydantic_models.request import Request


class RequestsCategory(DbCategory):
    def get_request(self, request_id: int) -> Request:
        with self.begin_session() as session:
            requests = (
                session.query(DbRequest)
                .filter(DbRequest.request_id == request_id)
                .all()
            )

            if not requests:
                raise ItemNotFoundException(f"Request {request_id} not found")

            return Request.model_validate(requests[0].to_dict())

    def get_all_requests(self) -> list[Request]:
        with self.begin_session() as session:
            requests = session.query(DbRequest).all()
            return [Request.model_validate(i.to_dict()) for i in requests]

    def get_all_unanswered_requests(self) -> list[Request]:
        with self.begin_session() as session:
            requests = (
                session.query(DbRequest).filter(DbRequest.answered == False).all()
            )
            return [Request.model_validate(i.to_dict()) for i in requests]

    def upload_or_update_request(self, request: Request) -> Request:
        with self.begin_session() as session:
            request_with_id = (
                session.query(DbRequest)
                .filter(DbRequest.request_id == request.request_id)
                .first()
            )

            if request_with_id:
                request_id = request_with_id.request_id
                request_model = Request.model_validate(request_with_id.to_dict())
                values = vars(request)
                del values["request_id"]
                session.execute(
                    update(DbRequest)
                    .filter(DbRequest.request_id == request_id)
                    .values(values)
                )
                session.commit()
                return request_model

            new_request = DbRequest(
                request_type=request.request_type,
                created_on=request.created_on or datetime.date.today(),
                user_id=request.user_id,
                user_message=request.user_message,
                vk_comment=request.vk_comment,
                answer=request.answer,
                decision=request.decision,
                answered=request.answered,
            )

            session.add(new_request)
            session.commit()
            session.refresh(new_request)

            return Request.model_validate(new_request.to_dict())

    def get_user_requests(self, user_id: int) -> list[Request]:
        with self.begin_session() as session:
            requests = (
                session.query(DbRequest).filter(DbRequest.user_id == user_id).all()
            )

            return [Request.model_validate(i.to_dict()) for i in requests]
