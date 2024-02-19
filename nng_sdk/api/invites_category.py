from enum import Enum
from typing import Optional

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.user import User


class UseInviteResponseType(Enum):
    invalid_or_banned_referral = 0
    invalid_user = 1
    banned_user = 2
    user_already_invited = 3
    cannot_invite_yourself = 4
    user_is_invited_by_you = 5
    success = 6
    too_low_trust = 7
    too_low_trust_referral = 8


class UseInviteResponse(BaseModel):
    response_type: UseInviteResponseType
    referral_id: Optional[int] = None


class InvitesCategory(ApiCategory):
    def get_users_invited_by_referral(self, user_id: int) -> list[User]:
        return [
            User.model_validate(i) for i in self._get(f"invites/referral/{user_id}")
        ]

    def get_my_code(self, user_id: int) -> str:
        return self._get(f"invites/get_my_code/{user_id}")["code"]

    def use_invite(self, invite: str, user_id: int) -> UseInviteResponse:
        return UseInviteResponse.model_validate(
            self._post("invites/use", {"invite_string": invite, "user": user_id})
        )
