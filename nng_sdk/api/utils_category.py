from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory


class GetCommentInfoPost(BaseModel):
    comment_link: str


class CommentInfo(BaseModel):
    id: int
    from_id: int
    date: int
    text: Optional[str]


class GetCommentInfoResponse(BaseModel):
    valid: bool
    is_nng: bool
    group_id: int
    normalized_link: Optional[str] = None
    object: Optional[CommentInfo] = None


class UtilsCategory(ApiCategory):
    def get_comment_info(self, link: str) -> GetCommentInfoResponse:
        return GetCommentInfoResponse.model_validate(
            self._post(f"utils/get_comment_info", {"comment_link": link})
        )
