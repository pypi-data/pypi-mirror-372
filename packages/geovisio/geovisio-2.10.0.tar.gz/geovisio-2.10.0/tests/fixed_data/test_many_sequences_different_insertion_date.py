import pytest
from flask import current_app
from dateutil.parser import parse as dateparser
from datetime import datetime
import psycopg
from pystac import Collection

from geovisio.utils import db
from ..conftest import FIXTURE_DIR, app_with_data, getPictureIds, create_test_app


@pytest.fixture(scope="module")
def app(dburl, fs):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fs.tmp,
            "FS_PERMANENT_URL": fs.permanent,
            "FS_DERIVATES_URL": fs.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
            "SERVER_NAME": "localhost:5000",
            "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
            "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
        }
    ) as app:
        yield app


def createManySequences(dburl):
    seq = getPictureIds(dburl)[0]

    # Duplicate sequence metadata to have many sequences
    with db.cursor(current_app) as cursor:
        # Populate sequences
        for i in range(10):
            cursor.execute(
                """INSERT INTO sequences(status, metadata, geom, account_id, inserted_at, updated_at, computed_capture_date)
                SELECT
                    status, metadata, geom, account_id,
                    inserted_at + random() * (timestamp '2030-01-01 00:00:00' - inserted_at),
                    CASE WHEN random() < 0.5 THEN inserted_at + random() * (timestamp '2030-01-01 00:00:00' - inserted_at) END,
                    (inserted_at - random() * (inserted_at - timestamp '2000-01-01 00:00:00'))::date
                FROM sequences"""
            )

        # Populate sequences_pictures
        cursor.execute(
            """INSERT INTO sequences_pictures(seq_id, pic_id, rank)
            SELECT s.id, sp.pic_id, sp.rank
            FROM sequences s, sequences_pictures sp
            WHERE s.id != %s""",
            [seq.id],
        )

        # change the updated at date, since we don't want them all to the at the first updated at date
        # to do this, we need to change a field for each sequence, since the updated_at is computed by a trigger
        seqs = cursor.execute("SELECT id FROM sequences").fetchall()
        for s in seqs:
            cursor.execute(
                """UPDATE sequences
                SET metadata = metadata || '{"desc": "updated metadata"}'
                WHERE id = %s""",
                [s[0]],
            )


def _get_query_string(ref):
    from urllib.parse import parse_qs

    qs = ref.split("?")[1]
    return parse_qs(qs)


def collections_dates(app, child_col):
    dates = []
    for c in child_col:
        r = app.get(c.absolute_href)
        assert r.status_code == 200
        dates.append({k: r.json[k].replace("T", " ") for k in ["created", "updated"]} | {"id": c.extra_fields["id"]})
    return dates


@pytest.fixture(scope="module")
def client_app_with_many_sequences(
    app,
    dburl,
):
    """
    Fixture returning an app's client with many sequences loaded.
    Data shouldn't be modified by tests as it will be shared by several tests
    """
    import pathlib

    datadir = pathlib.Path(FIXTURE_DIR)
    pics = [
        datadir / "1.jpg",
        datadir / "2.jpg",
        datadir / "3.jpg",
        datadir / "4.jpg",
        datadir / "5.jpg",
    ]

    with app.app_context():
        client = app_with_data(app=app, sequences={"seq1": pics})
        createManySequences(dburl)
        return client


def test_user_collection_pagination_with_filters(client_app_with_many_sequences, defaultAccountID, dburl):
    with psycopg.connect(dburl) as conn:
        stats = conn.execute(
            """WITH mean AS (
        SELECT to_timestamp(avg(extract(epoch from inserted_at))) AS mean_inserted_at FROM sequences
    )
    SELECT mean.mean_inserted_at, COUNT(*), MIN(sequences.updated_at) FROM sequences, mean 
        WHERE inserted_at > mean.mean_inserted_at
        GROUP BY mean.mean_inserted_at
    """
        ).fetchone()
        assert stats
        mean_inserted_at, nb_sequence_after, min_updated_at = stats
        mean_inserted_at = mean_inserted_at.strftime("%Y-%m-%dT%H:%M:%SZ")

    query = f"/api/users/{defaultAccountID}/collection?limit=100&filter=created > '{mean_inserted_at}'&sortby=-updated"
    response = client_app_with_many_sequences.get(query)

    assert response.status_code == 200
    ctl = Collection.from_dict(response.json)

    childs = ctl.get_links("child")
    assert len(childs) == 100

    cols = collections_dates(client_app_with_many_sequences, childs)

    # Pagination links should be there since there is more data (but not first/prev since it's the first page)
    assert len(ctl.get_links("first")) == 0
    assert len(ctl.get_links("prev")) == 0
    assert len(ctl.get_links("next")) == 1

    next_qs = _get_query_string(ctl.get_links("next")[0].absolute_href)
    assert next_qs == {
        "limit": ["100"],
        "sortby": ["-updated,+created,+id"],
        "filter": [f"created > '{mean_inserted_at}'"],
        "page": [
            f"updated < '{cols[-1]['updated']}' OR (updated = '{cols[-1]['updated']}' AND created > '{cols[-1]['created']}') OR (updated = '{cols[-1]['updated']}' AND created = '{cols[-1]['created']}' AND id > '{cols[-1]['id']}')",
        ],
    }

    assert len(ctl.get_links("last")) == 1
    last_qs = _get_query_string(ctl.get_links("last")[0].absolute_href)
    assert last_qs == {
        "limit": ["100"],
        "sortby": ["-updated,+created,+id"],
        "filter": [f"created > '{mean_inserted_at}'"],
        "page": [f"updated >= '{min_updated_at}'"],
    }

    # we should be able to get all sequences, using the pagination, respecting the given filter:
    nextLink = query
    all_col_forward = {}
    while nextLink:
        response = client_app_with_many_sequences.get(nextLink)
        assert response.status_code == 200
        nextLink = next((l["href"] for l in response.json["links"] if l["rel"] == "next"), None)

        all_col_forward.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    assert len(all_col_forward) == nb_sequence_after

    # and the same backward
    nextLink = ctl.get_links("last")[0].absolute_href
    all_col_backward = {}
    while nextLink:
        response = client_app_with_many_sequences.get(nextLink)
        assert response.status_code == 200
        nextLink = next((l["href"] for l in response.json["links"] if l["rel"] == "prev"), None)

        all_col_backward.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    assert len(all_col_backward) == len(all_col_forward)
    assert all_col_backward == all_col_forward


def test_collections_created_date_filtering(client_app_with_many_sequences):
    from dateutil.tz import UTC

    def get_creation_date(response):
        return sorted(dateparser(r["created"]) for r in response.json["collections"])

    response = client_app_with_many_sequences.get("/api/collections?limit=10")
    assert response.status_code == 200
    initial_creation_date = get_creation_date(response)
    last_date = initial_creation_date[-1]

    def compare_query(query, date, after):
        response = client_app_with_many_sequences.get(query)
        assert response.status_code == 200, response.text
        creation_dates = get_creation_date(response)
        assert creation_dates
        if after:
            assert all([d > date for d in creation_dates])
        else:
            assert all([d < date for d in creation_dates])

    compare_query(
        f"/api/collections?limit=10&created_after={last_date.strftime('%Y-%m-%dT%H:%M:%S')}", last_date.replace(microsecond=0), after=True
    )
    # date without hour should be ok
    compare_query(
        f"/api/collections?limit=10&created_after={last_date.strftime('%Y-%m-%d')}",
        datetime.combine(last_date.date(), last_date.min.time(), tzinfo=UTC),
        after=True,
    )
    compare_query(
        f"/api/collections?limit=10&created_after={last_date.strftime('%Y-%m-%dT%H:%M:%SZ')}", last_date.replace(microsecond=0), after=True
    )
    # isoformated date should work
    compare_query(
        f"/api/collections?limit=10&created_after={last_date.strftime('%Y-%m-%dT%H:%M:%S')}%2B00:00",
        last_date.replace(microsecond=0),
        after=True,
    )

    # same filters should work with the `created_before` parameter
    compare_query(
        f"/api/collections?limit=10&created_before={last_date.strftime('%Y-%m-%dT%H:%M:%S')}", last_date.replace(microsecond=0), after=False
    )
    compare_query(
        f"/api/collections?limit=10&created_before={last_date.strftime('%Y-%m-%d')}",
        datetime.combine(last_date.date(), last_date.min.time(), tzinfo=UTC),
        after=False,
    )
    compare_query(
        f"/api/collections?limit=10&created_before={last_date.strftime('%Y-%m-%dT%H:%M:%SZ')}",
        last_date.replace(microsecond=0),
        after=False,
    )
    compare_query(
        f"/api/collections?limit=10&created_before={last_date.strftime('%Y-%m-%dT%H:%M:%S')}%2B00:00",
        last_date.replace(microsecond=0),
        after=False,
    )

    # We can also filter by both created_before and created_after
    mid_date = initial_creation_date[int(len(initial_creation_date) / 2)]
    response = client_app_with_many_sequences.get(
        f"/api/collections?limit=10&created_before={last_date.strftime('%Y-%m-%dT%H:%M:%SZ')}&created_after={mid_date.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    )
    assert response.status_code == 200
    creation_dates = get_creation_date(response)
    assert creation_dates
    assert all([d > mid_date.replace(microsecond=0) and d < last_date for d in creation_dates])
