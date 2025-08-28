import pytest
from urllib.parse import unquote

from geovisio.utils.fields import Bounds, FieldMapping, SQLDirection, SortBy, SortByField
from geovisio.utils.sequences import (
    get_pagination_links,
    STAC_FIELD_MAPPINGS,
    get_pagination_stac_filter,
    has_next_results,
    has_previous_results,
)


def simplify(links):
    return {l["rel"]: unquote(l["href"]) for l in links}


@pytest.mark.parametrize(
    ("sortBy", "dataBounds", "expected_next", "expected_prev"),
    [
        (
            SortBy(
                fields=[
                    SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                ]
            ),
            Bounds(first=["2012-01-12"], last=["2015-01-02"]),
            "created > '2015-01-02'",
            "created < '2012-01-12'",
        ),
        (
            SortBy(
                fields=[
                    SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.DESC),
                ]
            ),
            Bounds(first=["2015-01-02"], last=["2012-01-12"]),
            "created < '2012-01-12'",
            "created > '2015-01-02'",
        ),
        (
            SortBy(
                fields=[
                    SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                    SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
                ]
            ),
            Bounds(first=["2012-01-12", 12], last=["2015-01-02", 24]),
            "created > '2015-01-02' OR (created = '2015-01-02' AND id > '24')",
            "created < '2012-01-12' OR (created = '2012-01-12' AND id < '12')",
        ),
        (
            SortBy(
                fields=[
                    SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                    SortByField(field=STAC_FIELD_MAPPINGS["updated"], direction=SQLDirection.ASC),
                    SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
                ]
            ),
            Bounds(first=["2012-01-12", "2022-01-12", 12], last=["2015-01-02", "2018-01-12", 24]),
            "created > '2015-01-02' OR (created = '2015-01-02' AND updated > '2018-01-12') OR (created = '2015-01-02' AND updated = '2018-01-12' AND id > '24')",
            "created < '2012-01-12' OR (created = '2012-01-12' AND updated < '2022-01-12') OR (created = '2012-01-12' AND updated = '2022-01-12' AND id < '12')",
        ),
    ],
)
def test_get_pagination_stac_filter(sortBy, dataBounds, expected_next, expected_prev):
    assert get_pagination_stac_filter(sortBy=sortBy, dataBounds=dataBounds, next=True) == expected_next
    assert get_pagination_stac_filter(sortBy=sortBy, dataBounds=dataBounds, next=False) == expected_prev


def test_pagination_filters(app):
    links = get_pagination_links(
        route="stac_collections.getAllCollections",
        routeArgs={},
        sortBy=SortBy(
            fields=[
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
            ]
        ),
        datasetBounds=Bounds(first=["2010-01-12"], last=["2015-01-02"]),
        dataBounds=Bounds(first=["2012-01-12"], last=["2015-01-02"]),
        additional_filters=None,
    )

    assert simplify(links) == {
        "first": "http://localhost:5000/api/collections?sortby=+created",
        "prev": "http://localhost:5000/api/collections?sortby=+created&page=created+<+'2012-01-12'",
        # no last/prev since it's the last page
    }


def test_pagination_filters_with_args(app):
    links = get_pagination_links(
        route="stac_collections.getAllCollections",
        routeArgs={"limit": 12},
        sortBy=SortBy(
            fields=[
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
            ]
        ),
        datasetBounds=Bounds(first=["2010-01-12"], last=["2020-01-02"]),
        # Note: the id can be lower in the max than in the min, since it's a lexical sort, the max  the the id max of all sequences that have been created at 2015-01-02
        dataBounds=Bounds(first=["2012-01-12", 12], last=["2015-01-02", 4]),
        additional_filters=None,
    )

    assert simplify(links) == {
        "first": "http://localhost:5000/api/collections?limit=12&sortby=+created,+id",
        "next": "http://localhost:5000/api/collections?limit=12&sortby=+created,+id&page=created+>+'2015-01-02'+OR+(created+=+'2015-01-02'+AND+id+>+'4')",
        "prev": "http://localhost:5000/api/collections?limit=12&sortby=+created,+id&page=created+<+'2012-01-12'+OR+(created+=+'2012-01-12'+AND+id+<+'12')",
        "last": "http://localhost:5000/api/collections?limit=12&sortby=+created,+id&page=created+<=+'2020-01-02'",
    }


@pytest.mark.parametrize(
    ("sortBy", "datasetBounds", "queryBounds", "has_previous", "has_next"),
    [
        (
            [SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC)],
            Bounds(first=["2012-01-12"], last=["2015-01-02"]),
            Bounds(first=["2012-01-12"], last=["2014-01-02"]),
            False,
            True,
        ),
        (
            [SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC)],
            Bounds(first=["2010-01-01"], last=["2024-12-31"]),
            Bounds(first=["2012-01-12"], last=["2015-01-02"]),
            True,
            True,
        ),
        (
            [SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC)],
            Bounds(first=["2010-01-01"], last=["2024-12-31"]),
            Bounds(first=["2010-01-01"], last=["2024-12-31"]),
            False,
            False,
        ),
        (
            [
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["updated"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
            ],
            Bounds(first=["2010-01-12", "2012-01-12", 121245], last=["2015-01-02", "2019-01-12", 24]),
            # -----------------------------------------------------------------v here there are more collections with the same inserted_at, bit updated later
            Bounds(first=["2012-01-12", "2022-01-12", 12], last=["2015-01-02", "2018-01-12", 24]),
            True,
            True,
        ),
        (
            [
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["updated"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
            ],
            Bounds(first=["2010-01-12", "2012-01-12", 12], last=["2015-01-02", "2019-01-12", 24]),
            Bounds(first=["2010-01-12", "2012-01-12", 45], last=["2015-01-02", "2019-01-12", 24]),  # here the min differs only by the id
            True,
            False,
        ),
        (
            [
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["updated"], direction=SQLDirection.ASC),
                SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
            ],
            Bounds(first=["2010-01-12", "2012-01-12", 12], last=["2015-01-02", "2019-01-12", 24]),
            Bounds(first=["2010-01-12", "2012-01-12", 12], last=["2015-01-02", "2019-01-12", 24]),
            False,
            False,
        ),
        (
            [
                SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.DESC),
                SortByField(field=STAC_FIELD_MAPPINGS["updated"], direction=SQLDirection.DESC),
                SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.DESC),
            ],
            Bounds(first=["2015-01-02", "2019-01-12", 24], last=["2010-01-12", "2012-01-12", 121245]),
            Bounds(first=["2015-01-02", "2018-01-12", 24], last=["2012-01-12", "2022-01-12", 12]),
            True,
            True,
        ),
    ],
)
def test_has_other_results(sortBy, datasetBounds, queryBounds, has_previous, has_next):
    assert has_previous_results(SortBy(fields=sortBy), datasetBounds, queryBounds) == has_previous
    assert has_next_results(SortBy(fields=sortBy), datasetBounds, queryBounds) == has_next
