from onepasswordconnectsdk.models import Item, Field


class OpUser:
    user_id: int
    token: str

    def __init__(self, user_id: int, token: str):
        self.user_id = user_id
        self.token = token

    def to_item(self, default_vault_id: str) -> Item:
        item = Item(
            vault=default_vault_id,
            id=self.user_id,
            title=self.user_id,
            category="api_credential",
            tags=["vk/user"],
            fields=[
                Field("username", label="username", value=str(self.user_id)),
                Field("credential", label="credential", value=self.token),
            ],
        )

        return item
