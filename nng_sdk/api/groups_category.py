from nng_sdk.api.api_category import ApiCategory
from nng_sdk.pydantic_models.group import Group


class GroupsCategory(ApiCategory):
    def get_groups(self) -> list[Group]:
        return [Group.model_validate(i) for i in self._get("groups")]

    def get_group(self, group_id: int):
        return Group.model_validate(self._get(f"groups/{group_id}"))
