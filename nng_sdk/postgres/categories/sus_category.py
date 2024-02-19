from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.sus import DbSus


class SusCategory(DbCategory):
    def add_sus(self, sus_id: int):
        with self.begin_session() as session:
            sus = DbSus(id=sus_id)
            session.add(sus)
            session.commit()

    def is_sus(self, sus_id: int) -> bool:
        with self.begin_session() as session:
            sus = session.query(DbSus).filter(DbSus.id == sus_id).all()
            return any(sus)

    def get_all_sus(self) -> list[int]:
        with self.begin_session() as session:
            return [sus.id for sus in session.query(DbSus).all()]
