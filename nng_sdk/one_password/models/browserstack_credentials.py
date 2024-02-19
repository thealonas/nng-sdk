from pydantic import BaseModel


class BrowserStackCredentials(BaseModel):
    login: str
    api_key: str
