import datetime

from sqlalchemy import update, desc
from sqlalchemy.orm import Session

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.editor_history import DbEditorHistory
from nng_sdk.postgres.db_models.users import DbUser
from nng_sdk.postgres.exceptions import UserDoesNotExist
from nng_sdk.pydantic_models.editor_history import EditorHistory, EditorHistoryItem


class EditorHistoryCategory(DbCategory):
    def get_user_history(self, user_id: int) -> EditorHistory:
        with self.begin_session() as session:
            self._raise_and_ensure_user_exists(user_id, session)

            all_user_history: list[DbEditorHistory] = (
                session.query(DbEditorHistory)
                .filter(DbEditorHistory.user_id == user_id)
                .order_by(desc(DbEditorHistory.date))
                .all()
            )

            history = EditorHistory(user_id=user_id, history=[])

            if not all_user_history:
                return history

            history.history = [
                EditorHistoryItem.model_validate(i.to_dict()) for i in all_user_history
            ]

            return history

    @staticmethod
    def _raise_and_ensure_user_exists(user_id: int, session: Session):
        user_exists = session.query(DbUser).filter(DbUser.user_id == user_id).first()
        if not user_exists:
            raise UserDoesNotExist(f"User {user_id} does not exist")

    def raise_and_ensure_user_exists(self, user_id: int):
        with self.begin_session() as session:
            self._raise_and_ensure_user_exists(user_id, session)
        return True

    @staticmethod
    def _add_user_history(
        user_id: int, history_item: EditorHistoryItem, session: Session
    ):
        history = DbEditorHistory(
            user_id=user_id,
            group_id=history_item.group_id,
            granted=history_item.granted,
            date=history_item.date,
            wip=history_item.wip,
        )

        session.add(history)
        session.commit()

    def add_user_history(self, user_id: int, history_item: EditorHistoryItem):
        with self.begin_session() as session:
            self._add_user_history(user_id, history_item, session)

    @staticmethod
    def _clear_non_granted_items(user_id: int, session: Session):
        session.query(DbEditorHistory).filter(
            DbEditorHistory.user_id == user_id
        ).filter(DbEditorHistory.granted == False).delete()

        session.commit()

    @staticmethod
    def _clear_wip(user_id: int, session: Session):
        all_stories = (
            session.query(DbEditorHistory)
            .filter(DbEditorHistory.user_id == user_id)
            .filter(DbEditorHistory.granted == True)
            .all()
        )

        for story in all_stories:
            session.execute(
                update(DbEditorHistory)
                .where(DbEditorHistory.history_id == story.history_id)
                .values(wip=False)
            )

        session.commit()

    def clear_non_granted_items(self, user_id: int):
        with self.begin_session() as session:
            self._clear_non_granted_items(user_id, session)

    def clear_wip(self, user_id: int):
        with self.begin_session() as session:
            self._clear_wip(user_id, session)

    def add_non_granted_item(
        self,
        user_id: int,
        group_id: int,
        date: datetime.datetime | None = None,
    ):
        date = date or datetime.datetime.now()
        with self.begin_session() as session:
            self._raise_and_ensure_user_exists(user_id, session)

            # чистим все невыданные элементы чтобы не было мусора
            self._clear_non_granted_items(user_id, session)

            #
            self._clear_wip(user_id, session)

            # добавляем мусор
            self._add_user_history(
                user_id,
                EditorHistoryItem(
                    group_id=group_id, granted=False, date=date, wip=False
                ),
                session,
            )

    def set_wip(self, user_id: int, group_id: int):
        with self.begin_session() as session:
            self._raise_and_ensure_user_exists(user_id, session)

            session.execute(
                update(DbEditorHistory)
                .filter(DbEditorHistory.user_id == user_id)
                .filter(DbEditorHistory.group_id == group_id)
                .filter(DbEditorHistory.granted == False)
                .values(wip=True)
            )

            session.commit()

    def is_wip(self, user_id: int):
        with self.begin_session() as session:
            wip_history = (
                session.query(DbEditorHistory)
                .filter(DbEditorHistory.user_id == user_id)
                .filter(DbEditorHistory.wip == True)
                .all()
            )

            return bool(wip_history)

    def add_granted_item(
        self,
        user_id: int,
        group_id: int,
        date: datetime.datetime | None = None,
    ):
        date = date or datetime.datetime.now()
        with self.begin_session() as session:
            self._raise_and_ensure_user_exists(user_id, session)
            self._add_user_history(
                user_id,
                EditorHistoryItem(
                    group_id=group_id, granted=True, date=date, wip=False
                ),
                session,
            )

            self._clear_wip(user_id, session)

            # чистим все невыданные элементы после выдачи
            self._clear_non_granted_items(user_id, session)

    def delete_user_history(self, user_id: int):
        with self.begin_session() as session:
            session.query(DbEditorHistory).where(
                DbEditorHistory.user_id == user_id
            ).delete()

            session.commit()
