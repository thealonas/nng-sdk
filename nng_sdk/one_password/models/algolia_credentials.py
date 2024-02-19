from pydantic import BaseModel


class AlgoliaCredentials(BaseModel):
    app_id: str
    api_key: str
    index_name: str
