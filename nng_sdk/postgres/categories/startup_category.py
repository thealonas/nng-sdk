from sqlalchemy import update, insert

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.startups import DbStartup
from nng_sdk.postgres.exceptions import (
    ItemNotFoundException,
)
from nng_sdk.pydantic_models.startup import Startup


class StartupCategory(DbCategory):
    def get_startup_for_service(self, service_name: str) -> Startup:
        with self.begin_session() as session:
            startups: list[DbStartup] = (
                session.query(DbStartup)
                .filter(DbStartup.service_name == service_name)
                .all()
            )

            if not startups:
                raise ItemNotFoundException("Startup not found")

            return Startup.model_validate(startups[0].to_dict())

    def upload_startup(self, startup: Startup):
        with self.begin_session() as session:
            startups: list[Startup] = (
                session.query(DbStartup)
                .filter(DbStartup.service_name == startup.service_name)
                .all()
            )

            if not startups:
                session.execute(insert(DbStartup).values(vars(startup)))
            else:
                session.execute(
                    update(DbStartup)
                    .values(vars(startup))
                    .where(DbStartup.service_name == startup.service_name)
                )

            session.commit()
