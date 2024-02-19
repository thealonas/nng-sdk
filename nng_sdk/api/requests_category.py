from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.request import RequestType, Request


class RequestWebsocketLog(BaseModel):
    request_id: int
    send_to_user: int


class PutRequest(BaseModel):
    request_type: RequestType
    user_id: int
    user_message: str
    vk_comment: Optional[str] = None


class PostRequest(BaseModel):
    answer: Optional[str] = None
    decision: bool
    answered: bool


class PostChangeRequestIntruder(BaseModel):
    new_intruder: int


class PutRequestResponse(BaseModel):
    response: str
    success: bool
    request_id: Optional[int] = None


class RequestsCategory(ApiCategory):
    def get_requests(self) -> list[Request]:
        return [Request.model_validate(i) for i in self._get("requests/list")]

    def get_user_requests(self, user_id: int) -> list[Request]:
        return [
            Request.model_validate(i) for i in self._get(f"requests/user/{user_id}")
        ]

    def change_request_intruder(self, request_id: int, new_intruder: int) -> Request:
        return Request.model_validate(
            self._post(
                f"requests/change_intruder/{request_id}",
                PostChangeRequestIntruder(new_intruder=new_intruder).dict(),
            )
        )

    def open_request(self, put_request: PutRequest) -> PutRequestResponse:
        return PutRequestResponse.model_validate(
            self._put("requests/open", put_request.dict())
        )

    def get_request(self, request_id: int) -> Request:
        req = self._get(f"requests/request/{request_id}")
        return Request.model_validate(req)
