from core.db import pool as db
from peewee import Model, UUIDField
from re import finditer


def make_table_name(model_class):
    model_name = model_class.__name__
    names = [name.lower() for name in camel_case_split(model_name)]
    names.append("tbl")
    name = "_".join(names)
    return name


def camel_case_split(identifier):
    matches = finditer(
        ".+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)", identifier
    )
    return [m.group(0) for m in matches]


class BaseModel(Model):
    id = UUIDField(primary_key=True)

    class Meta:
        database = db
        table_function = make_table_name
