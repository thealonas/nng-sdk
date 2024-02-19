from nng_sdk.pydantic_models.base_model import BaseNngModel


class Group(BaseNngModel):
    group_id: int
    screen_name: str
