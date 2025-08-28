import pytest
from flask import current_app
from geovisio.utils import db
import psycopg
from pystac import Collection, Catalog
from ..conftest import FIXTURE_DIR, app_with_data, defaultAccountToken, getPictureIds, create_test_app

"""
Module for tests needing a lot of sequences.

To reduce testing time, the data is loaded only once for all tests.

No tests should change the data!
"""


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
                    inserted_at,
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


def test_collections_pagination_classic(client_app_with_many_sequences):
    # Launch all calls against API
    nextLink = "/api/collections?limit=50"
    receivedLinks = []
    receivedSeqIds = []

    while nextLink:
        response = client_app_with_many_sequences.get(nextLink)
        assert response.status_code == 200

        myLinks = {l["rel"]: l["href"] for l in response.json["links"]}

        receivedLinks.append(myLinks)
        nextLink = myLinks.get("next")

        for c in response.json["collections"]:
            receivedSeqIds.append(c["id"])

    # Check received links
    for i, links in enumerate(receivedLinks):
        assert "root" in links
        assert "parent" in links
        assert "self" in links
        assert "/api/collections?limit=50" in links["self"]

        if i == 0:
            assert "next" in links
            assert "last" in links
            assert "prev" not in links
            assert "first" not in links
        elif i == len(receivedLinks) - 1:
            assert "next" not in links
            assert "last" not in links
            assert "prev" in links
            assert "first" in links
        else:
            assert "first" in links
            assert "last" in links
            assert "next" in links
            assert "prev" in links
            prevLinks = receivedLinks[i - 1]
            prevLinks["next"] = links["self"]
            prevLinks["self"] = links["prev"]
            nextLinks = receivedLinks[i + 1]
            links["next"] = nextLinks["self"]
            links["self"] = nextLinks["prev"]

    # Check received sequence IDS
    assert len(receivedSeqIds) == 1024
    assert len(set(receivedSeqIds)) == 1024


def test_collections_pagination_descending(client_app_with_many_sequences):
    # Call collections endpoint to get last page
    response = client_app_with_many_sequences.get("/api/collections?limit=50")
    assert response.status_code == 200

    lastLink = next((l for l in response.json["links"] if l["rel"] == "last"))

    # Launch all calls against API
    prevLink = lastLink["href"]
    receivedLinks = []
    receivedSeqIds = []

    while prevLink:
        response = client_app_with_many_sequences.get(prevLink)
        assert response.status_code == 200

        myLinks = {l["rel"]: l["href"] for l in response.json["links"]}

        receivedLinks.append(myLinks)
        prevLink = myLinks.get("prev")

        for c in response.json["collections"]:
            receivedSeqIds.append(c["id"])

    # Check received links
    for i, links in enumerate(receivedLinks):
        assert "root" in links
        assert "parent" in links
        assert "self" in links
        assert "/api/collections?limit=50" in links["self"]

        if i == 0:
            assert "next" not in links, links.get("next")
            assert "last" not in links
            assert "prev" in links
            assert "first" in links
        elif i == len(receivedLinks) - 1:
            assert "next" in links
            assert "last" in links
            assert "prev" not in links
            assert "first" not in links
        else:
            assert links["first"] == "http://localhost:5000/api/collections?limit=50&sortby=%2Bcreated,%2Bid"
            assert "last" in links
            assert "next" in links
            assert "prev" in links
            prevLinks = receivedLinks[i + 1]
            prevLinks["next"] = links["self"]
            prevLinks["self"] = links["prev"]
            nextLinks = receivedLinks[i - 1]
            links["next"] = nextLinks["self"]
            links["self"] = nextLinks["prev"]

    # Check received sequence IDS
    assert len(receivedSeqIds) == 1024
    assert len(set(receivedSeqIds)) == 1024


def test_user_collection_many_filters_sortby(client_app_with_many_sequences, defaultAccountID, dburl):
    response = client_app_with_many_sequences.get(
        f"/api/users/{defaultAccountID}/collection?limit=50&sortby=created,updated&filter=updated > '2020-01-01'"
    )

    assert response.status_code == 200
    ctl = Collection.from_dict(response.json)

    childs = ctl.get_links("child")
    assert len(childs) == 50

    # No pagination links as we have filtered on a column
    #  which is not the first to sort by
    assert len(ctl.get_links("first")) == 0
    assert len(ctl.get_links("prev")) == 0
    assert len(ctl.get_links("next")) == 1

    creations_dates = collections_creation_dates(client_app_with_many_sequences, childs)
    update_dates = collections_update_dates(client_app_with_many_sequences, childs)
    last_id = childs[-1].extra_fields["id"]

    next_qs = _get_query_string(ctl.get_links("next")[0].absolute_href)
    assert next_qs == {
        "limit": ["50"],
        "sortby": ["+created,+updated,+id"],
        "filter": ["updated > '2020-01-01'"],
        "page": [
            f"created > '{creations_dates[-1]}' OR (created = '{creations_dates[-1]}' AND updated > '{update_dates[-1]}') OR (created = '{creations_dates[-1]}' AND updated = '{update_dates[-1]}' AND id > '{last_id}')",
        ],
    }

    with psycopg.connect(dburl) as conn:
        last_inserted_at = conn.execute("SELECT max(inserted_at) FROM sequences WHERE updated_at > '2020-01-01'").fetchone()
        assert last_inserted_at
        last_inserted_at = str(last_inserted_at[0])
    last_qs = _get_query_string(ctl.get_links("last")[0].absolute_href)
    assert last_qs == {
        "limit": ["50"],
        "sortby": ["+created,+updated,+id"],
        "filter": ["updated > '2020-01-01'"],
        "page": [f"created <= '{last_inserted_at}'"],
    }


@pytest.mark.parametrize(
    ("sortby"), ("created", "-created", "updated", "-updated", "datetime", "-datetime", "%2Bcreated,-updated", "-created,%2Bupdated")
)
def test_user_collection_pagination_first2last(client_app_with_many_sequences, dburl, defaultAccountID, sortby):
    # Launch all calls against API
    nextLink = f"/api/users/{defaultAccountID}/collection?limit=200&sortby={sortby}"
    receivedChildren = {}

    while nextLink:
        response = client_app_with_many_sequences.get(nextLink)
        assert response.status_code == 200
        nextLink = next((l["href"] for l in response.json["links"] if l["rel"] == "next"), None)

        receivedChildren.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    len(receivedChildren) == 1024


@pytest.mark.parametrize(
    ("sortby"), ("created", "-created", "updated", "-updated", "datetime", "-datetime", "%2Bcreated,-updated", "-created,%2Bupdated")
)
def test_user_collection_pagination_last2first(client_app_with_many_sequences, dburl, defaultAccountID, sortby):
    # Call first page to get last page URL
    response = client_app_with_many_sequences.get(f"/api/users/{defaultAccountID}/collection?limit=200&sortby={sortby}")
    assert response.status_code == 200
    lastLink = next(l["href"] for l in response.json["links"] if l["rel"] == "last")
    assert lastLink is not None

    # Launch all calls against API
    prevLink = lastLink
    receivedChildren = {}

    while prevLink:
        response = client_app_with_many_sequences.get(prevLink)
        assert response.status_code == 200
        prevLink = next((l["href"] for l in response.json["links"] if l["rel"] == "prev"), None)

        receivedChildren.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    len(receivedChildren) == 1024


def _get_query_string(ref):
    from urllib.parse import parse_qs

    qs = ref.split("?")[1]
    return parse_qs(qs)


def collections_creation_dates(app, child_col):
    dates = []
    for c in child_col:
        r = app.get(c.absolute_href)
        assert r.status_code == 200
        dates.append(r.json["created"].replace("T", " "))
    return dates


def collections_update_dates(app, child_col):
    dates = []
    for c in child_col:
        r = app.get(c.absolute_href)
        assert r.status_code == 200
        dates.append(r.json["updated"].replace("T", " "))
    return dates


def test_user_with_many_catalog(client_app_with_many_sequences, defaultAccountID, dburl):
    nextLink = f"/api/users/{str(defaultAccountID)}/catalog"
    all_col_forward = {}
    while nextLink:
        response = client_app_with_many_sequences.get(nextLink)

        assert response.status_code == 200
        assert response.json["type"] == "Catalog"
        Catalog.from_dict(response.json)
        nextLink = next((l["href"] for l in response.json["links"] if l["rel"] == "next"), None)

        all_col_forward.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    assert len(all_col_forward) == 1024

    # and the same backward
    response = client_app_with_many_sequences.get(f"/api/users/{str(defaultAccountID)}/catalog")
    prevLink = next(l["href"] for l in response.json["links"] if l["rel"] == "last")
    all_col_backward = {}
    while prevLink:
        response = client_app_with_many_sequences.get(prevLink)
        assert response.status_code == 200
        prevLink = next((l["href"] for l in response.json["links"] if l["rel"] == "prev"), None)

        all_col_backward.update({l["id"]: l for l in response.json["links"] if l["rel"] == "child"})

    assert all_col_backward == all_col_forward


def test_my_catalog(client_app_with_many_sequences, defaultAccountID, defaultAccountToken):
    client = client_app_with_many_sequences
    response = client.get(f"/api/users/me/catalog", headers={"Authorization": f"Bearer {defaultAccountToken()}"}, follow_redirects=True)
    userName = "Default account"
    assert response.status_code == 200
    assert response.json["type"] == "Catalog"
    ctl = Catalog.from_dict(response.json)
    assert len(ctl.links) > 0
    assert ctl.title == userName + "'s sequences"
    assert ctl.id == f"user:{defaultAccountID}"
    assert ctl.description == "List of all sequences of user " + userName
    assert ctl.extra_fields.get("extent") is None
    assert ctl.get_links("self")[0].get_absolute_href() == f"http://localhost:5000/api/users/{str(defaultAccountID)}/catalog/"

    # also work with a filter and a page
    response = client.get(
        f"/api/users/me/catalog?limit=10", headers={"Authorization": f"Bearer {defaultAccountToken()}"}, follow_redirects=True
    )
    assert response.status_code == 200
    col_links = [l["href"] for l in response.json["links"] if l["rel"] == "child"]
    assert len(col_links) == 10
    next_link = next((l["href"] for l in response.json["links"] if l["rel"] == "next"), None)
    assert next_link is not None


@pytest.mark.parametrize(
    ("query", "headers"),
    (
        ("format=csv", {}),
        ({}, {"Accept": "text/csv"}),
        ("format=csv&limit=10", {}),  # even when specifying a limit, we get all the results for the moment (it could change in the futur)
    ),
)
def test_user_collection_csv(client_app_with_many_sequences, defaultAccountID, dburl, query, headers):
    """We can get the user collection as csv, either with the `format` query param or with the `Accept` header
    Note that with this, we alway get all the results, it's not limited to 1000 results"""
    client = client_app_with_many_sequences
    url = f"/api/users/{str(defaultAccountID)}/collection"

    response = client.get(url, query_string=query, headers=headers)

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/csv"
    lines = response.text.splitlines()
    assert len(lines) == 1025
    headers = lines[0].split(",")
    assert headers == [
        "id",
        "status",
        "name",
        "created",
        "updated",
        "capture_date",
        "minimum_capture_time",
        "maximum_capture_time",
        "min_x",
        "min_y",
        "max_x",
        "max_y",
        "nb_pictures",
        "length_km",
        "computed_h_pixel_density",
        "computed_gps_accuracy",
    ]


def test_user_me_collection(client_app_with_many_sequences, defaultAccountToken):
    response = client_app_with_many_sequences.get(
        f"/api/users/me/collection?limit=50", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
    )

    assert response.status_code == 200

    ctl = Collection.from_dict(response.json)

    childs = ctl.get_links("child")
    assert len(childs) == 50
