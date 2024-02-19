from pydantic import BaseModel


class VkClient(BaseModel):
    client_id: int
    client_secret: str
