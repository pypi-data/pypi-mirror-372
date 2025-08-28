from pystac import Collection
from dateutil.parser import parse as dateparser
from geovisio import tokens
from geovisio.utils import db
from tests import conftest
from pystac import ItemCollection
from tests.conftest import STAC_VERSION
from urllib.parse import urlencode
from datetime import date
from uuid import UUID
from PIL import Image
import pytest
import io
from psycopg.rows import dict_row
import json
from psycopg.sql import SQL
import psycopg
from flask import current_app
import re
from geovisio import create_app

"""
Module like tests/test_web_collections, but to reduce testing time, the data is loaded only once for all tests.

No tests should change the data!
"""


@pytest.fixture(scope="module", autouse=True)
def fixed_data_app(dburl, fs):

    app = create_app(
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
            "API_MAIN_PAGE": "https://panoramax.osm.fr/",
            "API_VIEWER_PAGE": "https://panoramax.osm.fr/a-cool-viewer/",
        }
    )
    yield app
    app.pool.close()


@pytest.fixture(scope="module")
def bobAccountID(fixed_data_app):
    with fixed_data_app.app_context():
        accountID = db.fetchone(current_app, "SELECT id from accounts WHERE name = 'bob'")
        if accountID:
            return accountID[0]
        accountID = db.fetchone(current_app, "INSERT INTO accounts (name) VALUES ('bob') RETURNING id")
        assert accountID
        return accountID[0]


@pytest.fixture(scope="module")
def bobAccountToken(bobAccountID, fixed_data_app):
    with fixed_data_app.app_context():
        accountToken = db.fetchone(current_app, "SELECT id FROM tokens WHERE account_id = %s", [bobAccountID])
        assert accountToken
        return tokens._generate_jwt_token(accountToken[0])


@pytest.fixture(scope="module")
def defaultAccountToken(fixed_data_app):
    with fixed_data_app.app_context():
        accountToken = db.fetchone(
            current_app, "SELECT tokens.id FROM tokens JOIN accounts a ON a.id = tokens.account_id WHERE a.is_default"
        )
        assert accountToken
        return tokens._generate_jwt_token(accountToken[0])


@pytest.fixture(scope="module")
def app_data(fixed_data_app, bobAccountToken):
    """
    Fixture returning an app's client with many sequences loaded.
    Data shouldn't be modified by tests as it will be shared by several tests
    """
    import pathlib

    datadir = pathlib.Path(conftest.FIXTURE_DIR)
    pics = [
        datadir / "1.jpg",
        datadir / "2.jpg",
        datadir / "3.jpg",
        datadir / "4.jpg",
        datadir / "5.jpg",
    ]

    conftest.app_with_data(app=fixed_data_app, sequences={"seq1": pics}, jwtToken=bobAccountToken)
    return fixed_data_app


@pytest.fixture(scope="function")
def client(app_data):
    """Create a context/client for each tests, so nothing is persisted (in flask.g for example) between tests.
    This is especially important for babel that has some cache in g"""
    with app_data.app_context(), app_data.test_client() as client:
        yield client


def test_collections(client):
    response = client.get("/api/collections")
    data = response.json

    assert response.status_code == 200

    assert len(data["collections"]) == 1
    assert data["links"] == [
        {"href": "http://localhost:5000/api/", "rel": "root", "title": "Instance catalog", "type": "application/json"},
        {"href": "http://localhost:5000/api/", "rel": "parent", "type": "application/json"},
        {"href": "http://localhost:5000/api/collections", "rel": "self", "type": "application/json"},
    ]

    Collection.from_dict(data["collections"][0])

    assert data["collections"][0]["type"] == "Collection"
    assert data["collections"][0]["stac_version"] == STAC_VERSION
    assert len(data["collections"][0]["id"]) > 0
    assert len(data["collections"][0]["title"]) > 0
    assert data["collections"][0]["description"] == "A sequence of geolocated pictures"
    assert len(data["collections"][0]["keywords"]) > 0
    assert len(data["collections"][0]["license"]) > 0
    assert len(data["collections"][0]["extent"]["spatial"]["bbox"][0]) == 4
    assert len(data["collections"][0]["extent"]["temporal"]["interval"][0]) == 2
    assert len(data["collections"][0]["links"]) == 5
    assert data["collections"][0]["created"].startswith(date.today().isoformat())
    assert data["collections"][0]["stats:items"]["count"] == 5
    assert "stats:collections" not in data["collections"][0]


def test_collections_rss(client):
    # With query string
    response = client.get("/api/collections", query_string={"format": "rss"})
    assert response.status_code == 200
    assert response.data.startswith(b"""<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" """)

    # With Accept header
    response = client.get("/api/collections", headers={"Accept": "application/rss+xml"})
    assert response.status_code == 200
    assert response.data.startswith(b"""<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" """)

    # Check content formatting
    pattern = re.compile(
        b"""<\?xml version="1\.0" encoding="UTF-8"\?>
<rss version="2\.0" xmlns:dc="http://purl\.org/dc/elements/1\.1/" xmlns:content="http://purl\.org/rss/1\.0/modules/content/" xmlns:georss="http://www\.georss\.org/georss"><channel><title>GeoVisio collections</title><link>https://panoramax\.osm\.fr/</link><description>List of collections from this GeoVisio server</description><language>en</language><lastBuildDate>[A-Za-z]{3}, [0-9]{2} [A-Za-z]{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT</lastBuildDate><generator>GeoVisio</generator><docs>https://cyber\.harvard\.edu/rss/rss\.html</docs><image><url>http://localhost:5000/static/img/logo\.png</url><title>GeoVisio logo</title><link>https://panoramax\.osm\.fr/</link></image><item><title>seq1</title><link>https://panoramax\.osm\.fr/a-cool-viewer/#focus=map&amp;map=18/49\.00688961988304/1\.9191854417991367</link><description>Sequence "seq1" by "bob" was captured on [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}\.</description><author>bob</author><pubDate>[A-Za-z]{3}, [0-9]{2} [A-Za-z]{3} [0-9]{4} [0-9]{2}:[0-9]{2}:[0-9]{2} GMT</pubDate><enclosure url="http://localhost:5000/api/collections/[0-9a-f-]{36}/thumb\.jpg" length="" type="image/jpeg"></enclosure><guid isPermaLink="true">http://localhost:5000/api/collections/[0-9a-f-]{36}</guid><georss:point>1\.9191854417991367 49\.00688961988304</georss:point><content:encoded>
\t\t\t\t\t&lt;p&gt;
\t\t\t\t\t\t&lt;img src="http://localhost:5000/api/collections/[0-9a-f-]{36}/thumb\.jpg" /&gt;&lt;br /&gt;
\t\t\t\t\t\tSequence "seq1" by "bob" was captured on [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}\+[0-9]{2}:[0-9]{2}\.&lt;br /&gt;
\t\t\t\t\t\t&lt;a href="https://panoramax\.osm\.fr/a-cool-viewer/#focus=map&amp;map=18/49\.00688961988304/1\.9191854417991367"&gt;View on the map&lt;/a&gt; - &lt;a href="http://localhost:5000/api/collections/[0-9a-f-]{36}"&gt;JSON metadata&lt;/a&gt;
\t\t\t\t\t&lt;/p&gt;\n\t\t\t\t</content:encoded></item></channel></rss>"""
    )

    assert pattern.match(response.data)


def test_collections_rss_i18n_fr(client):
    # Check translation
    response = client.get("/api/collections", headers={"Accept": "application/rss+xml", "Accept-Language": "fr_FR,fr,en"})
    assert response.status_code == 200
    assert response.data.startswith(b"""<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" """)
    assert b"<language>fr</language>" in response.data
    assert b"Liste des" in response.data


def test_collections_rss_i18n_de(client):
    response = client.get("/api/collections", headers={"Accept": "application/rss+xml", "Accept-Language": "de"})
    assert response.status_code == 200
    assert response.data.startswith(b"""<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" """)
    assert b"<language>de</language>" in response.data
    assert b"Liste der Sequenzen von diesem" in response.data


def test_collections_pagination_outalimit(client):
    response = client.get("/api/collections?limit=50&created_after=2100-01-01T10:00:00Z")
    assert response.status_code == 400
    assert response.json == {"message": "There is no collection created after 2100-01-01 10:00:00+00:00", "status_code": 400}

    response = client.get("/api/collections?limit=50&created_before=2000-01-01T10:00:00Z")
    assert response.status_code == 400
    assert response.json == {"message": "There is no collection created before 2000-01-01 10:00:00+00:00", "status_code": 400}

    response = client.get("/api/collections?limit=-1")
    assert response.status_code == 400
    assert response.json == {"message": "limit parameter should be an integer between 1 and 1000", "status_code": 400}

    response = client.get("/api/collections?limit=1001")
    assert response.status_code == 400
    assert response.json == {"message": "limit parameter should be an integer between 1 and 1000", "status_code": 400}


def test_collections_invalid_created_after(client):
    response = client.get("/api/collections?limit=50&created_after=pouet")
    assert response.status_code == 400
    assert response.json == {
        "details": {"error": "Unknown string format: pouet"},
        "message": "Invalid `created_after` argument",
        "status_code": 400,
    }


def test_collections_bbox(client):
    response = client.get("/api/collections?bbox=0,0,1,1")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 0

    response = client.get("/api/collections?bbox=1.312864,48.004817,3.370054,49.357521")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1


def test_collections_datetime(client):
    response = client.get("/api/collections?datetime=../2021-01-01")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 0

    response = client.get("/api/collections?datetime=2021-01-01/..")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1

    # Note that sequences are filtered by day, not time
    #   due to computed_capture_date field in sequences table
    response = client.get("/api/collections?datetime=2021-07-29T09:00:00Z/2021-07-29T10:00:00Z")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1


def test_collections_filter(client):
    response = client.get("/api/collections?filter=updated >= '2030-12-31'")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 0

    response = client.get("/api/collections?filter=updated >= '2018-01-01'")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1

    response = client.get("/api/collections?filter=updated BETWEEN '2018-01-01' AND '2030-12-31'")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1

    response = client.get("/api/collections?filter=created >= '2023-01-01'")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 1

    response = client.get("/api/collections?filter=created <= '2023-01-01' AND updated >= '2018-01-01'")
    assert response.status_code == 200
    assert len(response.json["collections"]) == 0

    response = client.get("/api/collections?filter=status == 'private'")  # Invalid operator
    assert response.status_code == 400

    response = client.get("/api/collections?filter=bad_field = 'private'")  # Not allowed field
    assert response.status_code == 400


def test_collectionMissing(client):
    response = client.get("/api/collections/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_collectionById(client, dburl):
    seqId, picId = conftest.getFirstPictureIds(dburl)

    response = client.get("/api/collections/" + str(seqId))
    data = response.json

    assert response.status_code == 200
    clc = Collection.from_dict(data)
    assert clc.extra_fields["stats:items"]["count"] == 5
    assert clc.extra_fields["geovisio:length_km"] == 0.009


def test_invalid_sequence_hide(client, dburl, bobAccountToken):
    sequence = conftest.getPictureIds(dburl)[0]

    # hide pic
    response = client.patch(
        f"/api/collections/{sequence.id}", data={"visible": "invalid_value"}, headers={"Authorization": f"Bearer {bobAccountToken}"}
    )
    assert response.status_code == 400


def test_hide_unexisting_seq(client, bobAccountToken):
    response = client.patch(
        "/api/collections/00000000-0000-0000-0000-000000000000",
        data={"visible": "false"},
        headers={"Authorization": f"Bearer {bobAccountToken}"},
    )
    assert response.status_code == 404
    assert response.json == {"message": "Collection 00000000-0000-0000-0000-000000000000 wasn't found in database", "status_code": 404}


def test_empty_sequence_patch(client, dburl, bobAccountToken):
    sequence = conftest.getPictureIds(dburl)[0]

    response = client.patch(
        f"/api/collections/{sequence.id}/items/{sequence.pictures[0].id}", headers={"Authorization": f"Bearer {bobAccountToken}"}
    )
    # changing no value is valid, and should result if the same thing as a get (but with a 304 - not-modified instead of a 200)
    assert response.status_code == 304


def test_anomynous_sequence_patch(client, dburl):
    """Patching a sequence as an unauthentified user should result in an error"""
    sequence = conftest.getPictureIds(dburl)[0]

    response = client.patch(
        f"/api/collections/{sequence.id}",
    )
    assert response.status_code == 401
    assert response.json == {"message": "Authentication is mandatory"}


def test_set_already_visible_sequence(client, dburl, bobAccountToken):
    """Setting an already visible sequence to visible is valid, and change nothing"""
    sequence = conftest.getPictureIds(dburl)[0]

    # hide sequence
    p = client.patch(f"/api/collections/{sequence.id}", data={"visible": "true"}, headers={"Authorization": f"Bearer {bobAccountToken}"})
    assert p.status_code == 200
    r = client.get(f"/api/collections/{sequence.id}")
    assert r.status_code == 200


def test_not_owned_sequence_patch(client, dburl, defaultAccountToken):
    """Patching a sequence that does not belong to us should result in an error"""
    sequence = conftest.getPictureIds(dburl)[0]

    response = client.patch(
        f"/api/collections/{sequence.id}", data={"visible": "true"}, headers={"Authorization": f"Bearer {defaultAccountToken}"}
    )
    assert response.status_code == 403


def test_getCollectionImportStatus_noseq(client):
    response = client.get("/api/collections/00000000-0000-0000-0000-000000000000/geovisio_status")
    assert response.status_code == 404


def test_getCollectionImportStatus_ready(client, dburl):
    seqId, picId = conftest.getFirstPictureIds(dburl)

    response = client.get(f"/api/collections/{seqId}/geovisio_status")

    assert response.status_code == 200
    assert len(response.json["items"]) == 5

    for i in response.json["items"]:
        assert len(i) == 6
        assert UUID(i["id"]) is not None
        assert i["rank"] > 0
        assert i["status"] == "ready"
        assert i["processed_at"].startswith(date.today().isoformat())
        assert i["nb_errors"] == 0
        assert i["processing_in_progress"] is False


def test_get_collection_thumbnail(client, dburl):
    seqId, picId = conftest.getFirstPictureIds(dburl)

    response = client.get(f"/api/collections/{str(seqId)}/thumb.jpg")
    assert response.status_code == 200
    assert response.content_type == "image/jpeg"
    img = Image.open(io.BytesIO(response.get_data()))
    assert img.size == (500, 300)

    first_pic_thumb = client.get(f"/api/pictures/{str(picId)}/thumb.jpg")
    assert first_pic_thumb.data == response.data


def test_delete_sequence_no_auth(client, dburl):
    """A sequence cannot be deleted with authentication"""
    sequence = conftest.getPictureIds(dburl)
    response = client.delete(f"/api/collections/{sequence[0].id}")
    assert response.status_code == 401
    assert response.json == {"message": "Authentication is mandatory"}


def test_delete_sequence_not_owned(client, dburl, defaultAccountToken):
    """A sequence cannot be deleted with authentication"""
    sequence = conftest.getPictureIds(dburl)
    response = client.delete(f"/api/collections/{sequence[0].id}", headers={"Authorization": f"Bearer {defaultAccountToken}"})
    assert response.status_code == 403
    assert response.json == {"message": "You're not authorized to edit this sequence", "status_code": 403}


def test_user_collection(client, bobAccountID):
    # Get user ID
    response = client.get(f"/api/users/{bobAccountID}/collection")
    data = response.json
    userName = "bob"
    assert response.status_code == 200
    assert data["type"] == "Collection"
    ctl = Collection.from_dict(data)
    assert len(ctl.links) > 0
    assert ctl.title == userName + "'s sequences"
    assert ctl.id == f"user:{bobAccountID}"
    assert ctl.description == "List of all sequences of user " + userName
    assert ctl.extent.spatial.to_dict() == {"bbox": [[1.9191854417991367, 49.00688961988304, 1.919199780601944, 49.00697341759938]]}
    assert ctl.extent.temporal.to_dict() == {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:17:02Z"]]}
    assert ctl.get_links("self")[0].get_absolute_href() == f"http://localhost:5000/api/users/{bobAccountID}/collection"

    assert ctl.extra_fields["stats:items"]["count"] == 5
    assert ctl.extra_fields["stats:collections"]["count"] == 1
    assert ctl.extra_fields["geovisio:length_km"] == 0.009
    assert data["providers"] == [{"name": userName, "roles": ["producer"], "id": str(bobAccountID)}]
    assert ctl.stac_extensions == [
        "https://stac-extensions.github.io/stats/v0.2.0/schema.json",
        "https://stac.linz.govt.nz/v0.0.15/quality/schema.json",
        "https://stac-extensions.github.io/timestamps/v1.1.0/schema.json",
    ]

    # both `updated` and `created` should be valid date
    dateparser(data["updated"])
    dateparser(data["created"])
    assert data["created"].startswith(date.today().isoformat())
    assert data["updated"].startswith(date.today().isoformat())

    # Check links
    childs = ctl.get_links("child")
    assert len(childs) == 1
    child = childs[0]
    assert child.title is not None
    assert child.extra_fields["id"] is not None
    assert child.get_absolute_href() == "http://localhost:5000/api/collections/" + child.extra_fields["id"]
    assert child.extra_fields["extent"]["temporal"] == {"interval": [["2021-07-29T09:16:54+00:00", "2021-07-29T09:17:02+00:00"]]}
    assert child.extra_fields["extent"]["spatial"] == {
        "bbox": [[1.9191854417991367, 49.00688961988304, 1.919199780601944, 49.00697341759938]]
    }
    assert child.extra_fields["stats:items"]["count"] == 5
    assert child.extra_fields["geovisio:length_km"] == 0.009
    # each collection also have an updated/created date
    assert child.extra_fields["updated"].startswith(date.today().isoformat())
    assert child.extra_fields["created"].startswith(date.today().isoformat())

    # Also test filter parameter works
    response = client.get(f"/api/users/{bobAccountID}/collection?filter=created >= '2020-01-01' AND updated >= '2023-01-01'")
    data = response.json
    assert response.status_code == 200
    ctl = Collection.from_dict(data)
    childs = ctl.get_links("child")
    assert len(childs) == 1

    # No pagination links as there is no more data to display
    assert len(ctl.get_links("first")) == 0
    assert len(ctl.get_links("prev")) == 0
    assert len(ctl.get_links("next")) == 0
    assert len(ctl.get_links("last")) == 0


def test_user_collection_pagination_outalimit(client, bobAccountID):
    response = client.get(f"/api/users/{bobAccountID}/collection?limit=50&filter=created > '2100-01-01T10:00:00Z'")
    assert response.status_code == 404
    assert response.json == {"message": "No matching sequences found", "status_code": 404}

    response = client.get(f"/api/users/{bobAccountID}/collection?limit=50&filter=created < '2000-01-01T10:00:00Z'")
    assert response.status_code == 404
    assert response.json == {"message": "No matching sequences found", "status_code": 404}

    response = client.get(f"/api/users/{bobAccountID}/collection?limit=-1")
    assert response.status_code == 400
    assert response.json == {"message": "limit parameter should be an integer between 1 and 1000", "status_code": 400}

    response = client.get(f"/api/users/{bobAccountID}/collection?limit=1001")
    assert response.status_code == 400
    assert response.json == {"message": "limit parameter should be an integer between 1 and 1000", "status_code": 400}


def test_user_collection_filter_bbox(client, bobAccountID):
    response = client.get(f"/api/users/{bobAccountID}/collection?bbox=0,0,1,1")
    assert response.status_code == 200
    assert [l for l in response.json["links"] if l["rel"] == "child"] == []

    response = client.get(f"/api/users/{bobAccountID}/collection?bbox=1.312864,48.004817,3.370054,49.357521")
    assert response.status_code == 200

    childs = [l for l in response.json["links"] if l["rel"] == "child"]
    assert len(childs) == 1


@pytest.mark.parametrize(
    ("query", "headers"),
    (
        ("format=csv", {}),
        ({}, {"Accept": "text/csv"}),
    ),
)
def test_user_collection_csv(client, bobAccountID, dburl, query, headers):
    response = client.get(f"/api/users/{bobAccountID}/collection", query_string=query, headers=headers)
    seq = db.fetchone(current_app, "SELECT id, inserted_at, updated_at FROM sequences", row_factory=dict_row)
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/csv"
    lines = response.text.splitlines()
    assert len([c for c in lines if c]) == 2
    fields = lines[1].split(",")
    # we trunk the inserted/updated at fields, since psycopg make round it a bit
    assert fields[3][:19] == seq["inserted_at"].isoformat().replace("T", " ")[:19]
    assert fields[4][:19] == seq["updated_at"].isoformat().replace("T", " ")[:19]
    assert fields == [
        str(seq["id"]),
        "ready",
        "seq1",
        fields[3],
        fields[4],
        "2021-07-29",
        "2021-07-29 09:16:54+00",
        "2021-07-29 09:17:02+00",
        "1.9191854417991367",
        "49.00688961988304",
        "1.919199780601944",
        "49.00697341759938",
        "5",
        "0.009",
        "16",
        "4",
    ]


@pytest.mark.parametrize(
    ("query", "headers"),
    (
        ({"format": "csv"}, {}),
        ({}, {"Accept": "text/csv"}),
    ),
)
def test_logged_user_collection_csv(client, bobAccountToken, query, headers):
    response = client.get(
        "/api/users/me/collection",
        query_string=query,
        headers={"Authorization": f"Bearer {bobAccountToken}"} | headers,
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/csv"
    lines = response.text.splitlines()
    assert len([c for c in lines if c]) == 2


intersectsGeojson1 = json.dumps(
    {
        "type": "Polygon",
        "coordinates": [
            [
                [1.9191969931125639, 49.00691313179996],
                [1.9191332906484602, 49.00689685694783],
                [1.9191691651940344, 49.00687024535389],
                [1.919211409986019, 49.006892018477274],
                [1.9191969931125639, 49.00691313179996],
            ]
        ],
    }
)
intersectsGeojson2 = json.dumps({"type": "Point", "coordinates": [1.919185442, 49.00688962]})
intersectsGeojsonPointNear = json.dumps(
    {"type": "Point", "coordinates": [1.9191855, 49.0068897]}
)  # round a bit the coordinates, we should still find the first pic


@pytest.mark.parametrize(
    ("query", "httpCode", "validRanks"),
    (
        ({}, 200, [5, 4, 3, 2, 1]),
        ({"limit": 2}, 200, [5, 4]),
        ({"limit": -1}, 400, None),
        ({"limit": 99999}, 400, None),
        ({"limit": "bla"}, 400, None),
        ({"bbox": [0, 0, 1, 1]}, 200, []),
        ({"bbox": "[0,0,1,1"}, 200, []),
        ({"bbox": [1]}, 400, None),
        ({"bbox": [1.919185, 49.00688, 1.919187, 49.00690]}, 200, [1]),
        ({"datetime": "2021-07-29T11:16:54+02"}, 200, [1]),
        ({"datetime": "2021-07-29T00:00:00Z/.."}, 200, [5, 4, 3, 2, 1]),
        ({"datetime": "../2021-07-29T00:00:00Z"}, 200, []),
        ({"datetime": "2021-01-01T00:00:00Z/2021-07-29T11:16:58+02"}, 200, [3, 2, 1]),
        ({"datetime": "2021-01-01T00:00:00Z/"}, 400, None),
        ({"datetime": "/2021-01-01T00:00:00Z"}, 400, None),
        ({"datetime": ".."}, 400, None),
        ({"datetime": "2021-07-29TNOTATIME"}, 400, None),
        ({"intersects": intersectsGeojson1}, 200, [1, 2]),
        ({"intersects": intersectsGeojson2}, 200, [1]),
        ({"intersects": intersectsGeojsonPointNear}, 200, [1]),
        ({"intersects": "{ 'broken': ''"}, 400, None),
        ({"intersects": "{ 'type': 'Feature' }"}, 400, None),
        ({"ids": [1, 2]}, 200, [2, 1]),
        ({"collections": "[:seq_id]"}, 200, [5, 4, 3, 2, 1]),
        ({"collections": [":seq_id"]}, 200, [5, 4, 3, 2, 1]),
        ({"collections": "[:seq_id, :seq_id]"}, 200, [5, 4, 3, 2, 1]),
        ({"collections": [":seq_id", ":seq_id"]}, 200, [5, 4, 3, 2, 1]),
        ({"sortby": "updated"}, 200, [1, 2, 3, 4, 5]),
        ({"sortby": "-updated"}, 200, [5, 4, 3, 2, 1]),
        ({"sortby": "-pouet"}, 400, None),
        ({"sortby": "distance_to"}, 400, None),  # it's not possible to sort by distance_to yet
        ({"datetime": "2021-01-01T00:00:00Z/2021-07-29T11:16:58+02", "sortby": "updated"}, 200, [1, 2, 3]),
    ),
)
@conftest.SEQ_IMGS
def test_search(client, dburl, query, httpCode, validRanks):
    seq = conftest.getPictureIds(dburl)[0]
    # Transform input ranks into picture ID to pass to query
    if "ids" in query:
        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                r = cursor.execute(
                    "SELECT array_to_json(array_agg(pic_id::varchar)) FROM sequences_pictures WHERE rank = ANY(%s)", [query["ids"]]
                ).fetchone()
                assert r
                query["ids"] = json.dumps(r[0])

    # Retrieve sequence ID to pass into collections in query
    if "collections" in query:
        if isinstance(query["collections"], list):
            query["collections"] = [c.replace(":seq_id", seq.id) for c in query["collections"]]
        else:
            query["collections"] = query["collections"].replace(":seq_id", seq.id)

    response = client.get(f"/api/search?{urlencode(query)}")

    assert response.status_code == httpCode, response.text

    if httpCode != 200:
        return
    clc = ItemCollection.from_dict(response.json)

    # all search response should have a link to the root of the stac catalog
    assert response.json["links"] == [
        {"rel": "root", "href": "http://localhost:5000/api/", "title": "Instance catalog", "type": "application/json"}
    ]
    assert validRanks is not None
    assert len(clc) == len(validRanks)

    if len(validRanks) > 0:
        with psycopg.connect(dburl) as db:
            rank_by_pic = {r[0]: r[1] for r in db.execute("SELECT pic_id::varchar, rank FROM sequences_pictures")}
            pic_by_rank = {i: r for r, i in rank_by_pic.items()}

            res_ranks = [rank_by_pic[item.id] for item in clc]
            assert res_ranks == validRanks

            for rank in validRanks:
                item = next(it for it in clc.items if it.id == pic_by_rank[rank])
                next_link = next((l.target.split("/").pop() for l in item.links if l.rel == "next"), None)
                prev_link = next((l.target.split("/").pop() for l in item.links if l.rel == "prev"), None)
                if rank > 1:
                    assert rank_by_pic[prev_link] == rank - 1
                else:
                    assert prev_link is None
                if rank < 5:
                    assert rank_by_pic[next_link] == rank + 1
                else:
                    assert next_link is None

    if "limit" in query:
        assert len(clc) == query["limit"]


def test_search_post(client):
    response = client.post("/api/search", json={"limit": 1, "intersects": intersectsGeojson1})
    data = response.json

    assert response.status_code == 200
    clc = ItemCollection.from_dict(data)
    assert len(clc) == 1


def test_search_by_geom_sorted(client, dburl):
    # when searching by geometry, the results should be order by the proximity with the center of the geometry
    seq = conftest.getPictureIds(dburl)[0]

    with psycopg.connect(dburl, row_factory=dict_row) as db:
        big_geom = db.execute("SELECT id, ST_AsGeoJson(ST_Expand(geom, 1)) AS big_geom_around FROM pictures").fetchall()
        big_geom = {str(b["id"]): b for b in big_geom}
    assert len(big_geom) == 5

    # if I search with a geometry centerd on the first pic, it should be the first result
    response = client.post("/api/search", json={"intersects": big_geom[seq.pictures[0].id]["big_geom_around"]})
    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[0].id, seq.pictures[1].id, seq.pictures[2].id, seq.pictures[3].id, seq.pictures[4].id]

    response = client.post("/api/search", json={"intersects": big_geom[seq.pictures[1].id]["big_geom_around"]})
    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[1].id, seq.pictures[0].id, seq.pictures[2].id, seq.pictures[3].id, seq.pictures[4].id]

    response = client.post("/api/search", json={"intersects": big_geom[seq.pictures[3].id]["big_geom_around"]})
    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[3].id, seq.pictures[4].id, seq.pictures[2].id, seq.pictures[1].id, seq.pictures[0].id]


def test_search_by_bbox_sorted(client, dburl):
    seq = conftest.getPictureIds(dburl)[0]

    with psycopg.connect(dburl, row_factory=dict_row) as db:
        big_bbox = db.execute(
            """
            WITH bboxes AS (
                SELECT p.id, ST_Expand(p.geom, 1) AS bbox
                FROM pictures p
                JOIN sequences_pictures sp ON p.id = sp.pic_id
                ORDER BY sp.rank
            )
            SELECT id, ST_XMin(bbox) AS xmin, ST_XMax(bbox) AS xmax, ST_YMin(bbox) AS ymin, ST_YMax(bbox) AS ymax
            FROM bboxes
        """
        ).fetchall()

        big_bbox = {str(b["id"]): b for b in big_bbox}
    assert len(big_bbox) == 5

    def _get_bbox(i):
        return [big_bbox[i]["xmin"], big_bbox[i]["ymin"], big_bbox[i]["xmax"], big_bbox[i]["ymax"]]

    response = client.post("/api/search", json={"bbox": _get_bbox(seq.pictures[0].id)})

    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[0].id, seq.pictures[1].id, seq.pictures[2].id, seq.pictures[3].id, seq.pictures[4].id]

    response = client.post("/api/search", json={"bbox": _get_bbox(seq.pictures[1].id)})
    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[1].id, seq.pictures[0].id, seq.pictures[2].id, seq.pictures[3].id, seq.pictures[4].id]

    response = client.post("/api/search", json={"bbox": _get_bbox(seq.pictures[3].id)})
    assert response.status_code == 200
    ids = [i["id"] for i in response.json["features"]]
    assert ids == [seq.pictures[3].id, seq.pictures[4].id, seq.pictures[2].id, seq.pictures[1].id, seq.pictures[0].id]


def test_search_post_list_params(client, dburl):
    ids = conftest.getFirstPictureIds(dburl)

    response = client.post("/api/search", json={"limit": 1, "collections": [ids[0]]})
    data = response.json

    assert response.status_code == 200
    clc = ItemCollection.from_dict(data)
    assert len(clc) == 1

    response = client.post("/api/search", json={"limit": 1, "ids": [ids[1]]})
    data = response.json

    assert response.status_code == 200
    clc = ItemCollection.from_dict(data)
    assert len(clc) == 1


def test_search_place_360(client, dburl):
    sequence = conftest.getPictureIds(dburl)[0]

    # Should return pictures around (as they are 360°)
    response = client.get("/api/search?place_position=1.9191859,49.0068908&place_distance=0-10&limit=2")
    assert response.status_code == 200, response
    pics = response.json["features"]
    assert len(pics) == 2
    assert pics[0]["id"] == sequence.pictures[0].id
    assert pics[1]["id"] == sequence.pictures[1].id

    # Different pictures retrieved with a higher distance range
    response = client.get("/api/search?place_position=1.9191859,49.0068908&place_distance=5-20&limit=2")
    assert response.status_code == 200, response
    pics = response.json["features"]
    assert len(pics) == 2
    assert pics[0]["id"] == sequence.pictures[3].id
    assert pics[1]["id"] == sequence.pictures[4].id

    # No impact of fov tolerance on results (as we're 360°)
    response = client.get("/api/search?place_position=1.9191859,49.0068908&place_distance=5-20&place_fov_tolerance=2&limit=2")
    assert response.status_code == 200, response
    pics = response.json["features"]
    assert len(pics) == 2
    assert pics[0]["id"] == sequence.pictures[3].id
    assert pics[1]["id"] == sequence.pictures[4].id

    # Works with POST as well
    response = client.post("/api/search", json={"limit": 2, "place_position": [1.9191859, 49.0068908], "place_distance": "0-10"})
    assert response.status_code == 200, response
    pics = response.json["features"]
    assert len(pics) == 2
    assert pics[0]["id"] == sequence.pictures[0].id
    assert pics[1]["id"] == sequence.pictures[1].id
