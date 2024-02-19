from typing import Callable

from sqlalchemy.orm import Session


class DbCategory:
    def __init__(self, begin_session: Callable[[], Session]):
        self.begin_session = begin_session

    @staticmethod
    def is_pydantic(obj: object):
        return type(obj).__class__.__name__ == "ModelMetaclass"

    def parse_pydantic_schema(self, schema):
        parsed_schema = dict(schema)
        for key, value in parsed_schema.items():
            try:
                if isinstance(value, list) and len(value):
                    if self.is_pydantic(value[0]):
                        parsed_schema[key] = [
                            schema.Meta.orm_model(**schema.dict()) for schema in value
                        ]
                else:
                    if self.is_pydantic(value):
                        parsed_schema[key] = value.Meta.orm_model(**value.dict())
            except AttributeError:
                raise AttributeError(
                    "Found nested Pydantic model but Meta.orm_model was not specified."
                )
        return parsed_schema
