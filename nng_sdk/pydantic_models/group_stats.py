import datetime

from nng_sdk.pydantic_models.base_model import BaseNngModel


class GroupStat(BaseNngModel):
    group_id: int
    members_count: int
    managers_count: int

    def to_dict(self) -> dict:
        return vars(self)


class GroupStats(BaseNngModel):
    date: datetime.date
    stats: list[GroupStat]
    total_users: int
    total_managers: int

    def to_dict(self) -> dict:
        obj = vars(self)
        obj["stats"] = [stat.to_dict() for stat in obj["stats"]]
        return obj
