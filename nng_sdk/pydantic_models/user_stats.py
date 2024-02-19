import datetime

from nng_sdk.pydantic_models.base_model import BaseNngModel


class UserStats(BaseNngModel):
    year: str
    users: int

    @property
    def date(self) -> datetime.date:
        year, month = self.year.split("-")
        return datetime.date(int(year), int(month), 1)

    class Meta:
        model_key_prefix = "stats"
