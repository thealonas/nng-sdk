from os import environ

from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from nng_sdk.postgres.categories.comments_category import CommentsCategory
from nng_sdk.postgres.categories.editor_history_category import EditorHistoryCategory
from nng_sdk.postgres.categories.group_stats_category import GroupsStatsCategory
from nng_sdk.postgres.categories.groups_category import GroupsCategory
from nng_sdk.postgres.categories.requests_category import RequestsCategory
from nng_sdk.postgres.categories.startup_category import StartupCategory
from nng_sdk.postgres.categories.sus_category import SusCategory
from nng_sdk.postgres.categories.tickets_category import TicketsCategory
from nng_sdk.postgres.categories.user_stats_category import UserStatsCategory
from nng_sdk.postgres.categories.users_category import UsersCategory
from nng_sdk.postgres.categories.watchdog_category import WatchdogCategory
from nng_sdk.postgres.db_models.base import BaseDatabaseModel


class NngPostgres:
    engine: Engine
    __session: sessionmaker | None = None

    def __init__(
        self,
        db_url: str | None = None,
        debug: bool = False,
    ):
        if not db_url:
            db_url = environ.get("NNG_DB_URL")

        self.engine = create_engine(db_url, echo=debug)
        BaseDatabaseModel.metadata.create_all(self.engine)

        self.__session = sessionmaker(bind=self.engine, autoflush=True)

        self.users = UsersCategory(self.begin_session)
        self.groups = GroupsCategory(self.begin_session)
        self.groups_stats = GroupsStatsCategory(self.begin_session)
        self.startup = StartupCategory(self.begin_session)
        self.editor_history = EditorHistoryCategory(self.begin_session)
        self.user_stats = UserStatsCategory(self.begin_session)
        self.watchdog = WatchdogCategory(self.begin_session)
        self.requests = RequestsCategory(self.begin_session)
        self.tickets = TicketsCategory(self.begin_session)
        self.sus = SusCategory(self.begin_session)
        self.comments = CommentsCategory(self.begin_session)

    def begin_session(self) -> Session:
        return Session(self.engine)
