from enum import Enum
from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory


class OperationStatus(Enum):
    join_group = 0
    success = 1
    fail = 2
    cooldown = 3


class GiveEditorResponse(BaseModel):
    status: OperationStatus
    argument: Optional[str] = None


class EditorCategory(ApiCategory):
    def give_editor(self, user_id: int) -> GiveEditorResponse:
        response = self._post("editor/give", {"user_id": user_id})
        return GiveEditorResponse.model_validate(response)
