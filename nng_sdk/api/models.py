from enum import Enum
from typing import Optional

from pydantic import BaseModel


class VkEvent(BaseModel):
    group_id: int
    type: str
    secret: Optional[str] = None
    object: Optional[dict] = None


class EditorLogType(Enum):
    editor_success = 0
    editor_fail_left_group = 1
    editor_fail = 2
    new_ban = 3


class EditorLog(BaseModel):
    user_id: int
    log_type: EditorLogType
    group_id: Optional[int] = None
