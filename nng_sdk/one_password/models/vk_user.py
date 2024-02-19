from pydantic import BaseModel


class VkUser(BaseModel):
    phone: str
    password: str
    totp: str
