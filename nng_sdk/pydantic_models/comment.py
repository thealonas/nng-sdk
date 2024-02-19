import datetime
from typing import Optional

from nng_sdk.pydantic_models.base_model import BaseNngModel


class Comment(BaseNngModel):
    comment_id: int = -1
    target_group_id: int
    group_id: int
    post_id: int
    author_id: int
    comment_vk_id: int
    posted_on: datetime.datetime
    text: Optional[str] = None
    attachments: list[str] = []
    toxicity: float = 0
