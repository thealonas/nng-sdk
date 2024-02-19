from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.user_stats import DbUserStats
from nng_sdk.postgres.exceptions import ItemAlreadyExistsException
from nng_sdk.pydantic_models.user_stats import UserStats


class UserStatsCategory(DbCategory):
    def upload_stats(self, year: int, users: int):
        with self.begin_session() as session:
            if session.query(DbUserStats).filter_by(year=year).count() > 0:
                raise ItemAlreadyExistsException(
                    f"Stats for year {year} already uploaded"
                )

            session.add(DbUserStats(year=year, users=users))
            session.commit()

    def get_all_stats(self) -> list[UserStats]:
        with self.begin_session() as session:
            all_stats = session.query(DbUserStats).all()
            return [UserStats.model_validate(vars(stat)) for stat in all_stats]
