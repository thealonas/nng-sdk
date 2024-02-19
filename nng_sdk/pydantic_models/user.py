import datetime
from enum import StrEnum
from typing import Optional, List

from nng_sdk.postgres.db_models.users import DbUser, DbTrustInfo, DbViolation
from nng_sdk.pydantic_models.base_model import BaseNngModel


class ViolationType(StrEnum):
    warned = "warned"
    banned = "banned"


class BanPriority(StrEnum):
    green = "green"
    teal = "teal"
    orange = "orange"
    red = "red"


class Violation(BaseNngModel):
    type: ViolationType
    group_id: Optional[int] = None
    priority: Optional[BanPriority] = None
    complaint: Optional[int] = None
    request_ref: Optional[int] = None
    watchdog_ref: Optional[int] = None
    active: Optional[bool] = None
    date: Optional[datetime.date] = None

    def is_expired(self):
        if self.type != ViolationType.warned:
            return False

        current_date = datetime.date.today()

        if (current_date - self.date).days > 365:
            return True

        return False

    class Meta:
        orm_model = DbViolation


class TrustInfo(BaseNngModel):
    trust: int
    toxicity: float

    registration_date: Optional[datetime.date] = None
    nng_join_date: datetime.date

    odd_groups: bool

    closed_profile: bool
    has_photo: bool
    has_wall_posts: bool
    has_friends: bool
    verified: bool

    joined_test_group: bool
    joined_main_group: bool

    has_violation: bool
    had_violation: bool

    has_warning: bool
    had_warning: bool

    activism: bool
    used_nng: bool
    donate: bool

    last_updated: Optional[datetime.date] = None

    class Meta:
        orm_model = DbTrustInfo

    @staticmethod
    def create_default() -> "TrustInfo":
        return TrustInfo(
            trust=40,
            toxicity=0,
            registration_date=datetime.date.today(),
            nng_join_date=datetime.date.today(),
            odd_groups=False,
            closed_profile=False,
            has_photo=False,
            has_wall_posts=False,
            has_friends=False,
            verified=False,
            joined_test_group=False,
            activism=False,
            has_violation=False,
            had_violation=False,
            has_warning=False,
            had_warning=False,
            used_nng=False,
            joined_main_group=False,
            donate=False,
            last_updated=datetime.datetime.min,
        )


class User(BaseNngModel):
    user_id: int
    name: str
    admin: bool
    trust_info: TrustInfo
    invited_by: Optional[int] = None
    join_date: datetime.date
    groups: List[int]
    violations: List[Violation]

    class Meta:
        orm_model = DbUser

    def get_active_violation(self) -> Violation:
        if not self.violations:
            raise RuntimeError("User is not banned")

        active_violation_list = [v for v in self.violations if v.active]
        if not active_violation_list:
            raise RuntimeError("User is not banned")

        return min(active_violation_list, key=lambda v: v.date)

    def add_violation(self, violation: Violation):
        if self.violations is None:
            self.violations = []
        self.violations.append(violation)

    def has_active_violation(self) -> bool:
        try:
            self.get_active_violation()
            return True
        except RuntimeError:
            return False

    def has_warning(self) -> bool:
        if not self.violations:
            return False

        return len([i for i in self.violations if i.type == ViolationType.warned]) > 0

    def add_group(self, group_id: int):
        if self.groups is None:
            self.groups = []

        if group_id in self.groups:
            return

        self.groups.append(group_id)
        self.groups = list(set(self.groups))
        self.groups.sort()

    def remove_group(self, group_id: int):
        if self.groups is None:
            self.groups = []

        try:
            self.groups.remove(group_id)
        except ValueError:
            pass

        self.groups = list(set(self.groups))
        self.groups.sort()
