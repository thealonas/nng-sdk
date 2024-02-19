from sqlalchemy import select, update, cast, String, or_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from nng_sdk.logger import get_logger
from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.users import DbUser, DbTrustInfo, DbViolation
from nng_sdk.postgres.exceptions import (
    ItemNotFoundException,
    ItemAlreadyExistsException,
    NngPostgresException,
)
from nng_sdk.pydantic_models.user import (
    User,
    Violation,
    TrustInfo,
)


class UsersCategory(DbCategory):
    def get_user(self, user_id: int) -> User:
        with self.begin_session() as session:
            query = (
                select(DbUser)
                .join(DbTrustInfo)
                .outerjoin(DbViolation)
                .where(DbUser.user_id == user_id)
            )

            result = list(session.scalars(query).unique())

            if not result:
                raise ItemNotFoundException(f"User {user_id} not found")

            user_dict_obj = result[0].to_dict()
            return User.model_validate(user_dict_obj)

    def search_users(self, search_query: str, limit: int = 100) -> list[User]:
        with self.begin_session() as session:
            search_query_str = f"%{search_query}%".lower()

            if limit >= 0:
                query = (
                    select(DbUser)
                    .where(
                        or_(
                            cast(DbUser.user_id, String).like(search_query_str),
                            DbUser.name.ilike(search_query_str),
                        )
                    )
                    .join(DbTrustInfo)
                    .outerjoin(DbViolation)
                    .limit(limit)
                )
            else:
                query = (
                    select(DbUser)
                    .where(
                        or_(
                            cast(DbUser.user_id, String).like(search_query_str),
                            DbUser.name.ilike(search_query_str),
                        )
                    )
                    .join(DbTrustInfo)
                    .outerjoin(DbViolation)
                )

            result = list(session.scalars(query).unique())
            return [User.model_validate(i.to_dict()) for i in result]

    def get_all_users(self) -> list[User]:
        with self.begin_session() as session:
            query = select(DbUser).outerjoin(DbViolation).join(DbTrustInfo)
            result = list(session.scalars(query).unique())
            return [User.model_validate(i.to_dict()) for i in result]

    def get_banned_users(self) -> list[User]:
        with self.begin_session() as session:
            users = (
                session.query(DbUser)
                .join(DbTrustInfo)
                .outerjoin(DbViolation)
                .filter(DbViolation.active == True)
            )

            return [User.model_validate(i.to_dict()) for i in users]

    def get_thx_users(self) -> list[User]:
        with self.begin_session() as session:
            users = (
                session.query(DbUser)
                .outerjoin(DbViolation)
                .join(DbTrustInfo)
                .filter(DbTrustInfo.activism == True)
            )

            return [User.model_validate(i.to_dict()) for i in users]

    def get_invited_users(self, invite_issuer: int) -> list[User]:
        with self.begin_session() as session:
            users = (
                session.query(DbUser)
                .outerjoin(DbViolation)
                .join(DbTrustInfo)
                .filter(DbUser.invited_by == invite_issuer)
            )

            return [User.model_validate(i.to_dict()) for i in users]

    def add_violation(self, user_id: int, violation: Violation):
        with self.begin_session() as session:
            user = session.query(DbUser).filter(DbUser.user_id == user_id).all()
            if not user:
                raise ItemNotFoundException("User not found")

            violation_dict = self.parse_pydantic_schema(violation)
            violation_dict["user_id"] = user_id
            db_violation = DbViolation(**violation_dict)

            session.add(db_violation)
            session.commit()

    def unban_user(self, user_id: int):
        with self.begin_session() as session:
            query = (
                select(DbUser).outerjoin(DbViolation).where(DbUser.user_id == user_id)
            )
            result = list(session.scalars(query).unique())
            if not result:
                raise ItemNotFoundException("User not found")

            violations = result[0].violations
            for violation in violations:
                if violation.active is None:
                    continue
                violation.active = False
                session.add(violation)

            session.commit()

    @staticmethod
    def _update_user_trust_info(user_id: int, trust: TrustInfo, session: Session):
        trust_info_query: DbTrustInfo | None = (
            session.query(DbTrustInfo).filter(DbTrustInfo.user_id == user_id).first()
        )

        if not trust_info_query:
            raise ItemNotFoundException("Trust info not found")

        session.execute(
            update(DbTrustInfo)
            .where(DbTrustInfo.user_id == user_id)
            .values(**trust.model_dump(mode="json"))
        )

        session.commit()

    def update_user_trust_info(self, user_id: int, trust: TrustInfo):
        with self.begin_session() as session:
            self._update_user_trust_info(user_id, trust, session)

    def get_all_editors(self) -> list[User]:
        with self.begin_session() as session:
            editors = (
                session.query(DbUser)
                .outerjoin(DbViolation)
                .join(DbTrustInfo)
                .filter(func.array_length(DbUser.groups, 1) > 0)
                .all()
            )
            return [User.model_validate(i.to_dict()) for i in editors]

    def update_user(self, user: User):
        with self.begin_session() as session:
            existing_users: list[DbUser] | None = (
                session.query(DbUser).filter(DbUser.user_id == user.user_id).all()
            )

            if not existing_users:
                raise ItemNotFoundException("User not found")

            existing_user = existing_users[0]

            user_dict = self.parse_pydantic_schema(user)

            for key in existing_user.__dict__.keys():
                if key in user_dict.keys():
                    setattr(existing_user, key, user_dict[key])

            session.add(existing_user)

            self._update_user_trust_info(user.user_id, user.trust_info, session)

            # violation мы не обновляем потому что для этого есть своё апи
            # см. add_violation(), unban_user()
            session.commit()

    def add_user(self, user: User):
        with self.begin_session() as session:
            user_dict = self.parse_pydantic_schema(user)
            db_user = DbUser(**user_dict)

            try:
                session.add(db_user)
                session.commit()
            except IntegrityError as e:
                logger = get_logger()
                logger.error(e)
                session.rollback()
                raise ItemAlreadyExistsException(f"User {user.user_id} already exist")
            return user

    def delete_user(self, user_id: int):
        with self.begin_session() as session:
            try:
                user: DbUser = (
                    session.query(DbUser).filter(DbUser.user_id == user_id).first()
                )
            except IntegrityError:
                raise ItemNotFoundException(f"User {user_id} not found")

            try:
                session.delete(user)
            except IntegrityError as e:
                session.rollback()
                raise NngPostgresException(e)
            else:
                session.commit()
