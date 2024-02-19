from sqlalchemy import update, insert

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.comments import DbComment
from nng_sdk.postgres.exceptions import ItemNotFoundException, NngPostgresException
from nng_sdk.pydantic_models.comment import Comment


class CommentsCategory(DbCategory):
    def get_all_comments(self) -> list[Comment]:
        with self.begin_session() as session:
            all_comments: list[DbComment] = session.query(DbComment).all()
            if not all_comments:
                return []

            return [
                Comment.model_validate(comment.to_dict()) for comment in all_comments
            ]

    def already_exists(
        self, comment_vk_id: int, group_id: int, target_group_id: int, author_id: int
    ) -> bool:
        with self.begin_session() as session:
            comment = (
                session.query(DbComment)
                .filter(DbComment.comment_vk_id == comment_vk_id)
                .filter(DbComment.group_id == group_id)
                .filter(DbComment.target_group_id == target_group_id)
                .filter(DbComment.author_id == author_id)
                .all()
            )

            if comment:
                return True

            return False

    def get_user_comments(self, user_id: int) -> list[Comment]:
        with self.begin_session() as session:
            comments = (
                session.query(DbComment).filter(DbComment.author_id == user_id).all()
            )

            if not comments:
                return []

            return [Comment.model_validate(comment.to_dict()) for comment in comments]

    def get_comment(self, comment_id: int):
        with self.begin_session() as session:
            comment = (
                session.query(DbComment)
                .filter(DbComment.comment_id == comment_id)
                .all()
            )

            if not comment:
                raise ItemNotFoundException("Comment not found")

            return Comment.model_validate(comment[0].to_dict())

    def update_comment(self, comment: Comment):
        comment_id = comment.comment_id

        if comment_id == -1:
            raise NngPostgresException("Comment id is required")

        with self.begin_session() as session:
            comment_query = (
                session.query(DbComment)
                .filter(DbComment.comment_id == comment_id)
                .all()
            )

            if not comment_query:
                raise ItemNotFoundException("Comment not found")

            update_values = comment.model_dump(mode="json")
            update_values.pop("comment_id")

            session.execute(
                update(DbComment)
                .where(DbComment.comment_id == comment_id)
                .values(**update_values)
            )

            session.commit()

    def upload_comment(self, comment: Comment) -> Comment:
        insert_values = comment.model_dump(mode="json")
        insert_values.pop("comment_id")

        with self.begin_session() as session:
            uploaded_comment = session.execute(
                insert(DbComment).values(**insert_values).returning(DbComment)
            )

            session.commit()

            return Comment.model_validate(uploaded_comment.first()[0].to_dict())
