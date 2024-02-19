import logging
from typing import Any

from vk_api import VkApi
from vk_api.vk_api import VkApiMethod

from nng_sdk.logger import get_logger
from nng_sdk.one_password.op_connect import OpConnect


class VkManager:
    VK_VERSION = "5.199"

    logging = get_logger()
    op_connect: OpConnect = OpConnect()
    api: VkApiMethod = None
    bot: VkApiMethod = None

    @staticmethod
    def get_token_user_id(access_token: str) -> int | None:
        session = VkApi(token=access_token, api_version=VkManager.VK_VERSION)
        users = session.get_api().users.get()
        if not users:
            return None

        return users[0]["id"]

    def auth_in_vk(self, captcha_solver: Any | None = None):
        logging.info("пытаюсь авторизоваться в API ВКонтакте")
        token = self.op_connect.get_main_user_token()
        logging.info(f"получил токен главного пользователя из 1Password")

        if captcha_solver is not None:
            logging.info("сервис использует хэндлер каптчи")
            session = VkApi(
                token=token, captcha_handler=captcha_solver, api_version=self.VK_VERSION
            )
        else:
            session = VkApi(token=token, api_version=self.VK_VERSION)

        self.api = session.get_api()

    def auth_in_bot(self):
        logging.info("пытаюсь авторизоваться в API ВКонтакте как бот")
        bot_group = self.op_connect.get_bot_group()
        session = VkApi(token=bot_group.token, api_version=self.VK_VERSION)
        self.bot = session.get_api()

    def get_executable_bot(self):
        return self.bot

    def get_executable_api(self):
        return self.api

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(VkManager, cls).__new__(cls)
        return cls.instance
