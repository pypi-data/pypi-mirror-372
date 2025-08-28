import pytest
from geovisio import errors
from geovisio.utils.semantics import update_tags, Entity, EntityType
from geovisio.utils import db
from psycopg.sql import SQL
from psycopg.rows import dict_row
from geovisio.utils.tags import SemanticTagUpdate, TagAction
from tests import conftest
from flask import current_app


def get_tags(seq_id):
    return db.fetchall(
        current_app, SQL("SELECT key, value FROM sequences_semantics WHERE sequence_id = %s"), [seq_id], row_factory=dict_row
    )


def test_replace_tags(client, bobAccountID):
    """For the moment the replace action should be an explicit delete + add, and it can be done in one query"""
    seq = conftest.createSequence(client, "some sequence title")
    seq_id = seq.split("/")[-1]
    entity = Entity(type=EntityType.seq, id=seq_id)
    with db.conn(current_app) as conn, conn.cursor() as cursor:
        update_tags(cursor, entity, [SemanticTagUpdate(key="some_key", value="some_value")], account=bobAccountID)

    assert get_tags(seq_id) == [
        {
            "key": "some_key",
            "value": "some_value",
        }
    ]
    with db.conn(current_app) as conn, conn.transaction() as tr, conn.cursor() as cursor:
        update_tags(
            cursor,
            entity,
            [
                SemanticTagUpdate(action=TagAction.delete, key="some_key", value="some_value"),
                SemanticTagUpdate(action=TagAction.add, key="some_key", value="some_new_value"),
            ],
            account=bobAccountID,
        )

    assert get_tags(seq_id) == [
        {
            "key": "some_key",
            "value": "some_new_value",
        }
    ]


def test_duplicate_tags(client, bobAccountID):
    seq = conftest.createSequence(client, "some sequence title")
    seq_id = seq.split("/")[-1]
    entity = Entity(type=EntityType.seq, id=seq_id)
    with pytest.raises(errors.InvalidAPIUsage) as e:
        with db.conn(current_app) as conn, conn.cursor() as cursor:
            update_tags(
                cursor,
                entity,
                [SemanticTagUpdate(key="some_key", value="some_dup_value"), SemanticTagUpdate(key="some_key", value="some_dup_value")],
                account=bobAccountID,
            )

    assert str(e.value) == "Impossible to add semantic tags because of duplicates"
