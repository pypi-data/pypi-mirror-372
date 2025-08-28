from flask import current_app
from numpy import sort
from pystac import Collection
from geovisio.utils import db, pictures
from geovisio.utils.tags import SemanticTagUpdate
from geovisio.utils.tags import TagAction
import geovisio.web.collections
from geovisio.workers import runner_pictures
from geovisio.utils.fields import Bounds, SortBy, SortByField
from geovisio.utils.sequences import STAC_FIELD_MAPPINGS, SQLDirection
from tests import conftest
from tests.conftest import STAC_VERSION, createSequence, get_tags_history, uploadPicture, waitForSequence, create_test_app
from typing import Optional
import os
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from PIL import Image
import pytest
import time
import io
import json
import psycopg
from psycopg.sql import SQL
from psycopg.rows import dict_row


@pytest.mark.parametrize(
    ("ua", "res"),
    (
        ("GeoVisioWebsite/1.0 Linux BlaBla", geovisio.web.collections.UploadClient.website),
        ("Panoramaxcli/0.5", geovisio.web.collections.UploadClient.cli),
        ("GeoVisiocli/0.5", geovisio.web.collections.UploadClient.cli),
        ("PanoramaxAPP/2.0", geovisio.web.collections.UploadClient.mobile_app),
        (None, geovisio.web.collections.UploadClient.unknown),
        ("Mozilla/5.0 (Linux)", geovisio.web.collections.UploadClient.other),
    ),
)
def test_userAgentToClient(ua, res):
    assert geovisio.web.collections.userAgentToClient(ua) == res


def test_dbSequenceToStacCollection(client):
    dbSeq = {
        "id": UUID("{12345678-1234-5678-1234-567812345678}"),
        "name": "Test sequence",
        "minx": -1.0,
        "maxx": 1.0,
        "miny": -2.0,
        "maxy": 2.0,
        "mints": datetime.fromisoformat("2020-01-01T12:50:37+00:00"),
        "maxts": datetime.fromisoformat("2020-01-01T13:30:42+00:00"),
        "created": datetime.fromisoformat("2023-01-01T12:42:00+02:00"),
        "updated": datetime.fromisoformat("2023-01-01T13:42:00+02:00"),
        "account_name": "Default account",
        "account_id": UUID("{12345678-1234-5678-0000-567812345678}"),
        "nbpic": 10,
        "nbseq": 2,
        "user_agent": "PanoramaxCLI/0.7",
        "length_km": 1.5,
        "computed_h_pixel_density": 14,
        "computed_gps_accuracy": 2.7,
    }

    res = geovisio.web.collections.dbSequenceToStacCollection(dbSeq)

    assert res
    assert res["type"] == "Collection"
    assert res["stac_version"] == STAC_VERSION
    assert res["id"] == "12345678-1234-5678-1234-567812345678"
    assert res["title"] == "Test sequence"
    assert res["description"] == "A sequence of geolocated pictures"
    assert res["providers"] == [
        {"name": "Default account", "roles": ["producer"], "id": "12345678-1234-5678-0000-567812345678"},
    ]
    assert res["keywords"] == ["pictures", "Test sequence"]
    assert res["license"] == "etalab-2.0"
    assert res["created"] == "2023-01-01T10:42:00+00:00"
    assert res["updated"] == "2023-01-01T11:42:00+00:00"
    assert res["extent"]["spatial"]["bbox"] == [[-1.0, -2.0, 1.0, 2.0]]
    assert res["extent"]["temporal"]["interval"] == [["2020-01-01T12:50:37+00:00", "2020-01-01T13:30:42+00:00"]]
    assert res["stats:items"]["count"] == 10
    assert res["geovisio:upload-software"] == "cli"
    assert res["geovisio:length_km"] == 1.5
    assert res["quality:horizontal_accuracy"] == 2.7
    assert res["quality:horizontal_accuracy_type"] == "95% confidence interval"
    assert res["summaries"]["panoramax:horizontal_pixel_density"] == [14]
    assert len(res["links"]) == 5
    l = next(l for l in res["links"] if l["rel"] == "license")
    assert l["title"] == "License for this object (etalab-2.0)"
    assert l["href"] == "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE"


def test_dbSequenceToStacCollectionEmptyTemporalInterval(client):
    dbSeq = {
        "id": UUID("{12345678-1234-5678-1234-567812345678}"),
        "name": "Test sequence",
        "minx": -1.0,
        "maxx": 1.0,
        "miny": -2.0,
        "maxy": 2.0,
        "mints": None,
        "created": datetime.fromisoformat("2023-01-01T12:42:00+02:00"),
        "account_name": "Default account",
        "account_id": UUID("{12345678-1234-5678-0000-567812345678}"),
    }

    res = geovisio.web.collections.dbSequenceToStacCollection(dbSeq)

    assert res
    assert res["type"] == "Collection"
    assert res["stac_version"] == STAC_VERSION
    assert res["id"] == "12345678-1234-5678-1234-567812345678"
    assert res["title"] == "Test sequence"
    assert res["description"] == "A sequence of geolocated pictures"
    assert res["providers"] == [
        {"name": "Default account", "roles": ["producer"], "id": "12345678-1234-5678-0000-567812345678"},
    ]
    assert res["keywords"] == ["pictures", "Test sequence"]
    assert res["license"] == "etalab-2.0"
    assert res["created"] == "2023-01-01T10:42:00+00:00"
    assert res["extent"]["spatial"]["bbox"] == [[-1.0, -2.0, 1.0, 2.0]]
    assert res["extent"]["temporal"]["interval"] == [[None, None]]
    assert res["geovisio:upload-software"] == "unknown"
    assert "quality:horizontal_accuracy" not in res
    assert "quality:horizontal_accuracy_type" not in res
    assert "summaries" not in res
    assert len(res["links"]) == 5


def test_dbSequenceToStacCollectionEmptyBbox(client):
    dbSeq = {
        "id": UUID("{12345678-1234-5678-1234-567812345678}"),
        "name": "Test sequence",
        "minx": None,
        "maxx": None,
        "miny": None,
        "maxy": None,
        "mints": datetime.fromisoformat("2020-01-01T12:50:37+00:00"),
        "maxts": datetime.fromisoformat("2020-01-01T13:30:42+00:00"),
        "created": datetime.fromisoformat("2023-01-01T12:42:00+02:00"),
        "updated": datetime.fromisoformat("2023-01-01T12:42:00+02:00"),
        "account_name": "Default account",
        "account_id": UUID("{12345678-1234-5678-0000-567812345678}"),
        "user_agent": "RandomClient",
    }

    res = geovisio.web.collections.dbSequenceToStacCollection(dbSeq)

    assert res
    assert res["type"] == "Collection"
    assert res["stac_version"] == STAC_VERSION
    assert res["id"] == "12345678-1234-5678-1234-567812345678"
    assert res["title"] == "Test sequence"
    assert res["description"] == "A sequence of geolocated pictures"
    assert res["providers"] == [
        {"name": "Default account", "roles": ["producer"], "id": "12345678-1234-5678-0000-567812345678"},
    ]
    assert res["keywords"] == ["pictures", "Test sequence"]
    assert res["license"] == "etalab-2.0"
    assert res["created"] == "2023-01-01T10:42:00+00:00"
    assert res["extent"]["spatial"]["bbox"] == [[-180.0, -90.0, 180.0, 90.0]]
    assert res["geovisio:upload-software"] == "other"

    l = next(l for l in res["links"] if l["rel"] == "license")
    assert l["title"] == "License for this object (etalab-2.0)"
    assert l["href"] == "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE"


def test_dbSequenceToStacCollectionNoLicense(no_license_app_client):
    dbSeq = {
        "id": UUID("{12345678-1234-5678-1234-567812345678}"),
        "name": "Test sequence",
        "minx": -1.0,
        "maxx": 1.0,
        "miny": -2.0,
        "maxy": 2.0,
        "mints": datetime.fromisoformat("2020-01-01T12:50:37+00:00"),
        "maxts": datetime.fromisoformat("2020-01-01T13:30:42+00:00"),
        "created": datetime.fromisoformat("2023-01-01T12:42:00+02:00"),
        "updated": datetime.fromisoformat("2023-01-01T13:42:00+02:00"),
        "account_name": "Default account",
        "account_id": UUID("{12345678-1234-5678-0000-567812345678}"),
    }

    res = geovisio.web.collections.dbSequenceToStacCollection(dbSeq)

    assert res
    assert res["type"] == "Collection"
    assert res["stac_version"] == STAC_VERSION
    assert res["id"] == "12345678-1234-5678-1234-567812345678"
    assert res["title"] == "Test sequence"
    assert res["description"] == "A sequence of geolocated pictures"
    assert res["providers"] == [
        {"name": "Default account", "roles": ["producer"], "id": "12345678-1234-5678-0000-567812345678"},
    ]
    assert res["keywords"] == ["pictures", "Test sequence"]
    assert res["license"] == "proprietary"
    assert res["created"] == "2023-01-01T10:42:00+00:00"
    assert res["updated"] == "2023-01-01T11:42:00+00:00"
    assert res["extent"]["spatial"]["bbox"] == [[-1.0, -2.0, 1.0, 2.0]]
    assert res["extent"]["temporal"]["interval"] == [["2020-01-01T12:50:37+00:00", "2020-01-01T13:30:42+00:00"]]
    assert len(res["links"]) == 4
    rels = [l for l in res["links"] if l["rel"] == "license"]
    assert not rels


def test_collectionsEmpty(client):
    response = client.get("/api/collections")

    assert response.status_code == 200
    assert len(response.json["collections"]) == 0
    assert set((l["rel"] for l in response.json["links"])) == {"root", "parent", "self"}


@conftest.SEQ_IMGS
def test_collections_hidden(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE sequences SET status = 'hidden'")
                conn.commit()

        response = client.get("/api/collections")
        assert response.status_code == 200
        assert len(response.json["collections"]) == 0


@conftest.SEQ_IMGS
def test_get_hidden_sequence(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        assert len(sequence.pictures) == 5

        # hide sequence
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200
        assert response.json["geovisio:status"] == "hidden"

        # status should be set to hidden in db
        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            seqStatus = cursor.execute("SELECT status FROM sequences WHERE id = %s", [sequence.id]).fetchone()
            assert seqStatus
            assert seqStatus[0] == "hidden"

            # we should have a trace of the sequence history
            # with who did the change, and the previous value
            r = cursor.execute("SELECT account_id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert r == [(bobAccountID, {"status": "ready"})]

        # The sequence is hidden, public call cannot see it, only Bob
        r = client.get(f"/api/collections/{sequence.id}")
        assert r.status_code == 404
        r = client.get(f"/api/collections/{sequence.id}/items")
        assert r.status_code == 404
        # sequence is not in the global list
        r = client.get("/api/collections")
        assert r.status_code == 200
        assert len(r.json["collections"]) == 0
        # even for Bob
        r = client.get("/api/collections", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert len(r.json["collections"]) == 0
        # but when we ask for deleted collections, we see it as deleted for public calls (since we consider that 'hidden' sequences are shown as 'deleted')
        r = client.get("/api/collections?filter=status='deleted' OR status='ready'")
        assert r.status_code == 200
        assert len(r.json["collections"]) == 1
        assert r.json["collections"][0]["geovisio:status"] == "deleted"
        # we also see it as deleted when querying with a IN
        # but when we ask for deleted collections, we see it as deleted
        r = client.get("/api/collections?filter=status IN ('deleted', 'ready')")
        assert r.status_code == 200
        assert len(r.json["collections"]) == 1
        assert r.json["collections"][0]["geovisio:status"] == "deleted"

        # even Bob does not see it with the right status, the right status is only show in /api/users/:bob/collection
        r = client.get(
            "/api/collections?filter=status='deleted' OR status='ready'", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert r.status_code == 200
        assert len(r.json["collections"]) == 1
        assert r.json["collections"][0]["geovisio:status"] == "deleted"
        r = client.get(f"/api/users/{bobAccountID}/collection")
        assert r.status_code == 404  # no collection for bob can be seen publicly
        # but Bob can see his collection with the right status
        r = client.get(f"/api/users/{bobAccountID}/collection", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        col = [l for l in r.json["links"] if l["rel"] == "child"]
        assert col[0]["geovisio:status"] == "hidden"

        # Bob can see the items of his collection
        r = client.get(f"/api/collections/{sequence.id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert len(r.json["features"]) == 5

        for p in sequence.pictures:
            r = client.get(f"/api/collections/{sequence.id}/items/{p.id}")
            assert r.status_code == 404

            r = client.get(f"/api/collections/{sequence.id}/items/{p.id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
            assert r.status_code == 200

        # other sequence's routes are also unavailable for public access
        r = client.get(f"/api/collections/{sequence.id}/geovisio_status")
        assert r.status_code == 404
        r = client.get(f"/api/collections/{sequence.id}/geovisio_status", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200

        # if we set the sequence back to public, it should be fine for everybody
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "true"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        assert client.get(f"/api/collections/{sequence.id}").status_code == 200
        for p in sequence.pictures:
            assert client.get(f"/api/collections/{sequence.id}/items/{p.id}").status_code == 200

        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            r = cursor.execute("SELECT account_id, previous_value_changed FROM sequences_changes ORDER BY ts", []).fetchall()
            assert r == [(bobAccountID, {"status": "ready"}), (bobAccountID, {"status": "hidden"})]

        r = client.get("/api/collections")
        assert r.status_code == 200
        assert len(r.json["collections"]) == 1
        assert next((s for s in r.json["collections"] if s["id"] == sequence.id), None) is not None

        # but when we ask for deleted collections, we do not see it as deleted
        r = client.get("/api/collections?filter=status='deleted' OR status='ready'")
        assert r.status_code == 200
        assert len(r.json["collections"]) == 1
        assert "geovisio:status" not in r.json["collections"][0]


@conftest.SEQ_IMGS
def test_get_hidden_sequence_and_pictures(datafiles, initSequenceApp, dburl, bobAccountToken):
    """
    If we:
            * hide the pictures n°1
            * hide the sequence
            * un-hide the sequence

    The pictures n°1 should stay hidden
    """
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        assert len(sequence.pictures) == 5

        # hide pic
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{sequence.pictures[0].id}",
            data={"visible": "false"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )

        r = client.get(f"/api/collections/{sequence.id}/items/{sequence.pictures[0].id}")
        assert r.status_code == 404

        # hide sequence
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        r = client.get(f"/api/collections/{sequence.id}")
        assert r.status_code == 404

        # set the sequence to visible
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "true"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200
        r = client.get(f"/api/collections/{sequence.id}")
        assert r.status_code == 200

        # but the pic is still hidden
        r = client.get(f"/api/collections/{sequence.id}/items/{sequence.pictures[0].id}")
        assert r.status_code == 404


@conftest.SEQ_IMGS
def test_patch_sequence_title(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            # Add custom metadata in sequence
            cursor.execute('UPDATE sequences SET metadata = \'{"bla": "bloub"}\'::jsonb WHERE id = %s', [sequence.id])
            conn.commit()

            # Change sequence title
            newTitle = "Un tout nouveau titre STYLÉÉÉ"
            response = client.patch(
                f"/api/collections/{sequence.id}", data={"title": newTitle}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
            )
            assert response.status_code == 200
            assert response.json["title"] == newTitle

            # Check title in DB
            seqMeta = cursor.execute("SELECT metadata FROM sequences WHERE id = %s", [sequence.id]).fetchone()[0]
            assert seqMeta["title"] == newTitle
            assert seqMeta["bla"] == "bloub"  # Check it didn't erase other metadata

            # Check title in classic GET response
            r = client.get(f"/api/collections/{sequence.id}")
            assert r.status_code == 200
            assert r.json.get("title") == newTitle


@conftest.SEQ_IMGS
def test_patch_sequence_title_status(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # Change sequence title
        newTitle = "Un tout nouveau titre STYLÉÉÉ"
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"visible": "false", "title": newTitle},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        assert response.json["title"] == newTitle
        assert response.json["geovisio:status"] == "hidden"

        # Check title in DB
        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            seqMeta, seqStatus = cursor.execute("SELECT metadata, status FROM sequences WHERE id = %s", [sequence.id]).fetchone()
            assert seqMeta["title"] == newTitle
            assert seqStatus == "hidden"

        # Check title in classic GET response
        r = client.get(f"/api/collections/{sequence.id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert r.json.get("title") == newTitle
        assert r.json.get("geovisio:status") == "hidden"


@conftest.SEQ_IMGS
def test_patch_sequence_headings(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # Change relative orientation (looking right)
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"relative_heading": 90},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            seq_changes = cursor.execute("SELECT id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert [r["previous_value_changed"] for r in seq_changes] == [
                None
            ]  # the old value was empty, so there is an entry, but without a previous value
            pic_changes = cursor.execute(
                "SELECT picture_id, sequences_changes_id, previous_value_changed FROM pictures_changes ORDER BY ts", []
            ).fetchall()
            assert {str(c.pop("picture_id")): c for c in pic_changes} == {
                sequence.pictures[0].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 349, "heading_computed": False},
                },
                sequence.pictures[1].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 11, "heading_computed": False},
                },
                sequence.pictures[2].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 1, "heading_computed": False},
                },
                sequence.pictures[3].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 350, "heading_computed": False},
                },
                sequence.pictures[4].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 356, "heading_computed": False},
                },
            }

        # Check headings in items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        features = r.json["features"]
        assert [f["properties"]["view:azimuth"] for f in features] == [114, 103, 96, 72, 72]

        # Change relative orientation (looking left)
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"relative_heading": -90},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            r = cursor.execute("SELECT previous_value_changed FROM sequences_changes", []).fetchall()
            seq_changes = cursor.execute("SELECT id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert [r["previous_value_changed"] for r in seq_changes] == [None, {"relative_heading": 90}]
            pic_changes = cursor.execute(
                "SELECT picture_id, sequences_changes_id, previous_value_changed FROM pictures_changes ORDER BY ts", []
            ).fetchall()
            assert {str(c.pop("picture_id")): c for c in pic_changes} == {
                sequence.pictures[0].id: {
                    "sequences_changes_id": seq_changes[-1]["id"],
                    "previous_value_changed": {"heading": 114},
                },
                sequence.pictures[1].id: {
                    "sequences_changes_id": seq_changes[-1]["id"],
                    "previous_value_changed": {"heading": 103},
                },
                sequence.pictures[2].id: {
                    "sequences_changes_id": seq_changes[-1]["id"],
                    "previous_value_changed": {"heading": 96},
                },
                sequence.pictures[3].id: {
                    "sequences_changes_id": seq_changes[-1]["id"],
                    "previous_value_changed": {"heading": 72},
                },
                sequence.pictures[4].id: {
                    "sequences_changes_id": seq_changes[-1]["id"],
                    "previous_value_changed": {"heading": 72},
                },
            }

        # Check headings in items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        features = r.json["features"]
        assert [f["properties"]["view:azimuth"] for f in features] == [294, 283, 276, 252, 252]

        # Invalid relative heading
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"relative_heading": 250},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Relative heading is not valid, should be an integer in degrees from -180 to 180",
            "status_code": 400,
        }
        response = client.patch(
            f"/api/collections/{sequence.id}",
            json={"relative_heading": "pouet"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Relative heading is not valid, should be an integer in degrees from -180 to 180",
            "status_code": 400,
        }
        response = client.patch(
            f"/api/collections/{sequence.id}",
            json={"relative_heading": None},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Relative heading is not valid, should be an integer in degrees from -180 to 180",
            "status_code": 400,
        }


@conftest.SEQ_IMG
def test_patch_sequence_headings_one_picture(datafiles, initSequenceApp, dburl, bobAccountToken):
    """It should be possible to patch a collection with only one picture, the resulting heading should be the relative one"""
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # Change relative orientation (looking right)
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"relative_heading": 90},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            seq_changes = cursor.execute("SELECT id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert [r["previous_value_changed"] for r in seq_changes] == [None]
            pic_changes = cursor.execute(
                "SELECT picture_id, sequences_changes_id, previous_value_changed FROM pictures_changes ORDER BY ts", []
            ).fetchall()
            assert {str(c.pop("picture_id")): c for c in pic_changes} == {
                sequence.pictures[0].id: {
                    "sequences_changes_id": seq_changes[0]["id"],
                    "previous_value_changed": {"heading": 349, "heading_computed": False},
                },
            }

        # Check headings in items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        features = r.json["features"]
        assert [f["properties"]["view:azimuth"] for f in features] == [90]


@conftest.SEQ_IMGS
def test_patch_sequence_filename_sort(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        originalPicIds = [p.id for p in sequence.pictures]

        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            # at first there should be no history
            r = cursor.execute("SELECT account_id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert r == []

        # Mess up picture metadata to have different sorts
        sorts = [0, 2, 4, 1, 3]
        with psycopg.connect(dburl, autocommit=True) as conn, conn.cursor() as cursor:
            for i, p in enumerate(originalPicIds):
                newMeta = json.dumps({"originalFileName": f"{sorts[i]}.jpg"})
                cursor.execute(
                    "UPDATE pictures SET metadata = metadata || %(meta)s::jsonb WHERE id = %(id)s",
                    {"id": p, "meta": newMeta},
                )

        # Ascending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "+filename"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        # sort order is persisted
        assert response.json["geovisio:sorted-by"] == "+filename"

        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            # we should have a trace of the sequence history
            # with who did the change, and the previous value
            r = cursor.execute("SELECT account_id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert r == [(bobAccountID, {"current_sort": None})]

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["original_file:name"] for f in r.json["features"]] == ["0.jpg", "1.jpg", "2.jpg", "3.jpg", "4.jpg"]

        # Descending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "-filename"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            r = cursor.execute("SELECT account_id, previous_value_changed FROM sequences_changes", []).fetchall()
            assert r == [(bobAccountID, {"current_sort": None}), (bobAccountID, {"current_sort": "+filename"})]

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["original_file:name"] for f in r.json["features"]] == ["4.jpg", "3.jpg", "2.jpg", "1.jpg", "0.jpg"]

        col_geom = db.fetchone(current_app, "SELECT geom FROM sequences WHERE id = %s", [sequence.id])[0]

        assert col_geom is not None


@conftest.SEQ_IMGS
def test_patch_sequence_filedate_sort(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        originalPicIds = [p.id for p in sequence.pictures]

        # Mess up picture metadata to have different sorts
        new_datetime = [
            {
                "Exif.Image.DateTimeOriginal": "2020-01-01T00:00:01",
            },
            {
                "Exif.Image.DateTimeOriginal": "2020-01-01T00:00:04",
            },
            {
                # the 3rd picture is on the exact same time as the 5th, only the subsectime original can differ them
                "Exif.Image.DateTimeOriginal": "2020-01-01T00:00:02",
                "Exif.Photo.SubSecTimeOriginal": "10",
            },
            {
                "Exif.Image.DateTimeOriginal": "2020-01-01T00:00:05",
            },
            {
                "Exif.Image.DateTimeOriginal": "2020-01-01T00:00:02",
            },
        ]
        with psycopg.connect(dburl, autocommit=True) as conn, conn.cursor() as cursor:
            for i, p in enumerate(originalPicIds):
                exif = json.dumps(new_datetime[i] | {"test:prev_rank": f"{i + 1}"})
                meta = {"ts_camera": new_datetime[i]["Exif.Image.DateTimeOriginal"]}
                if "Exif.Photo.SubSecTimeOriginal" in new_datetime[i]:
                    meta["ts_camera"] += f".{new_datetime[i]['Exif.Photo.SubSecTimeOriginal']}"
                cursor.execute(
                    "UPDATE pictures SET exif = exif || %(exif)s::jsonb, metadata = metadata || %(meta)s::jsonb WHERE id = %(id)s",
                    {"id": p, "exif": exif, "meta": json.dumps(meta)},
                )

        # before sorting check items's datetime
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["test:prev_rank"] for f in r.json["features"]] == ["1", "2", "3", "4", "5"]

        # and by default no sort is set
        r = client.get(f"/api/collections/{sequence.id}")
        assert r.status_code == 200
        assert "geovisio:sorted-by" not in r.json

        # Ascending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "+filedate"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200, response.json
        assert response.json["geovisio:sorted-by"] == "+filedate"

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["test:prev_rank"] for f in r.json["features"]] == ["1", "5", "3", "2", "4"]

        # Descending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "-filedate"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        assert response.json["geovisio:sorted-by"] == "-filedate"

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["test:prev_rank"] for f in r.json["features"]] == ["4", "2", "3", "5", "1"]


@conftest.SEQ_IMGS
def test_patch_sequence_gpsdate_sort(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        originalPicIds = [p.id for p in sequence.pictures]

        # Mess up picture metadata to have different sorts
        sorts = [0, 2, 4, 1, 3]
        with psycopg.connect(dburl, autocommit=True) as conn, conn.cursor() as cursor:
            for i, p in enumerate(originalPicIds):
                newExif = json.dumps(
                    {
                        "Exif.GPSInfo.GPSDateStamp": "2020:01:01",
                        "Exif.GPSInfo.GPSTimeStamp": f"10:00:0{sorts[i]}",
                    }
                )
                meta = json.dumps({"ts_gps": f"2020-01-01T10:00:0{sorts[i]}+00:00"})
                cursor.execute(
                    "UPDATE pictures SET exif = exif || %(exif)s::jsonb, metadata = metadata || %(meta)s WHERE id = %(id)s",
                    {"id": p, "exif": newExif, "meta": meta},
                )

        # before sorting check items's datetime
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["Exif.GPSInfo.GPSTimeStamp"] for f in r.json["features"]] == [
            "10:00:00",
            "10:00:02",
            "10:00:04",
            "10:00:01",
            "10:00:03",
        ]

        # Ascending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "+gpsdate"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["Exif.GPSInfo.GPSTimeStamp"] for f in r.json["features"]] == [
            "10:00:00",
            "10:00:01",
            "10:00:02",
            "10:00:03",
            "10:00:04",
        ]

        # Descending sort
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"sortby": "-gpsdate"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        # Check items
        r = client.get(f"/api/collections/{sequence.id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert [f["properties"]["exif"]["Exif.GPSInfo.GPSTimeStamp"] for f in r.json["features"]] == [
            "10:00:04",
            "10:00:03",
            "10:00:02",
            "10:00:01",
            "10:00:00",
        ]


def test_patch_sequence_sort_empty(app, dburl, bobAccountToken):
    """It is not an error to sort an empty sequence"""
    with app.test_client() as client:
        # Create an empty sequence
        seqLoc = conftest.createSequence(client, "test", bobAccountToken())

        # Try to re-order pictures in it
        response = client.patch(
            seqLoc,
            data={"sortby": "+gpsdate"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200


@pytest.fixture(scope="function")
def cleanup_accounts_and_global_config(dburl):
    with db.conn(current_app) as conn:
        initial_value = conn.execute(SQL("SELECT collaborative_metadata FROM configurations")).fetchone()

        yield
        conn.execute(
            SQL("UPDATE configurations SET collaborative_metadata = %(collaborative_metadata)s"),
            {"collaborative_metadata": initial_value[0]},
        )
        conn.execute(SQL("UPDATE accounts SET collaborative_metadata = null"))


@pytest.mark.parametrize(
    ("patch_payload", "owner_accept_collaborative_editing", "instance_default_collaborative_editing", "error"),
    [
        ({}, True, False, None),
        ({}, False, False, None),  # empty payload is accepted, even when collaborative editing is forbidden
        # changing the visibility or title is always forbidden
        (
            {"title": "pouet"},
            True,
            True,
            "You're not authorized to edit those fields for this sequence. Only the owner can change the visibility and the title",
        ),
        (
            {"visible": "true", "semantics": [{"key": "t", "value": "some_value"}]},
            True,
            True,
            "You're not authorized to edit those fields for this sequence. Only the owner can change the visibility and the title",
        ),
        (
            {"visible": "false", "sortby": "+gpsdate", "semantics": [{"key": "t", "value": "some_value"}]},
            True,
            True,
            "You're not authorized to edit those fields for this sequence. Only the owner can change the visibility and the title",
        ),
        # changin the sorty/relative_heading depends on the account's collaborative editing if set, else it depend on the instance's default
        ({"sortby": "+gpsdate", "semantics": [{"key": "t", "value": "some_value"}]}, True, True, None),
        ({"sortby": "+gpsdate", "semantics": [{"key": "t", "value": "some_value"}]}, None, True, None),
        (
            {"sortby": "+gpsdate", "semantics": [{"key": "t", "value": "some_value"}]},
            False,
            True,
            "You're not authorized to edit this sequence, collaborative editing is not allowed",
        ),
        (
            {"relative_heading": 12, "semantics": [{"key": "t", "value": "some_value"}]},
            None,
            False,
            "You're not authorized to edit this sequence, collaborative editing is not allowed",
        ),
        # Editing tags is always allowed, even if the user has forbidden collaborative editing
        (
            {"semantics": [{"key": "t", "value": "some_value"}]},
            False,
            False,
            None,
        ),
        (
            {"semantics": [{"key": "some_tag", "value": "some_value"}]},
            False,
            True,
            None,
        ),
    ],
)
def test_patch_collection_rights(
    app,
    cleanup_accounts_and_global_config,
    bobAccountToken,
    camilleAccountToken,
    bobAccountID,
    patch_payload,
    owner_accept_collaborative_editing,
    instance_default_collaborative_editing,
    error,
):
    with app.test_client() as client:
        # Create a sequence owned by bob
        seq_loc = conftest.createSequence(client, "test", bobAccountToken())
        seq_id = seq_loc.split("/")[-1]

        # set the configuration for bob and instance
        with db.conn(app) as conn:
            conn.execute(
                SQL("UPDATE configurations SET collaborative_metadata = %(collaborative_metadata)s"),
                {"collaborative_metadata": instance_default_collaborative_editing},
            )
            conn.execute(
                SQL("UPDATE accounts SET collaborative_metadata = %(collaborative_metadata)s WHERE id = %(id)s"),
                {"collaborative_metadata": owner_accept_collaborative_editing, "id": bobAccountID},
            )

        assert (
            conn.execute(SQL("SELECT collaborative_metadata FROM configurations")).fetchone()[0] == instance_default_collaborative_editing
        )
        # and we try to edit the collection as bobette, who is not the owner
        r = client.patch(f"/api/collections/{seq_id}", json=patch_payload, headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        if not error:
            assert r.status_code == 200, r.text
        else:
            assert r.status_code == 403, r.text
            assert r.json == {"message": error, "status_code": 403}


@conftest.SEQ_IMGS
def test_patch_collection_history(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            seq_changes = cursor.execute("SELECT id, previous_value_changed FROM sequences_changes", []).fetchall()
            # at first, no changes are recorded in the database
            assert seq_changes == []

            # Change relative orientation (looking right)
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"title": "a new title"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200

            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes", []
            ).fetchall()
            first_change = [
                {
                    "sequence_id": sequence.id,
                    "account_id": bobAccountID,
                    "previous_value_changed": {"title": "seq1"},
                }
            ]
            assert seq_changes == first_change
            pic_changes = cursor.execute("SELECT sequences_changes_id, previous_value_changed FROM pictures_changes", []).fetchall()
            assert pic_changes == []  # no associated picture_changes

            # patching again with the same value, should not change any thing, we shouldn't have any new entry
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"title": "another new title"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200
            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes ORDER by ts", []
            ).fetchall()
            second_change = first_change + [
                {
                    "sequence_id": str(sequence.id),
                    "account_id": bobAccountID,
                    "previous_value_changed": {"title": "a new title"},
                }
            ]
            assert seq_changes == second_change

            # change sort order
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"sortby": "+gpsdate"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200
            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes ORDER by ts", []
            ).fetchall()
            third_change = second_change + [
                {
                    "sequence_id": str(sequence.id),
                    "account_id": bobAccountID,
                    "previous_value_changed": {"current_sort": None},
                }
            ]
            assert seq_changes == third_change
            pic_changes = cursor.execute("SELECT sequences_changes_id, previous_value_changed FROM pictures_changes", []).fetchall()
            assert pic_changes == []  # no associated picture_changes because the sort does not affect the pictures, but sequences_pictures

            # change title and visibility in the same time
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"title": "another great title", "visible": "false"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200
            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes ORDER by ts", []
            ).fetchall()
            assert len(seq_changes) == 4
            assert seq_changes[-1] == {
                "sequence_id": sequence.id,
                "account_id": bobAccountID,
                "previous_value_changed": {"title": "another new title", "status": "ready"},
            }

            # change heading
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"relative_heading": 90},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200
            seq_changes = cursor.execute(
                "SELECT id, previous_value_changed, sequence_id::text, account_id FROM sequences_changes ORDER by ts", []
            ).fetchall()
            seq_changes_id = [s.pop("id") for s in seq_changes]
            assert len(seq_changes) == 5
            assert seq_changes[-1] == {
                "sequence_id": str(sequence.id),
                "account_id": bobAccountID,
                "previous_value_changed": None,  # Note: there is no mention of the relative headings there, because the old value was empty. I do not find that nice, but don't really know how to circle around this
            }
            # now we should have changes on the pictures, linked to the last sequence
            pic_changes = cursor.execute(
                "SELECT picture_id, sequences_changes_id, previous_value_changed FROM pictures_changes ORDER BY ts", []
            ).fetchall()
            assert {str(c.pop("picture_id")): c for c in pic_changes} == {
                sequence.pictures[0].id: {
                    "sequences_changes_id": seq_changes_id[-1],
                    "previous_value_changed": {"heading": 349, "heading_computed": False},
                },
                sequence.pictures[1].id: {
                    "sequences_changes_id": seq_changes_id[-1],
                    "previous_value_changed": {"heading": 11, "heading_computed": False},
                },
                sequence.pictures[2].id: {
                    "sequences_changes_id": seq_changes_id[-1],
                    "previous_value_changed": {"heading": 1, "heading_computed": False},
                },
                sequence.pictures[3].id: {
                    "sequences_changes_id": seq_changes_id[-1],
                    "previous_value_changed": {"heading": 350, "heading_computed": False},
                },
                sequence.pictures[4].id: {
                    "sequences_changes_id": seq_changes_id[-1],
                    "previous_value_changed": {"heading": 356, "heading_computed": False},
                },
            }


@conftest.SEQ_IMGS
def test_patch_collection_history_status_change(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            # Change visibility to hide the picture, we should log this
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"visible": "false"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200

            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes", []
            ).fetchall()
            first_change = [
                {
                    "sequence_id": sequence.id,
                    "account_id": bobAccountID,
                    "previous_value_changed": {"status": "ready"},
                }
            ]
            assert seq_changes == first_change

            # if we try to hide again the picture, nothing should be tracked as there has been no modification
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"visible": "false"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200

            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes", []
            ).fetchall()
            assert seq_changes == first_change


def test_post_collection_body_form(client):
    response = client.post("/api/collections", data={"title": "Séquence"})

    assert response.status_code == 200
    assert response.headers.get("Location").startswith("http://localhost:5000/api/collections/")
    seqId = UUID(response.headers.get("Location").split("/").pop())
    assert seqId != ""

    # Check if JSON is a valid STAC collection
    assert response.json["type"] == "Collection"
    assert response.json["id"] == str(seqId)
    assert response.json["title"] == "Séquence"

    # Check if geovisio_status is consistent
    r = client.get(f"/api/collections/{seqId}/geovisio_status")
    assert r.status_code == 200
    assert r.json == {"status": "waiting-for-process", "items": []}


def test_post_collection_body_json(client):
    response = client.post("/api/collections", json={"title": "Séquence"})

    assert response.status_code == 200
    assert response.headers.get("Location").startswith("http://localhost:5000/api/collections/")
    seqId = UUID(response.headers.get("Location").split("/").pop())
    assert seqId != ""

    # Check if JSON is a valid STAC collection
    assert response.json["type"] == "Collection"
    assert response.json["id"] == str(seqId)
    assert response.json["title"] == "Séquence"


def test_post_collection_body_json_charset(client):
    response = client.post("/api/collections", headers={"Content-Type": "application/json;charset=uft8"}, json={"title": "Séquence"})

    assert response.status_code == 200
    assert response.headers.get("Location").startswith("http://localhost:5000/api/collections/")
    seqId = UUID(response.headers.get("Location").split("/").pop())
    assert seqId != ""

    # Check if JSON is a valid STAC collection
    assert response.json["type"] == "Collection"
    assert response.json["id"] == str(seqId)
    assert response.json["title"] == "Séquence"


def test_getCollectionImportStatus_empty_collection(client):
    response = client.post("/api/collections", json={"title": "Séquence"})

    assert response.status_code == 200
    assert response.headers.get("Location").startswith("http://localhost:5000/api/collections/")
    seqId = UUID(response.headers.get("Location").split("/").pop())
    assert seqId != ""
    status = client.get(f"/api/collections/{seqId}/geovisio_status")

    assert status.status_code == 200
    assert status.json == {"items": [], "status": "waiting-for-process"}


@conftest.SEQ_IMGS_FLAT
def test_getCollectionImportStatus_hidden(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])
                conn.commit()

                response = client.get(f"/api/collections/{seqId}/geovisio_status")

                assert response.status_code == 200
                assert len(response.json["items"]) == 1
                assert response.json["items"][0]["id"] != picId
                assert response.json["items"][0]["status"] == "ready"


@conftest.SEQ_IMGS_FLAT
def test_upload_sequence(datafiles, client, dburl):
    # Create sequence
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]
    seqLocation = resPostSeq.headers["Location"]

    # Create first image
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "b1.jpg").open("rb")},
    )

    assert resPostImg1.status_code == 202

    # Create second image
    resPostImg2 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={"position": 2, "picture": (datafiles / "b2.jpg").open("rb")},
    )

    assert resPostImg2.status_code == 202

    # Check upload status
    conftest.waitForSequence(client, seqLocation)

    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            dbSeq = cursor.execute("SELECT status, geom FROM sequences where id = %s", [seqId]).fetchone()
            assert dbSeq
            # Check sequence is ready
            assert dbSeq[0] == "ready"
            # the sequence geometry is empty since the 2 pictures are too far apart.
            assert dbSeq[1] is None

    resGetSeq = client.get(f"/api/collections/{seqId}")
    assert resGetSeq.status_code == 200

    # the sequence should have some metadata computed
    seq = resGetSeq.json

    assert seq["extent"]["spatial"] == {"bbox": [[-1.9499731060073981, 48.13939279199841, -1.9491245819090675, 48.139852239480945]]}
    assert seq["extent"]["temporal"]["interval"] == [["2015-04-25T13:36:17+00:00", "2015-04-25T13:37:48+00:00"]]
    assert seq["summaries"]["panoramax:horizontal_pixel_density"] == [64]

    # 2 pictures should be in the collections
    r = client.get(f"/api/collections/{seqId}/items")
    assert r.status_code == 200

    assert len(r.json["features"]) == 2
    # both pictures should be ready
    assert r.json["features"][0]["properties"]["geovisio:status"] == "ready"
    assert r.json["features"][1]["properties"]["geovisio:status"] == "ready"

    # the pictures should have the original filename and size as metadata
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            blurred = cursor.execute("SELECT id, metadata FROM pictures").fetchall()
            assert blurred and len(blurred) == 2
            blurred = {str(p[0]): p[1] for p in blurred}
            assert os.path.getsize(datafiles / "b1.jpg") == blurred[resPostImg1.json["id"]]["originalFileSize"]
            assert {
                "make": "OLYMPUS IMAGING CORP.",
                "type": "flat",
                "model": "SP-720UZ",
                "width": 4288,
                "height": 3216,
                "focal_length": 4.66,
                "field_of_view": 67,
                "blurredByAuthor": False,
                "originalFileName": "b1.jpg",
                "originalFileSize": 2731046,
                "crop": None,
                "altitude": None,
                "tz": "CEST",
                "pitch": None,
                "roll": None,
            }.items() <= blurred[resPostImg1.json["id"]].items()
            assert os.path.getsize(datafiles / "b2.jpg") == blurred[resPostImg2.json["id"]]["originalFileSize"]
            assert {
                "make": "OLYMPUS IMAGING CORP.",
                "type": "flat",
                "model": "SP-720UZ",
                "width": 4288,
                "height": 3216,
                "focal_length": 4.66,
                "field_of_view": 67,
                "blurredByAuthor": False,
                "originalFileName": "b2.jpg",
                "originalFileSize": 2896575,
                "crop": None,
                "altitude": None,
                "tz": "CEST",
                "pitch": None,
                "roll": None,
            }.items() <= blurred[resPostImg2.json["id"]].items()


@pytest.fixture()
def removeDefaultAccount(dburl):
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            accountID = cursor.execute("UPDATE accounts SET is_default = false WHERE is_default = true RETURNING id").fetchone()
            assert accountID

            conn.commit()
            yield
            # put back the account at the end of the test
            cursor.execute("UPDATE accounts SET is_default = true WHERE id = %s", [accountID[0]])


def test_upload_sequence_noDefaultAccount(client, dburl, removeDefaultAccount):
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 500
    assert resPostSeq.json == {"message": "No default account defined, please contact your instance administrator", "status_code": 500}


@conftest.SEQ_IMGS
def test_get_collection_thumbnail_first_pic_hidden(datafiles, initSequenceApp, dburl, bobAccountToken, defaultAccountToken):
    """ "
    If the first pic is hidden, the owner of the sequence should still be able to see it as the thumbnail,
    but all other users should see another pic as the thumbnail
    """
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # change the first pic visibility
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{sequence.pictures[0].id}",
            data={"visible": "false"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        response = client.get(f"/api/collections/{sequence.id}/thumb.jpg")
        assert response.status_code == 200
        assert response.content_type == "image/jpeg"
        img = Image.open(io.BytesIO(response.get_data()))
        assert img.size == (500, 300)

        # non logged users should not see the same picture
        first_pic_thumb = client.get(f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg")
        assert first_pic_thumb.status_code == 403  # this picture should not be visible to the other users

        second_pic_thumb = client.get(f"/api/pictures/{str(sequence.pictures[1].id)}/thumb.jpg")
        assert second_pic_thumb.status_code == 200  # the second picture is not hidden and should be visible and be the thumbnail
        assert response.data == second_pic_thumb.data

        # same thing for a logged user that is not the owner
        first_pic_thumb = client.get(
            f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
        )
        assert first_pic_thumb.status_code == 403

        second_pic_thumb = client.get(
            f"/api/pictures/{str(sequence.pictures[1].id)}/thumb.jpg", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
        )
        assert second_pic_thumb.status_code == 200
        assert response.data == second_pic_thumb.data

        owner_thumbnail = client.get(f"/api/collections/{sequence.id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert owner_thumbnail.status_code == 200
        assert owner_thumbnail.content_type == "image/jpeg"
        owner_first_pic_thumbnail = client.get(
            f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert owner_first_pic_thumbnail.status_code == 200
        assert owner_thumbnail.data == owner_first_pic_thumbnail.data  # the owner should see the first pic


@conftest.SEQ_IMGS
def test_get_collection_thumbnail_all_pics_hidden(datafiles, initSequenceApp, dburl, bobAccountToken, defaultAccountToken):
    """ "
    If the all pics are hidden, the owner of the sequence should still be able to see a the thumbnail,
    but all other users should not have any thumbnails
    """
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # change the first pic visibility
        for p in sequence.pictures:
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{str(p.id)}",
                data={"visible": "false"},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            assert response.status_code == 200

        # non logged users should not see a thumbnail
        response = client.get(f"/api/collections/{sequence.id}/thumb.jpg")
        assert response.status_code == 404

        for p in sequence.pictures:
            # the pictures should not be visible to the any other users, logged or not
            # specific hidden pictures will result on 403, not 404
            first_pic_thumb = client.get(f"/api/pictures/{str(p.id)}/thumb.jpg")
            assert first_pic_thumb.status_code == 403
            first_pic_thumb = client.get(
                f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
            )
            assert first_pic_thumb.status_code == 403

        # but the owner should see it
        owner_thumbnail = client.get(f"/api/collections/{sequence.id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert owner_thumbnail.status_code == 200
        assert owner_thumbnail.content_type == "image/jpeg"
        owner_first_pic_thumbnail = client.get(
            f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert owner_first_pic_thumbnail.status_code == 200
        assert owner_thumbnail.data == owner_first_pic_thumbnail.data  # the owner should see the first pic


@conftest.SEQ_IMGS
def test_get_collection_thumbnail_sequence_hidden(datafiles, initSequenceApp, dburl, bobAccountToken, defaultAccountToken):
    """ "
    If the sequence is hidden, the owner of the sequence should still be able to see a the thumbnail,
    but all other users should not have any thumbnails
    """
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # change the sequence visibility
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        # non logged users should not see a thumbnail
        response = client.get(f"/api/collections/{sequence.id}/thumb.jpg")
        assert response.status_code == 404

        for p in sequence.pictures:
            # the pictures should not be visible to the any other users, logged or not
            # specific hidden pictures will result on 403, not 404
            first_pic_thumb = client.get(f"/api/pictures/{str(p.id)}/thumb.jpg")
            assert first_pic_thumb.status_code == 403
            first_pic_thumb = client.get(
                f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
            )
            assert first_pic_thumb.status_code == 403

        # but the owner should see it
        owner_thumbnail = client.get(f"/api/collections/{sequence.id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert owner_thumbnail.status_code == 200
        assert owner_thumbnail.content_type == "image/jpeg"
        owner_first_pic_thumbnail = client.get(
            f"/api/pictures/{sequence.pictures[0].id}/thumb.jpg", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert owner_first_pic_thumbnail.status_code == 200
        assert owner_thumbnail.data == owner_first_pic_thumbnail.data  # the owner should see the first pic


def _wait_for_pics_deletion(pics_id, dburl):
    with psycopg.connect(dburl) as conn:
        waiting_time = 0.1
        total_time = 0
        nb_pics = 0
        while total_time < 10:
            nb_pics = conn.execute("SELECT count(*) FROM pictures WHERE id = ANY(%(pics)s)", {"pics": pics_id}).fetchone()

            # we wait for the collection and all its pictures to be ready
            if nb_pics and not nb_pics[0]:
                return
            time.sleep(waiting_time)
            total_time += waiting_time
        assert False, f"All pictures not deleted ({nb_pics} remaining)"


@conftest.SEQ_IMGS
def test_delete_sequence(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        # before the delete, we can query the seq
        response = client.get(f"/api/collections/{sequence.id}")
        assert response.status_code == 200

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert len(response.json["features"]) == 5
        assert first_pic_id in [f["id"] for f in response.json["features"]]

        assert os.path.exists(
            datafiles / "derivates" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8] / first_pic_id[9:]
        )
        assert os.path.exists(datafiles / "permanent" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8])

        authorized_header = {"Authorization": f"Bearer {bobAccountToken()}"}
        response = client.delete(f"/api/collections/{sequence.id}", headers=authorized_header)
        assert response.status_code == 204

        # The sequence or its pictures should not be returned in any response
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        response = client.get(f"/api/collections/{sequence.id}")
        assert response.status_code == 404

        # even the user shoudn't see anything
        response = client.get(f"/api/collections/{sequence.id}", headers=authorized_header)
        assert response.status_code == 404
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}", headers=authorized_header)
        assert response.status_code == 404
        response = client.get(f"/api/collections/{sequence.id}/thumbnail", headers=authorized_header)
        assert response.status_code == 404
        response = client.get(f"/api/collections/{sequence.id}/thumbnail")
        assert response.status_code == 404

        # we should't see this collection in the list of all collections (loggued or not)
        response = client.get("/api/collections")
        assert response.status_code == 200 and response.json["collections"] == []
        response = client.get("/api/collections", headers=authorized_header)
        assert response.status_code == 200 and response.json["collections"] == []

        # we shouldn't be able to add pictures to this collection
        response = client.post(
            f"/api/collections/{sequence.id}/items",
            data={"position": 101, "picture": (datafiles / "seq1" / "1.jpg").open("rb")},
            headers=authorized_header,
        )
        assert response.status_code == 404
        assert response.json == {"message": "The collection has been deleted, impossible to add pictures to it", "status_code": 404}

        # we shouldn't be able to edit this collection
        response = client.patch(
            f"/api/collections/{sequence.id}",
            data={"visible": "false"},
            headers=authorized_header,
        )
        assert response.status_code == 404
        assert response.json == {"message": f"Collection {sequence.id} wasn't found in database", "status_code": 404}

        # but we should still see it when asking for its status (this can be discussed, if it raises issues)
        status = client.get(f"/api/collections/{sequence.id}/geovisio_status")
        assert status.json["status"] == "deleted"
        assert all(p.get("status") in [None, "waiting-for-delete", "preparing"] for p in status.json["items"]), [
            p.get("status") for p in status.json["items"]
        ]

        with psycopg.connect(dburl) as conn:
            seq = conn.execute("SELECT status FROM sequences WHERE id = %s", [sequence.id]).fetchone()
            assert seq and seq[0] == "deleted"

            # Note: we shouldn't see this when filtering by the function, even for the user
            seq = conn.execute(
                "SELECT status FROM sequences WHERE id = %s AND is_sequence_visible_by_user(sequences, %s)", [sequence.id, bobAccountID]
            ).fetchone()
            assert not seq

            pic_status = conn.execute(
                "SELECT distinct(status) FROM pictures WHERE id = ANY(%(pics)s)", {"pics": [p.id for p in sequence.pictures]}
            ).fetchall()

            # pics are either already deleted or waiting deleting
            assert pic_status == [] or pic_status == [("waiting-for-delete",)]

        # async job should delete at one point all the pictures
        _wait_for_pics_deletion(pics_id=[p.id for p in sequence.pictures], dburl=dburl)

        # check that all files have correctly been deleted since it was the only sequence
        assert os.listdir(datafiles / "derivates") == []
        assert os.listdir(datafiles / "permanent") == []

        # even after pic delete, the sequence is still there, but marked as deleted
        status = client.get(f"/api/collections/{sequence.id}/geovisio_status")
        assert status.json == {"items": [], "status": "deleted"}


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
def test_delete_1_sequence_over_2(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    """2 sequences available, and delete of them, we should not mess with the other sequence"""
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)
        assert len(sequence) == 2

        initial_updated_at = None
        with psycopg.connect(dburl) as conn:
            res = conn.execute("SELECT updated_at FROM sequences WHERE id = %s", [sequence[0].id]).fetchone()
            assert res
            initial_updated_at = res[0]

        # before the delete, we can query both seq
        for seq in sequence:
            response = client.get(f"/api/collections/{seq.id}")
            assert response.status_code == 200

            response = client.get(f"/api/collections/{seq.id}/items")
            assert response.status_code == 200

        for s in sequence:
            for p in s.pictures:
                assert os.path.exists(p.get_derivate_dir(datafiles))
                assert os.path.exists(p.get_permanent_file(datafiles))

        # we delete the first sequence
        response = client.delete(f"/api/collections/{sequence[0].id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 204

        # The sequence or its pictures should not be returned in any response
        response = client.get(f"/api/collections/{sequence[0].id}/items/{sequence[0].pictures[0].id}")
        assert response.status_code == 404

        response = client.get(f"/api/collections/{sequence[0].id}")
        assert response.status_code == 404

        # everything is still fine for the other sequence
        assert client.get(f"/api/collections/{sequence[1].id}/items/{sequence[1].pictures[0].id}").status_code == 200
        assert client.get(f"/api/collections/{sequence[1].id}").status_code == 200

        # the sequence shouldn't be returned when listing all sequences
        def col_ids(r):
            return set([c["id"] for c in r.json["collections"]])

        response = client.get("/api/collections")
        assert response.status_code == 200 and col_ids(response) == {sequence[1].id}

        response = client.get("/api/collections", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200 and col_ids(response) == {sequence[1].id}

        # nor in the user's collections
        response = client.get(f"/api/users/{bobAccountID}/collection")
        assert response.status_code == 200 and [c["id"] for c in response.json["links"] if c["rel"] == "child"] == [sequence[1].id]
        response = client.get(f"/api/users/{bobAccountID}/collection", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200 and [c["id"] for c in response.json["links"] if c["rel"] == "child"] == [sequence[1].id]

        # but we should be able to see the collection when asking for deleted pictures
        response = client.get("/api/collections?filter=status='deleted' OR status='ready'")
        assert response.status_code == 200 and col_ids(response) == {sequence[0].id, sequence[1].id}
        first_col = next(c for c in response.json["collections"] if c["id"] == sequence[0].id)
        # even deleted col should be valid stac, but marked as deleted
        _ = Collection.from_dict(first_col)
        assert first_col["geovisio:status"] == "deleted"
        # not deleted collection shouldn't have the status
        not_deleted_col = next(c for c in response.json["collections"] if c["id"] == sequence[1].id)
        assert "geovisio:status" not in not_deleted_col

        # and by querying only for deleted collection, we should only have the deleted collection
        response = client.get("/api/collections?filter=status='deleted'")
        assert response.status_code == 200 and col_ids(response) == {sequence[0].id}
        assert response.json["collections"][0]["geovisio:status"] == "deleted"

        # the pagination links should also have the filter query param
        response = client.get("/api/collections?filter=status IN ('deleted','ready')&limit=1")
        assert response.status_code == 200
        pagination_links = {l["rel"]: l["href"] for l in response.json["links"] if l["rel"] in {"prev", "next", "first", "last"}}
        assert pagination_links.keys() == {"next", "last"}  # first page, so no prev/first
        for href in pagination_links.values():
            assert "status+IN+('deleted','ready')" in href

        # and the links should be valid
        response = client.get(pagination_links["next"])
        assert response.status_code == 200
        response = client.get(pagination_links["last"])
        assert response.status_code == 200

        with psycopg.connect(dburl) as conn:
            seq = conn.execute("SELECT status, updated_at FROM sequences WHERE id = %s", [sequence[0].id]).fetchone()
            assert seq and seq[0] == "deleted"
            assert seq[1] > initial_updated_at  # the updated_at should have been updated with the delete time

            pic_status = conn.execute(
                "SELECT distinct(status) FROM pictures WHERE id = ANY(%(pics)s)", {"pics": [p.id for p in sequence[0].pictures]}
            ).fetchall()

            # pics are either already deleted or waiting deleting
            assert pic_status == [] or pic_status == [("waiting-for-delete",)]

        # async job should delete at one point all the pictures
        _wait_for_pics_deletion(pics_id=[p.id for p in sequence[0].pictures], dburl=dburl)

        for p in sequence[0].pictures:
            assert not os.path.exists(p.get_derivate_dir(datafiles))
            assert not os.path.exists(p.get_permanent_file(datafiles))
        for p in sequence[1].pictures:
            assert os.path.exists(p.get_derivate_dir(datafiles))
            assert os.path.exists(p.get_permanent_file(datafiles))


@conftest.SEQ_IMGS
def test_delete_sequence_with_pic_still_waiting_for_process(datafiles, tmp_path, initSequenceApp, dburl, bobAccountToken):
    """Deleting a sequence with pictures that are still waiting to be processed should be fine (and the picture should be removed from the process queue)"""
    with (
        create_test_app(
            {
                "TESTING": True,
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "SECRET_KEY": "a very secret key",
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
            }
        ) as app,
        app.test_client() as client,
        psycopg.connect(dburl) as conn,
    ):
        token = bobAccountToken()
        seq_location = conftest.createSequence(client, os.path.basename(datafiles), jwtToken=token)
        pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, jwtToken=token)
        sequence = conftest.getPictureIds(dburl)[0]

        r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
        assert r and r[0] == 1

        r = conn.execute("SELECT id, status FROM pictures").fetchall()
        assert r and list(r) == [(UUID(pic_id), "waiting-for-process")]

        assert not os.path.exists(sequence.pictures[0].get_derivate_dir(datafiles))
        assert os.path.exists(sequence.pictures[0].get_permanent_file(datafiles))

        response = client.delete(f"/api/collections/{sequence.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204

        # since there are no background worker, the deletion is not happening, but the picture should be marked for deletion
        r = conn.execute("SELECT picture_id, picture_to_delete_id, task FROM job_queue").fetchall()
        assert r and r == [(None, UUID(pic_id), "delete")]

        # and the picture deleted right away
        r = conn.execute("SELECT count(*) FROM pictures").fetchone()
        assert r and r[0] == 0

        # pic should not have been deleted, since we background worker is there
        assert os.path.exists(sequence.pictures[0].get_permanent_file(datafiles))

        # we start the runner picture
        w = runner_pictures.PictureProcessor(app=app, stop=True)
        w.process_jobs()
        conftest.waitForAllJobsDone(app)

        r = conn.execute("SELECT * FROM job_queue").fetchall()
        assert r == []
        r = conn.execute("SELECT count(*) FROM pictures").fetchone()
        assert r and r[0] == 0

        assert not os.path.exists(sequence.pictures[0].get_permanent_file(datafiles))
        assert not os.path.exists(sequence.pictures[0].get_derivate_dir(datafiles))


def _wait_for_pic_worker(pic_id, dburl):
    with psycopg.connect(dburl) as conn:
        waiting_time = 0.1
        total_time = 0
        pic_status = 0
        while total_time < 20:
            pic_status = conn.execute("SELECT 1 FROM job_history WHERE picture_id = %(pic)s", {"pic": pic_id}).fetchone()

            if pic_status:
                return
            time.sleep(waiting_time)
            total_time += waiting_time
        assert False, "Pictures not 'preparing'"


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_delete_sequence_with_pic_being_processed(datafiles, tmp_path, initSequenceApp, dburl, bobAccountToken, monkeypatch):
    """Deleting a sequence with pictures that are currently processed shoudn't be a problem, the picture should be deleted after the process is finished"""

    def mockCreateBlurredHDPictureFactory(datafiles):
        """Emulate a slow blur process"""

        def mockCreateBlurredHDPicture(fs, blurApi, pictureBytes, outputFilename, keep_unblured_parts=False):
            print("waiting for picture blurring")
            time.sleep(5)
            print("blurring picture")
            with open(datafiles / "1_blurred.jpg", "rb") as f:
                fs.writebytes(outputFilename, f.read())
                return pictures.BlurredPicture(image=Image.open(datafiles / "1_blurred.jpg"))

        return mockCreateBlurredHDPicture

    from geovisio import utils

    monkeypatch.setattr(utils.pictures, "createBlurredHDPicture", mockCreateBlurredHDPictureFactory(datafiles))

    with (
        create_test_app(
            {
                "TESTING": True,
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "SECRET_KEY": "a very secret key",
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "API_BLUR_URL": "https://geovisio-blurring.net",
            }
        ) as app,
        app.test_client() as client,
        psycopg.connect(dburl) as conn,
    ):
        token = bobAccountToken()
        seq_location = conftest.createSequence(client, os.path.basename(datafiles), jwtToken=token)
        pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, jwtToken=token)
        sequence = conftest.getPictureIds(dburl)[0]

        r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
        assert r and r[0] == 1

        _wait_for_pic_worker(pic_id, dburl)

        # there should be only one job, and it should not be finished yet
        r = conn.execute("SELECT job_task, finished_at FROM job_history WHERE picture_id = %s", [pic_id]).fetchall()
        assert r and len(r) == 1
        assert r[0][0] == "prepare" and r[0][1] is None

        response = client.delete(f"/api/collections/{sequence.id}", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 204

        # The preparing process is quite long but the DELETE call should block until all tasks are finished
        r = conn.execute("SELECT picture_id, picture_to_delete_id, task FROM job_queue").fetchall()
        assert r and r == [(None, UUID(pic_id), "delete")]

        r = conn.execute("SELECT count(*) FROM pictures").fetchone()
        assert r and r[0] == 0  # the picture should be deleted

        time.sleep(2)  # waiting a bit for the deletion task

        # pic should have been deleted
        assert not os.path.exists(sequence.pictures[0].get_permanent_file(datafiles))
        assert not os.path.exists(sequence.pictures[0].get_derivate_dir(datafiles))

        r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
        assert r and r[0] == 0
        r = conn.execute("SELECT count(*) FROM pictures").fetchone()
        assert r and r[0] == 0


@pytest.mark.parametrize(
    ("min", "max", "direction", "expected", "additional_filters"),
    (
        ##############################################
        # In ascending order
        #
        # In middle of dataset bounds
        [
            "2021-01-01",
            "2021-01-15",
            SQLDirection.ASC,
            {
                "first": "sortby=%2Bcreated",
                "prev": "sortby=%2Bcreated&page=created+%3C+'2021-01-01'",
                "next": "sortby=%2Bcreated&page=created+%3E+'2021-01-15'",
                "last": "sortby=%2Bcreated&page=created+%3C%3D+'2024-12-31'",
            },
            None,
        ],
        # Matches dataset bounds
        ["2020-01-01", "2024-12-31", SQLDirection.ASC, {}, None],
        # Starting on dataset bounds
        [
            "2020-01-01",
            "2021-01-15",
            SQLDirection.ASC,
            {"next": "sortby=%2Bcreated&page=created+%3E+'2021-01-15'", "last": "sortby=%2Bcreated&page=created+%3C%3D+'2024-12-31'"},
            None,
        ],
        # Ending on dataset bounds
        [
            "2021-01-01",
            "2024-12-31",
            SQLDirection.ASC,
            {
                "first": "sortby=%2Bcreated",
                "prev": "sortby=%2Bcreated&page=created+%3C+'2021-01-01'",
            },
            None,
        ],
        ##############################################
        # In descending order
        #
        # In middle of dataset bounds
        [
            "2021-01-01",
            "2021-01-15",
            SQLDirection.DESC,
            {
                "first": "sortby=-created",
                "prev": "sortby=-created&page=created+%3E+'2021-01-15'",
                "next": "sortby=-created&page=created+%3C+'2021-01-01'",
                "last": "sortby=-created&page=created+%3E%3D+'2020-01-01'",
            },
            None,
        ],
        # Matches dataset bounds
        ["2020-01-01", "2024-12-31", SQLDirection.DESC, {}, None],
        # Starting on dataset bounds
        [
            "2020-01-01",
            "2021-01-15",
            SQLDirection.DESC,
            {
                "first": "sortby=-created",
                "prev": "sortby=-created&page=created+%3E+'2021-01-15'",
            },
            None,
        ],
        # Ending on dataset bounds
        [
            "2021-01-01",
            "2024-12-31",
            SQLDirection.DESC,
            {"next": "sortby=-created&page=created+%3C+'2021-01-01'", "last": "sortby=-created&page=created+%3E%3D+'2020-01-01'"},
            None,
        ],
        # additional_filters
        [
            "2021-01-01",
            "2021-01-15",
            SQLDirection.ASC,
            {
                "first": "filter=status%3D'deleted'&sortby=%2Bcreated",
                "prev": "sortby=%2Bcreated&filter=status%3D'deleted'&page=created+%3C+'2021-01-01'",
                "next": "sortby=%2Bcreated&filter=status%3D'deleted'&page=created+%3E+'2021-01-15'",
                "last": "sortby=%2Bcreated&filter=status%3D'deleted'&page=created+%3C%3D+'2024-12-31'",
            },
            "status='deleted'",
        ],
    ),
)
def test_get_pagination_links(dburl, tmp_path, min, max, direction, expected, additional_filters):
    with create_test_app(
        {
            "TESTING": True,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "SECRET_KEY": "a very secret key",
            "SERVER_NAME": "geovisio.fr",
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
            "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
        }
    ):
        min_creation, max_creation = "2020-01-01", "2024-12-31"
        if direction == SQLDirection.ASC:
            dset_bounds = Bounds(first=[min_creation], last=[max_creation])
            bounds = Bounds(first=[min], last=[max])
        else:
            # when direction is reversed, the bounds are reversed too
            dset_bounds = Bounds(first=[max_creation], last=[min_creation])
            bounds = Bounds(first=[max], last=[min])
        res = geovisio.utils.sequences.get_pagination_links(
            route="stac_collections.getUserCollection",
            routeArgs={"limit": 50, "userId": "1234"},
            sortBy=SortBy(
                fields=[
                    SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=direction),
                ]
            ),
            datasetBounds=dset_bounds,
            dataBounds=bounds,
            additional_filters=additional_filters,
        )

        assert len(expected.items()) == len(res)

        for expectedRelType, expectedRelHref in expected.items():
            resRelHref = next(l["href"] for l in res if l["rel"] == expectedRelType)
            assert resRelHref == f"http://geovisio.fr/api/users/1234/collection?limit=50&{expectedRelHref}"


# TODO add test on concurent collection modification, history should be good


@conftest.SEQ_IMGS
def test_collection_pics_aggregated_stats(app, client, bobAccountToken, datafiles, dburl):
    jwt_token = bobAccountToken()
    s = createSequence(client, "some sequence title", jwtToken=jwt_token)

    @dataclass
    class AggStats:
        min_ts: Optional[str]
        max_ts: Optional[str]
        nb_pic: int

        @staticmethod
        def get():
            with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
                r = cursor.execute("select min_picture_ts, max_picture_ts, nb_pictures from sequences;").fetchone()
                assert r
                return AggStats(
                    min_ts=r[0].isoformat() if r[0] else None,
                    max_ts=r[1].isoformat() if r[1] else None,
                    nb_pic=r[2],
                )

    # at first, there is nothing in the collection
    assert AggStats.get() == AggStats(min_ts=None, max_ts=None, nb_pic=0)

    pic1_id = uploadPicture(client, s, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, jwtToken=jwt_token)
    waitForSequence(client, s)
    assert AggStats.get() == AggStats(min_ts="2021-07-29T09:16:54+00:00", max_ts="2021-07-29T09:16:54+00:00", nb_pic=1)

    # upload a 2nd picture, stats should be updated
    pic2_id = uploadPicture(client, s, open(datafiles / "2.jpg", "rb"), "2.jpg", 2, jwtToken=jwt_token)
    waitForSequence(client, s)
    assert AggStats.get() == AggStats(min_ts="2021-07-29T09:16:54+00:00", max_ts="2021-07-29T09:16:56+00:00", nb_pic=2)

    # hide first pic do not change anything
    response = client.patch(
        f"{s}/items/{pic1_id}",
        data={"visible": "false"},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert response.status_code == 200
    assert AggStats.get() == AggStats(min_ts="2021-07-29T09:16:54+00:00", max_ts="2021-07-29T09:16:56+00:00", nb_pic=2)

    # DELETE pic 2, stat updated
    response = client.delete(
        f"{s}/items/{pic2_id}",
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert response.status_code == 204
    assert AggStats.get() == AggStats(min_ts="2021-07-29T09:16:54+00:00", max_ts="2021-07-29T09:16:54+00:00", nb_pic=1)

    # unhidding first pic does not change anything
    response = client.patch(
        f"{s}/items/{pic1_id}",
        data={"visible": "true"},
        headers={"Authorization": f"Bearer {jwt_token}"},
    )
    assert response.status_code == 200
    assert AggStats.get() == AggStats(min_ts="2021-07-29T09:16:54+00:00", max_ts="2021-07-29T09:16:54+00:00", nb_pic=1)


def test_collectionsCSVEmpty(client, bobAccountID):
    """Empty collections should be get you only the headers"""
    response = client.get(f"/api/users/{bobAccountID}/collection?format=csv")

    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/csv"
    assert (
        response.text
        == """id,status,name,created,updated,capture_date,minimum_capture_time,maximum_capture_time,min_x,min_y,max_x,max_y,nb_pictures,length_km,computed_h_pixel_density,computed_gps_accuracy
"""
    )


@conftest.SEQ_IMGS
def test_collectionsCSVOneEltCollection(client, datafiles, bobAccountID, bobAccountToken):
    """Collection with 1 element should be valid"""
    ids = conftest.upload_files(client, [datafiles / "1.jpg"], wait=True, jwtToken=bobAccountToken())
    us = conftest.get_upload_set(client, ids.id)
    seq_id = UUID(us["associated_collections"][0]["id"])

    response = client.get(f"/api/users/{bobAccountID}/collection?format=csv")
    assert response.status_code == 200, response.text
    assert response.headers.get("Content-Type") == "text/csv"
    assert len(response.text.splitlines()) == 2


@pytest.mark.parametrize(
    ("params", "error"),
    (
        ("filter=status%3D'ready'", "CSV export does not support filters"),
        ("sortby=created", "CSV export does not support sorting by anything but creation date"),
        ("sortby=-updated", "CSV export does not support sorting by anything but creation date"),
        ("page=created+%3E+'2021-01-01'", "CSV export does not support pagination"),
    ),
)
def test_collectionsCSVLimitedCapabilities(client, bobAccountID, params, error):
    """Collection with 1 element should be valid"""
    response = client.get(f"/api/users/{bobAccountID}/collection?format=csv&{params}")
    assert response.status_code == 400
    assert response.json == {"message": error, "status_code": 400}


def test_collectionsCSVWithoutPics(client, bobAccountID, bobAccountToken):
    """Collection with no pics should be valid"""
    conftest.createSequence(client, "a_sequence", jwtToken=bobAccountToken())

    response = client.get(f"/api/users/{bobAccountID}/collection?format=csv", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 200  # should be valid
    assert response.headers.get("Content-Type") == "text/csv"
    assert len(response.text.splitlines()) == 2


def test_patch_collections_update_tags(client, bobAccountToken, defaultAccountToken):
    """Tags can be added/deleted on a collection"""
    seq_loc = conftest.createSequence(client, "a_sequence", jwtToken=bobAccountToken())

    seq_id = seq_loc.split("/")[-1]

    patch_response = client.patch(
        f"/api/collections/{seq_id}",
        json={
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "another_value"},
                {"key": "some_tag", "value": "some_value"},
            ]
        },
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert patch_response.status_code == 200, patch_response.text
    assert patch_response.json["semantics"] == [
        {"key": "some_other_tag", "value": "some_other_value"},
        {"key": "some_tag", "value": "another_value"},
        {"key": "some_tag", "value": "some_value"},
    ]
    get_resp = client.get(f"/api/collections/{seq_id}")
    assert get_resp.status_code == 200
    assert get_resp.json == patch_response.json
    # all those updated tags should be in the history
    assert get_tags_history() == {
        "sequences": [
            (
                UUID(seq_id),
                "bob",
                [
                    {"action": "add", "key": "some_other_tag", "value": "some_other_value"},
                    {"action": "add", "key": "some_tag", "value": "another_value"},
                    {"action": "add", "key": "some_tag", "value": "some_value"},
                ],
            ),
        ],
    }
    # we can also remove tags
    patch_response = client.patch(
        f"/api/collections/{seq_id}",
        json={
            "semantics": [
                {"key": "some_tag", "value": "some_value", "action": "delete"},
                {"key": "some_other_tag", "value": "some_other_value", "action": "delete"},
                {"key": "another_great_tag", "value": "we can also add tags in the meantime"},
                {
                    "key": "a non existing tag",
                    "value": "some_other_value",
                    "action": "delete",
                },  # for the moment it's not an error to delete a non existing tag
            ]
        },
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},  # and a different user can edit the tags
    )
    assert patch_response.status_code == 200, patch_response.text
    assert patch_response.json["semantics"] == [
        {"key": "another_great_tag", "value": "we can also add tags in the meantime"},
        {"key": "some_tag", "value": "another_value"},
    ]
    get_resp = client.get(f"/api/collections/{seq_id}")
    assert get_resp.status_code == 200
    assert get_resp.json == patch_response.json
    # all those updated tags should be in the history
    assert get_tags_history() == {
        "sequences": [
            (
                UUID(seq_id),
                "bob",
                [
                    {"action": "add", "key": "some_other_tag", "value": "some_other_value"},
                    {"action": "add", "key": "some_tag", "value": "another_value"},
                    {"action": "add", "key": "some_tag", "value": "some_value"},
                ],
            ),
            (
                UUID(seq_id),
                "Default account",
                [
                    {"key": "some_tag", "value": "some_value", "action": "delete"},
                    {"key": "some_other_tag", "value": "some_other_value", "action": "delete"},
                    {"key": "another_great_tag", "value": "we can also add tags in the meantime", "action": "add"},
                    {
                        "key": "a non existing tag",
                        "value": "some_other_value",
                        "action": "delete",
                    },  # for the moment we also keep the non existing tag removal
                ],
            ),
        ],
    }


@conftest.SEQ_IMGS
def test_patch_collection_update_tags_no_logged(datafiles, initSequenceApp, dburl):
    """As for the other editing APIs, for the moment you need to be logged in to edit tags"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        patch_response = client.patch(
            f"/api/collections/{sequence.id}",
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value"},
                    {"key": "some_tag", "value": "another_value"},
                    {"key": "some_other_tag", "value": "some_other_value"},
                ]
            },
        )
        assert patch_response.status_code == 401, patch_response.text
        assert patch_response.json == {"message": "Authentication is mandatory"}


@conftest.SEQ_IMGS
def test_patch_collection_update_tags_another_user(datafiles, initSequenceApp, dburl, defaultAccountToken):
    """As for the other editing APIs anyone can edit the tags"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        patch_response = client.patch(
            f"/api/collections/{sequence.id}",
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value"},
                ]
            },
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
        )
        assert patch_response.status_code == 200, patch_response.text
        assert patch_response.json["semantics"] == [
            {"key": "some_tag", "value": "some_value"},
        ]

        # we can also find the tags when querying for several collections
        get_resp = client.get("/api/collections")
        assert get_resp.status_code == 200
        assert get_resp.json["collections"][0]["semantics"] == [
            {"key": "some_tag", "value": "some_value"},
        ]
