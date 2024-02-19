import datetime

from nng_sdk.pydantic_models.base_model import BaseNngModel


class EditorHistoryItem(BaseNngModel):
    group_id: int
    granted: bool
    date: datetime.datetime
    wip: bool


class EditorHistory(BaseNngModel):
    user_id: int
    history: list[EditorHistoryItem]

    @property
    def has_non_granted_items(self) -> bool:
        return any(not item.granted for item in self.history)

    def get_non_granted_item(self) -> EditorHistoryItem:
        return [item for item in self.history if not item.granted][0]

    def get_items_from_last_day(self) -> list[EditorHistoryItem]:
        one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
        return [item for item in self.history if item.date >= one_day_ago]
