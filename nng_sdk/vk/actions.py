import asyncio
import json
import random
from typing import Callable

import vk_api.exceptions
from vk_api import VkApiError, ApiError

from nng_sdk.logger import get_logger
from nng_sdk.vk.vk_manager import VkManager

__vk = VkManager()

ban_comment = "Блокировка после решения Администрации | Подробнее: https://vk.me/nnghub"


class GroupDataResponse:
    group_id: int
    members_count: int
    managers_count: int
    managers: list[dict]

    def __init__(
        self, group_id: int, members: int, managers_count: int, managers: list[dict]
    ):
        self.group_id = group_id
        self.members_count = members
        self.managers_count = managers_count
        self.managers = managers


class GroupIdentityResponse:
    id: int
    name: str
    screen_name: str
    photo_200: str

    def __init__(self, id: int, name: str, screen_name: str, photo_200: str):
        self.id = id
        self.name = name
        self.screen_name = screen_name
        self.photo_200 = photo_200


def vk_exception_handler(_: Exception):
    pass


def rate_limit_handler():
    asyncio.run(asyncio.sleep(60 * 60))


def captcha_handler():
    asyncio.run(asyncio.sleep(60))


def vk_action(action: Callable[..., any]) -> Callable[..., any]:
    pass_by_exception_messages = ["can't send messages for users without permission"]

    def wrapper(*args, **kwargs):
        try:
            return action(*args, **kwargs)
        except ApiError as e:
            error_message = e.error.get("error_msg")
            if not error_message:
                raise

            error_message = error_message.lower()

            if error_message in pass_by_exception_messages:
                return

            if error_message == "rate limit reached":
                get_logger().info("первышен лимит запросов, ожидаю...")
                rate_limit_handler()
                return wrapper(*args, **kwargs)

        except vk_api.exceptions.Captcha:
            get_logger().info("каптча, ожидаю...")
            captcha_handler()
            return wrapper(*args, **kwargs)
        except Exception as e:
            vk_exception_handler(e)
            raise

    return wrapper


@vk_action
def get_groups_data(groups: list[int]) -> dict[int, GroupDataResponse]:
    groups_bunched_by_12 = [groups[i : i + 12] for i in range(0, len(groups), 12)]

    vk_result = []

    for group_ids in groups_bunched_by_12:
        groups_parameter = ",".join(map(str, group_ids))
        results = __vk.api.execute.newGetMembersInGroups(groups=groups_parameter)

        for result in results:
            vk_result.append(result)

    output: dict[int, GroupDataResponse] = {}

    for group in vk_result:
        output[group["id"]] = GroupDataResponse(
            group_id=group["id"],
            members=group["members"],
            managers_count=group["admins"],
            managers=group["admins_items"],
        )

    return output


@vk_action
def get_groups_identity(group_ids: list[int]) -> list[GroupIdentityResponse]:
    groups_bunched_by_25 = [group_ids[i : i + 25] for i in range(0, len(group_ids), 25)]
    vk_result = []
    for groups_chunk in groups_bunched_by_25:
        groups_parameter = ",".join(map(str, groups_chunk))
        results = __vk.api.execute.getGroupsIdentity(group_ids=groups_parameter)
        for result in results:
            vk_result.append(result)

    output: list[GroupIdentityResponse] = []

    for group in vk_result:
        output.append(
            GroupIdentityResponse(
                id=group["id"],
                name=group["name"],
                screen_name=group["screen_name"],
                photo_200=group["photo_200"],
            )
        )

    return output


@vk_action
def get_groups_statuses(groups: list[int]) -> dict[int, str]:
    result: list[dict] = __vk.api.execute.getGroupsStatus(
        groups=",".join(map(str, groups))
    )
    return {group["id"]: group["status"] for group in result}


@vk_action
def get_user_data(user_id: int) -> dict:
    return __vk.api.users.get(user_ids=[user_id])[0]


@vk_action
def get_all_banned(group: int) -> list[dict]:
    return __vk.api.execute.getAllBanned(group=group)


@vk_action
def get_all_managers(group: int) -> list[dict]:
    return __vk.api.groups.getMembers(
        group_id=group, count=1000, filter="managers", fields="sex"
    )["items"]


@vk_action
def _get_users_data(users: list[int]) -> list[dict]:
    return __vk.api.execute.getUsers(user_ids=",".join(map(str, users)))


def get_users_data(users: list[int]) -> list[dict]:
    users_bunched_by_25000 = [
        users[i : i + 25000]
        for i in range(0, len(users), 25000)
        if len(users[i : i + 25000]) > 0
    ]

    data: list[dict] = []

    for users_chunk in users_bunched_by_25000:
        users_data = _get_users_data(users=users_chunk)

        for user_data in users_data:
            data.append(user_data)

    return data


@vk_action
def set_statuses(groups: list[int], text: str):
    groups_bunched_by_25 = [groups[i : i + 25] for i in range(0, len(groups), 25)]
    for groups_chunk in groups_bunched_by_25:
        __vk.api.execute.newSetGroupsStatuses(
            groups=",".join(map(str, groups_chunk)), text=text
        )


@vk_action
def delete_photo(group_id: int, photo_id: int):
    __vk.api.execute.watchdogProcessPhoto(group=group_id, photo=photo_id)


@vk_action
def delete_post(group_id: int, post_id: int):
    __vk.api.execute.watchdogProcessPost(group=group_id, post=post_id)


@vk_action
def edit_manager(group_id: int, user_id: int, role: str | None = None):
    __vk.api.groups.editManager(
        group_id=group_id, user_id=user_id, role=role, is_contact=False
    )


@vk_action
def send_message(
    user_id: int,
    text: str | None = None,
    keyboard: str | None = None,
    sticker_id: int | None = None,
    attachment: str | None = None,
    dont_parse_links: bool | None = True,
):
    random_id = random.randint(0, 2**32)
    __vk.bot.messages.send(
        peer_id=user_id,
        random_id=random_id,
        message=text,
        keyboard=keyboard,
        sticker_id=sticker_id,
        attachment=attachment,
        dont_parse_links=1 if dont_parse_links else 0,
    )


@vk_action
def delete_message(
    message_id: int,
    peer_id: int,
    error_callback: Callable[[VkApiError], None] | None = None,
):
    try:
        __vk.bot.messages.delete(
            message_ids=str(message_id), delete_for_all=1, peer_id=peer_id
        )
    except VkApiError as e:
        if error_callback:
            error_callback(e)
        else:
            raise


@vk_action
def send_long_message(
    peer_id: int,
    long_text: str,
    keyboard: str | None = None,
):
    text_split_by_4095_symbols = [
        long_text[i : i + 4095] for i in range(0, len(long_text), 4095)
    ]

    for index, text_chunk in enumerate(text_split_by_4095_symbols):
        if index - 1 == len(text_split_by_4095_symbols):
            send_message(peer_id, text_chunk, keyboard)
            return

        send_message(peer_id, text_chunk)


@vk_action
def edit_message(
    peer_id: int,
    new_message_text: str,
    conversation_message_id: int,
    keyboard: str | None = None,
    delete_message_error_callback: Callable[[VkApiError], None] | None = None,
    dont_parse_links: bool | None = True,
):
    try:
        __vk.bot.messages.edit(
            peer_id=peer_id,
            message=new_message_text,
            conversation_message_id=conversation_message_id,
            keyboard=keyboard,
            dont_parse_links=1 if dont_parse_links else 0,
        )
    except VkApiError:
        delete_message(conversation_message_id, peer_id, delete_message_error_callback)
        send_message(peer_id, new_message_text, keyboard)


@vk_action
def get_by_conversation_message_id(peer_id: int, conversation_message_id: int):
    return __vk.bot.messages.getByConversationMessageId(
        peer_id=peer_id, conversation_message_ids=str(conversation_message_id)
    )["items"][0]


@vk_action
def send_message_event_answer(
    event_id: str,
    user_id: int,
    peer_id: int,
    event_data: dict | None = None,
):
    __vk.bot.messages.sendMessageEventAnswer(
        event_id=event_id,
        user_id=user_id,
        peer_id=peer_id,
        event_data=json.dumps(event_data),
    )


@vk_action
def ban_editor(group_id: int, user_id: int):
    __vk.api.execute.watchdogBanEditor(
        group=group_id, user=user_id, banComment=ban_comment
    )


@vk_action
def get_wall_posts(group: int) -> list[dict]:
    return __vk.api.execute.getAllPosts(group=group)["items"]


@vk_action
def delete_posts(group: int, posts: list[int]):
    posts_bunched_by_25 = [posts[i : i + 25] for i in range(0, len(posts), 25)]
    for posts_chunk in posts_bunched_by_25:
        __vk.api.execute.deleteAllPosts(
            group=group, posts=",".join(map(str, posts_chunk))
        )


@vk_action
def get_last_post(group: int) -> dict:
    return __vk.api.wall.get(owner_id=-group, count=1)["items"][0]


@vk_action
def repost(wall: str, group_id: int):
    __vk.api.wall.repost(object=wall, group_id=group_id)


@vk_action
def unban_users(users: list[int], group: int):
    __vk.api.execute.unbanUsers(users=",".join(map(str, users)), group=group)


@vk_action
def is_in_group(user_id: int, group_id: int) -> bool:
    return bool(__vk.api.groups.isMember(group_id=group_id, user_id=user_id))


@vk_action
def get_photo_upload_server(owner_id: int) -> str:
    return __vk.api.photos.getOwnerPhotoUploadServer(owner_id=owner_id)["upload_url"]


@vk_action
def save_owner_photo(hash_value: str, photo: str, server: str) -> dict:
    return __vk.api.photos.saveOwnerPhoto(hash=hash_value, photo=photo, server=server)


@vk_action
def get_comment(
    owner_id: int, comment_id: int, extended: int = 0, fields: str = ""
) -> dict:
    answer = __vk.api.wall.getComment(
        owner_id=owner_id, comment_id=comment_id, extended=extended, fields=fields
    )
    return answer["items"][0]


@vk_action
def groups_ban(group_id: int, owner_id: int):
    __vk.api.groups.ban(
        group_id=group_id, owner_id=owner_id, comment=ban_comment, comment_visible=1
    )


@vk_action
def __ban_users_chunk(group, users):
    __vk.api.execute.banUsers(
        group=group, users=",".join(map(str, users)), comment=ban_comment
    )


@vk_action
def ban_users(group: int, users: list[int]):
    users_bunched_by_25 = [users[i : i + 25] for i in range(0, len(users), 25)]
    for users_chunk in users_bunched_by_25:
        __ban_users_chunk(group, users_chunk)


@vk_action
def get_members(group: int) -> list[dict]:
    answer = __vk.api.execute.newGetMembers(group=group)
    return answer["users"]


@vk_action
def tick_online_as_user(group_id: int):
    __vk.api.groups.enableOnline(group_id=group_id)
