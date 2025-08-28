from typing import Optional
from flask import current_app
from pydantic import BaseModel
from psycopg.sql import SQL
from geovisio.utils import db
from geovisio.utils.model_query import get_db_params_and_values


class SomeModel(BaseModel):
    a: int
    b: str
    c: Optional[int] = None


def test_simple_model_update(client):
    params = get_db_params_and_values(SomeModel(a=1, b="b"))

    assert params.params_as_dict == {"a": 1, "b": "b"}

    with db.conn(current_app) as conn:
        fields = params.fields_for_set()

        update_query = SQL("UPDATE test_model SET {fields} WHERE id = %(id)s").format(fields=fields)

        assert update_query.as_string(conn) == 'UPDATE test_model SET "a" = %(a)s, "b" = %(b)s WHERE id = %(id)s'


def test_simple_model_insert(client):
    params = get_db_params_and_values(SomeModel(a=1, b="b"))

    assert params.params_as_dict == {"a": 1, "b": "b"}

    with db.conn(current_app) as conn:
        fields = params.fields()
        values_placeholders = params.placeholders()

        insert_query = SQL("INSERT INTO test_model({fields}) VALUES({values}) RETURNING *").format(
            fields=fields, values=values_placeholders
        )

        assert insert_query.as_string(conn) == 'INSERT INTO test_model("a", "b") VALUES(%(a)s, %(b)s) RETURNING *'
