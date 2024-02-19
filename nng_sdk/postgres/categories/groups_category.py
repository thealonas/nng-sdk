from sqlalchemy.exc import IntegrityError

from nng_sdk.postgres.db_category import DbCategory
from nng_sdk.postgres.db_models.groups import DbGroup
from nng_sdk.postgres.exceptions import (
    ItemNotFoundException,
    ItemAlreadyExistsException,
)
from nng_sdk.pydantic_models.group import Group


class GroupsCategory(DbCategory):
    def get_all_groups(self):
        with self.begin_session() as session:
            groups: list[DbGroup] = session.query(DbGroup).all()
            return [Group.model_validate(i.to_dict()) for i in groups]

    def get_group(self, group_id: int):
        with self.begin_session() as session:
            group: DbGroup | None = (
                session.query(DbGroup).filter(DbGroup.group_id == group_id).first()
            )

            if not group:
                raise ItemNotFoundException(f"Cannot find group {group_id}")

            return Group.model_validate(group.to_dict())

    def add_group(self, group: Group):
        group_dict = self.parse_pydantic_schema(group)

        with self.begin_session() as session:
            session.add(DbGroup(**group_dict))
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                raise ItemAlreadyExistsException(
                    f"Group {group.group_id} already exists"
                )
