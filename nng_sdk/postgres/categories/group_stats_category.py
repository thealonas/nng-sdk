from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.group_stats import DbGroupStats
from nng_sdk.pydantic_models.group_stats import GroupStats


class GroupsStatsCategory(DbCategory):
    def upload_statistics(self, stats: GroupStats):
        dict_stats = stats.to_dict()

        with self.begin_session() as session:
            new_stats = DbGroupStats(
                date=stats.date,
                total_users=stats.total_users,
                total_managers=stats.total_managers,
                stats=dict_stats["stats"],
            )

            session.add(new_stats)
            session.commit()

    def get_stats(self) -> list[GroupStats]:
        with self.begin_session() as session:
            stats = session.query(DbGroupStats).all()
            return [GroupStats.model_validate(stat.to_dict()) for stat in stats]
