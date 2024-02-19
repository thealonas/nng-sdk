from urllib.error import HTTPError

from onepasswordconnectsdk.client import (
    Client,
    new_client_from_environment,
    FailedToRetrieveItemException,
)

from nng_sdk.one_password.models.algolia_credentials import AlgoliaCredentials
from nng_sdk.one_password.models.browserstack_credentials import BrowserStackCredentials
from nng_sdk.one_password.models.vk_client import VkClient
from nng_sdk.one_password.models.vk_user import VkUser
from nng_sdk.one_password.op_callback_group import OpCallbackGroup


class OpConnect:
    default_vault_id: str
    client: Client

    def get_items_by_filter(self, item_filter: str):
        url = f"/v1/vaults/{self.default_vault_id}/items?filter={item_filter}"
        response = self.client.build_request("GET", url)
        try:
            response.raise_for_status()
        except HTTPError:
            raise FailedToRetrieveItemException(
                f"Unable to retrieve items. Received {response.status_code} \
                             for {url} with message: {response.json().get('message')}"
            )

        return self.client.deserialize(response.content, "list[SummaryItem]")

    def get_callback_group(self, group_id: int) -> OpCallbackGroup:
        all_groups = self.get_items_by_filter('tag eq "vk/callback"')
        for group in all_groups:
            if int(group.title) != group_id:
                continue
            item = self.client.get_item_by_id(group.id, self.default_vault_id)
            return OpCallbackGroup(
                group_id=int(group.title),
                secret=self.unpack_field(item.fields, "credential"),
                confirm=self.unpack_field(item.fields, "confirm"),
            )

    @staticmethod
    def update_group_callback_fields(item, secret: str, confirm: str):
        for field in item.fields:
            if field.label == "credential":
                field.value = secret

            if field.label == "confirm":
                field.value = confirm

        return item

    def update_callback_group(self, group_id: int, secret: str, confirm: str):
        all_groups = self.get_items_by_filter('tag eq "vk/callback"')
        for group in all_groups:
            if int(group.title) != group_id:
                continue

            item = self.client.get_item_by_id(group.id, self.default_vault_id)
            item = self.update_group_callback_fields(item, secret, confirm)

            self.client.update_item(
                item.id,
                self.default_vault_id,
                item,
            )

    def get_bot_group(self) -> OpCallbackGroup:
        preview_item = self.get_items_by_filter('tag eq "vk/callback/bot"')[0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return OpCallbackGroup(
            group_id=int(preview_item.title),
            secret=self.unpack_field(item.fields, "credential"),
            confirm=self.unpack_field(item.fields, "confirm"),
            token=self.unpack_field(item.fields, "token"),
        )

    def get_main_user_token(self) -> str:
        preview_item = self.get_items_by_filter('tag eq "vk/user/main"')[0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return self.unpack_field(item.fields, "credential")

    def _get_vk_client(self, name: str):
        preview_item = [
            i for i in self.get_items_by_filter('tag eq "vk/client"') if i.title == name
        ][0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return VkClient(
            client_id=self.unpack_field(item.fields, "username"),
            client_secret=self.unpack_field(item.fields, "credential"),
        )

    def get_vk_client(self) -> VkClient:
        return self._get_vk_client("client")

    def get_perspective_api(self) -> str:
        return self.get_other("perspective")

    def get_vk_admin_client(self) -> VkClient:
        preview_item = self.get_items_by_filter('tag eq "vk/admin-client"')[0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return VkClient(
            client_id=self.unpack_field(item.fields, "username"),
            client_secret=self.unpack_field(item.fields, "credential"),
        )

    def get_browserstack_credentials(self) -> BrowserStackCredentials:
        all_other = self.get_items_by_filter('tag eq "other"')
        for other in all_other:
            if other.title != "browserstack":
                continue
            item = self.client.get_item_by_id(other.id, self.default_vault_id)
            return BrowserStackCredentials(
                login=self.unpack_field(item.fields, "username"),
                api_key=self.unpack_field(item.fields, "credential"),
            )

    def get_scraper_user(self) -> VkUser:
        preview_item = self.get_items_by_filter('tag eq "vk/user/scraper"')[0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return VkUser(
            phone=self.unpack_field(item.fields, "username"),
            password=self.unpack_field(item.fields, "password"),
            totp=self.unpack_field(item.fields, "one-time password"),
        )

    def get_second_user_token(self) -> str:
        preview_item = self.get_items_by_filter(
            'tag eq "vk/user" and tag eq "vk/user/second"'
        )[0]
        item = self.client.get_item_by_id(preview_item.id, self.default_vault_id)
        return self.unpack_field(item.fields, "credential")

    def __init__(self):
        self.auth()
        self.set_default_vault_id()

    @staticmethod
    def unpack_field(supply: list[{}], target: str) -> any:
        for item in supply:
            if item.label != target:
                continue
            return item.value
        return None

    def get_token(self, user_id: int) -> str:
        all_tokens = self.get_items_by_filter('tag eq "vk/user"')
        for token in all_tokens:
            if int(token.title) != user_id:
                continue
            item = self.client.get_item_by_id(token.id, self.default_vault_id)
            return self.unpack_field(item.fields, "credential")

    def get_algolia_credentials(self) -> AlgoliaCredentials:
        all_other = self.get_items_by_filter('tag eq "other"')
        algolia_credentials = None
        for other in all_other:
            if other.title != "algolia":
                continue
            algolia_credentials = self.client.get_item_by_id(
                other.id, self.default_vault_id
            )
            break

        if not algolia_credentials:
            raise FailedToRetrieveItemException(
                "Unable to retrieve algolia credentials"
            )

        return AlgoliaCredentials(
            app_id=self.unpack_field(algolia_credentials.fields, "username"),
            api_key=self.unpack_field(algolia_credentials.fields, "credential"),
            index_name=self.unpack_field(algolia_credentials.fields, "index"),
        )

    def get_broadcast_token(self) -> str:
        all_other = self.get_items_by_filter('tag eq "other"')
        for other in all_other:
            if other.title != "broadcast":
                continue
            broadcast = self.client.get_item_by_id(other.id, self.default_vault_id)
            return self.unpack_field(broadcast.fields, "credential")

    def get_invites_salt(self) -> str:
        all_other = self.get_items_by_filter('tag eq "other"')
        for other in all_other:
            if other.title != "invitesalt":
                continue

            salt = self.client.get_item_by_id(other.id, self.default_vault_id)
            return self.unpack_field(salt.fields, "credential")

    def get_other(self, element_title: str, target_field: str = "credential") -> str:
        all_other = self.get_items_by_filter('tag eq "other"')
        for other in all_other:
            if other.title != element_title:
                continue
            item = self.client.get_item_by_id(other.id, self.default_vault_id)
            return self.unpack_field(item.fields, target_field)

    def auth(self):
        self.client = new_client_from_environment()

    def set_default_vault_id(self, vault_id: str | None = None):
        if vault_id:
            self.default_vault_id = vault_id
            return

        self.default_vault_id = self.client.get_vaults()[0].id

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(OpConnect, cls).__new__(cls)
        return cls.instance
