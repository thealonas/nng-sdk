from typing import Optional

from sqlalchemy import update

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.watchdog import DbWatchdog
from nng_sdk.postgres.exceptions import ItemNotFoundException
from nng_sdk.pydantic_models.watchdog import Watchdog


class WatchdogCategory(DbCategory):
    def upload_or_update_log(self, watchdog: Watchdog) -> Optional[Watchdog]:
        with self.begin_session() as session:
            watchdogs = (
                session.query(DbWatchdog)
                .filter(DbWatchdog.watchdog_id == watchdog.watchdog_id)
                .all()
            )

            if len(watchdogs) > 0:
                update_dict = vars(watchdog)
                watchdog_id = watchdog.watchdog_id
                del update_dict["watchdog_id"]
                session.execute(
                    update(DbWatchdog)
                    .filter(DbWatchdog.watchdog_id == watchdog_id)
                    .values(update_dict)
                )
                session.commit()
                return
            else:
                new_watchdog = DbWatchdog(
                    intruder=watchdog.intruder,
                    victim=watchdog.victim,
                    group_id=watchdog.group_id,
                    priority=watchdog.priority,
                    date=watchdog.date,
                    reviewed=watchdog.reviewed,
                )
                session.add(new_watchdog)
                session.commit()
                session.refresh(new_watchdog)

                return Watchdog.model_validate(new_watchdog.to_dict())

    def get_all_logs(self) -> list[Watchdog]:
        with self.begin_session() as session:
            return [
                Watchdog.model_validate(watchdog.to_dict())
                for watchdog in session.query(DbWatchdog).all()
            ]

    def get_all_unreviewed_logs(self) -> list[Watchdog]:
        with self.begin_session() as session:
            return [
                Watchdog.model_validate(watchdog.to_dict())
                for watchdog in session.query(DbWatchdog)
                .filter(DbWatchdog.reviewed == False)
                .all()
            ]

    def get_log(self, watchdog_id: int):
        with self.begin_session() as session:
            watchdog = (
                session.query(DbWatchdog)
                .filter(DbWatchdog.watchdog_id == watchdog_id)
                .all()
            )

            if not watchdog:
                raise ItemNotFoundException("Watchdog not found")

            return Watchdog.model_validate(watchdog[0].to_dict())
