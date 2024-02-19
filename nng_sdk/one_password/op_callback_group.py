from typing import Optional

from onepasswordconnectsdk.models import Item, Field


class OpCallbackGroup:
    group_id: int
    secret: str
    confirm: str
    token: Optional[str] = None

    def __init__(
        self, group_id: int, secret: str, confirm: str, token: str | None = None
    ):
        self.group_id = group_id
        self.secret = secret
        self.confirm = confirm
        self.token = token

    def to_item(self, default_vault_id: str) -> Item:
        item = Item(
            vault=default_vault_id,
            id=self.group_id,
            title=self.group_id,
            category="api_credential",
            tags=["vk/callback"],
            fields=[
                Field("username", label="username", value=str(self.group_id)),
                Field("credential", label="credential", value=self.secret),
                Field("confirm", label="confirm", value=self.confirm),
            ],
        )

        return item
