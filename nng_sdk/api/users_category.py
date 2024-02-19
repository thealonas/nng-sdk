from typing import Optional, List

from pydantic import BaseModel

from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.user import Violation, TrustInfo, User


class BannedOutput(BaseModel):
    user_id: int
    name: str
    violations: List[Violation]

    def has_active_violation(self):
        return any(violation.active for violation in self.violations)


class ThxOutput(BaseModel):
    user_id: int
    name: str


class UserPut(BaseModel):
    user_id: int
    name: Optional[str] = None


class UserPost(BaseModel):
    name: Optional[str] = None
    admin: Optional[bool] = None
    groups: Optional[List[int]] = None
    violations: Optional[List[Violation]] = None
    trust_info: Optional[TrustInfo] = None


class UsersCategory(ApiCategory):
    def get_bnnd(self) -> list[BannedOutput]:
        return [BannedOutput.model_validate(i) for i in self._get("users/bnnd")]

    def get_thx(self) -> list[ThxOutput]:
        return [ThxOutput.model_validate(i) for i in self._get("users/thx")]

    def get_user(self, user_id: int) -> User:
        return User.model_validate(self._get(f"users/user/{user_id}"))

    def add_user(self, user_id: int, user_name: Optional[str] = None):
        data = {"user_id": user_id}
        if user_name is not None:
            data["user_name"] = user_name

        self._put(f"users/add", data)

    def post_user(self, user_id: int, data: UserPost):
        self._post(f"users/update/{user_id}", data.model_dump(mode="json"))

    def add_violation(self, user_id: int, data: Violation):
        self._post(f"users/add_violation/{user_id}", data.model_dump(mode="json"))

    def unban_user(self, user_id: int):
        self._post(f"users/unban/{user_id}", {})

    def get_groups_limit(self, user_id: int) -> int:
        return self._get(f"users/group_limit/{user_id}")["max_groups"]
