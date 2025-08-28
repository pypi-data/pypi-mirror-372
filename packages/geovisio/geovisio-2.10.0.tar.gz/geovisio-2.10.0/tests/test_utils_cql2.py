from geovisio.utils.cql2 import parse_semantic_filter

import pytest
from psycopg.sql import SQL


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("\"semantics.#\"='ILovePanoramax'", "((key = '#') AND (value = 'ILovePanoramax'))"),
        ("\"semantics.osm|amenity\" IN ('bench', 'whatever')", "((key = 'osm|amenity') AND value IN ('bench', 'whatever'))"),
        (
            "\"semantics.osm|traffic_sign\"='stop' OR \"semantics.osm|amenity\" IN ('bench', 'whatever')",
            "(((key = 'osm|traffic_sign') AND (value = 'stop')) OR ((key = 'osm|amenity') AND value IN ('bench', 'whatever')))",
        ),
        ("semantics.pouet='*'", "((key = 'pouet') AND (value = '*'))"),  # * is not a special value
        ("semantics.pouet IS NOT NULL", "(key = 'pouet')"),
    ],
)
def test_parse_semantic_filter(value, expected):
    assert parse_semantic_filter(value) == SQL(expected)


@pytest.mark.parametrize(
    ("value"),
    [
        ("semantics.pouet >= 'toto'"),
        ("semantics.pouet EXISTS"),
        ("semantics.pouet DOES-NOT-EXISTS"),
        ("semantics.pouet is not null"),  # should be uppercase in the documentation
        ("semantics.pouet IS NULL"),
        (
            "\"semantics.#\"='ILovePanoramax' AND \"semantics.#\"='ILoveBike' "
        ),  # this is not valid for the moment, but we might support it at one point
    ],
)
def test_parse_semantic_filter_error(value):
    with pytest.raises(Exception) as e:
        parse_semantic_filter(value)
    assert str(e.value) == "Unsupported filter parameter"
