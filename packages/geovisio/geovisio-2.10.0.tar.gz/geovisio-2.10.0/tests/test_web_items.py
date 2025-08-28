from pathlib import Path
import re
import os
from uuid import UUID
from datetime import date, datetime, timedelta
import psycopg
from pystac import ItemCollection, Item
from flask import current_app, json
from psycopg.rows import dict_row
from psycopg.sql import SQL
import requests
import pytest
import math
import itertools
from urllib.parse import urlencode
import time
from geopic_tag_reader import reader
from geovisio.utils import db
import geovisio.utils.pictures
from . import conftest
from .conftest import getFirstPictureIds, create_test_app, FIXTURE_DIR, waitForAllJobsDone, get_tags_history, getPictureIds


@conftest.SEQ_IMGS
def test_items(datafiles, initSequenceApp, dburl, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client:

        seqId, _ = getFirstPictureIds(dburl)

        response = client.get("/api/collections/" + str(seqId) + "/items")
        data = response.json

        assert response.status_code == 200

        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 5
        assert len(data["links"]) == 3
        assert data["features"][0]["properties"]["original_file:name"] == "1.jpg"
        assert data["features"][0]["properties"]["original_file:size"] == 3296115
        assert data["features"][0]["properties"]["geovisio:rank_in_collection"] == 1

        clc = ItemCollection.from_dict(data)
        assert len(clc) == 5

        # Check if items have next/prev picture info
        i = 0
        for item in clc:
            nbPrev = len([l for l in item.links if l.rel == "prev"])
            nbNext = len([l for l in item.links if l.rel == "next"])
            if i == 0:
                assert nbPrev == 0
                assert nbNext == 1
            elif i == len(clc) - 1:
                assert nbPrev == 1
                assert nbNext == 0
            else:
                assert nbPrev == 1
                assert nbNext == 1

            i += 1

        # Make one picture not available
        picHidden = data["features"][0]["id"]

        with psycopg.connect(dburl, autocommit=True) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picHidden])

        response = client.get("/api/collections/" + str(seqId) + "/items")
        data = response.json

        assert response.status_code == 200

        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 4
        picIds = [f["id"] for f in data["features"]]
        assert picHidden not in picIds
        assert data["features"][0]["providers"] == [
            {"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)},
        ]

        assert data["features"][0]["properties"]["original_file:name"] == "2.jpg"
        assert data["features"][0]["properties"]["original_file:size"] == 3251027
        assert data["features"][0]["properties"]["geovisio:rank_in_collection"] == 2  # 2 because the first one is hidden
        assert data["features"][0]["properties"]["panoramax:horizontal_pixel_density"] == 16
        assert data["features"][0]["properties"]["datetime"] == "2021-07-29T09:16:56+00:00"
        assert data["features"][0]["properties"]["datetimetz"] == "2021-07-29T11:16:56+02:00"
        assert data["features"][0]["properties"]["pers:pitch"] == 0
        assert data["features"][0]["properties"]["pers:roll"] == 0
        assert data["features"][0]["properties"]["pers:interior_orientation"]["sensor_array_dimensions"] == [5760, 2880]
        assert data["features"][0]["properties"]["quality:horizontal_accuracy"] == 4


@conftest.SEQ_IMGS
def test_items_pagination_classic(datafiles, initSequenceApp, dburl):
    """Linear test case : get page one by one, consecutively"""

    with initSequenceApp(datafiles, preprocess=False) as client:
        seq = conftest.getPictureIds(dburl)[0]
        picIds = [p.id for p in seq.pictures]

        # First page
        response = client.get(f"/api/collections/{seq.id}/items?limit=2")
        data = response.json

        assert response.status_code == 200
        assert data["type"] == "FeatureCollection"

        clc = ItemCollection.from_dict(data)
        assert len(clc) == 2

        assert clc[0].id == picIds[0]
        assert clc[1].id == picIds[1]

        links = clc.extra_fields["links"]
        assert len(links) == 5

        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "last": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=3",
            "next": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=2",
        }

        # Second page
        response = client.get(f"/api/collections/{seq.id}/items?limit=2&startAfterRank=2")
        data = response.json

        assert response.status_code == 200
        clc = ItemCollection.from_dict(data)
        assert len(clc) == 2
        links = clc.extra_fields["links"]
        assert len(links) == 7

        assert clc[0].id == picIds[2]
        assert clc[1].id == picIds[3]

        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=2",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "last": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "next": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
        }
        # Third page
        response = client.get(f"/api/collections/{seq.id}/items?limit=2&startAfterRank=4")
        data = response.json

        assert response.status_code == 200
        clc = ItemCollection.from_dict(data)
        assert len(clc) == 1
        links = clc.extra_fields["links"]
        assert len(links) == 5

        assert clc[0].id == picIds[4]

        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=2",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
        }


@conftest.SEQ_IMGS
def test_items_pagination_nolimit(datafiles, initSequenceApp, dburl):
    """Calling next without limit"""

    with initSequenceApp(datafiles, preprocess=False) as client:
        seq = conftest.getPictureIds(dburl)[0]

        response = client.get(f"/api/collections/{seq.id}/items?startAfterRank=2")
        assert response.status_code == 200
        clc = ItemCollection.from_dict(response.json)
        assert len(clc) == 3
        links = clc.extra_fields["links"]
        assert len(links) == 5, [l["rel"] for l in links]

        assert clc[0].id == seq.pictures[2].id
        assert clc[1].id == seq.pictures[3].id
        assert clc[2].id == seq.pictures[4].id

        # we should have all the pagination links
        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?startAfterRank=2",
        }


@conftest.SEQ_IMGS
def test_items_pagination_outalimit(datafiles, initSequenceApp, dburl):
    """Requests using invalid or out of limit values"""
    with initSequenceApp(datafiles, preprocess=False) as client:
        seq = conftest.getPictureIds(dburl)[0]

        # Invalid limit
        for v in ["100000000000000000000", "prout", "-1"]:
            response = client.get("/api/collections/" + seq.id + "/items?limit=" + v)
            assert response.status_code == 400

        # Out of bounds next rank
        response = client.get("/api/collections/" + seq.id + "/items?startAfterRank=9000")
        assert response.status_code == 404
        assert response.json == {"message": "No more items in this collection (last available rank is 5)", "status_code": 404}

        # Remove everything
        with psycopg.connect(dburl, autocommit=True) as conn:
            conn.execute("DELETE FROM sequences_pictures")

        response = client.get("/api/collections/" + seq.id + "/items?limit=2")
        assert response.status_code == 200 and response.json["features"] == []


@conftest.SEQ_IMGS
def test_items_empty_collection(app, client, datafiles, dburl, bobAccountToken):
    """Requests the items of an empty collection"""
    seq_location = conftest.createSequence(client, "a_sequence", jwtToken=bobAccountToken())
    seq_id = seq_location.split("/")[-1]

    # the collection is not ready (there is no pictures), so it is hidden by default
    response = client.get(f"/api/collections/{seq_id}/items")
    assert response.status_code == 404
    assert response.json == {"message": "Collection doesn't exist", "status_code": 404}

    # but bob see an empty collection
    response = client.get(f"/api/collections/{seq_id}/items", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 200 and response.json["features"] == []


@conftest.SEQ_IMGS
def test_items_withPicture_no_limit(datafiles, initSequenceApp, dburl):
    """Asking for a page with a specific picture in it"""

    with initSequenceApp(datafiles, preprocess=False) as client:
        seq = conftest.getPictureIds(dburl)[0]
        pic_ids = [p.id for p in seq.pictures]

        response = client.get(f"/api/collections/{seq.id}/items?withPicture={seq.pictures[1].id}")
        assert response.status_code == 200
        clc = ItemCollection.from_dict(response.json)
        assert len(clc) == 4
        links = {l["rel"]: l["href"] for l in clc.extra_fields["links"]}
        # we should have all the pagination links but the `last` since we already are at the last page
        assert links == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items",
        }

        assert [c.id for c in clc] == pic_ids[1:]


@conftest.SEQ_IMGS
def test_items_withPicture_with_limit(datafiles, initSequenceApp, dburl):
    """
    Asking for a page with a specific picture in it with a limit, we should get the nth page with the picture
    There is 5 pics, if we ask for the fourth pic, with a limit=2, we should get a page with the third and the fourth pic
    """
    with initSequenceApp(datafiles, preprocess=False) as client:
        seq = conftest.getPictureIds(dburl)[0]
        pic_ids = [p.id for p in seq.pictures]

        response = client.get(f"/api/collections/{seq.id}/items?withPicture={seq.pictures[3].id}&limit=2")
        assert response.status_code == 200
        clc = ItemCollection.from_dict(response.json)
        assert len(clc) == 2
        links = {l["rel"]: l["href"] for l in clc.extra_fields["links"]}
        # we should have all the pagination links
        assert links == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "last": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
            "next": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",  # the prev link should be the 1st and 2nd pic, so the first page
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
        }

        assert [c.id for c in clc] == pic_ids[2:4]


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
def test_items_withPicture_invalid(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqs = conftest.getPictureIds(dburl)

        response = client.get(f"/api/collections/{seqs[0].id}/items?withPicture=plop")
        assert response.status_code == 400
        assert response.json == {"message": "withPicture should be a valid UUID", "status_code": 400}

        response = client.get(f"/api/collections/{seqs[0].id}/items?withPicture=00000000-0000-0000-0000-000000000000")
        assert response.status_code == 400
        assert response.json == {"message": "Picture with id 00000000-0000-0000-0000-000000000000 does not exist", "status_code": 400}

        # asking for a picture in another collection should also trigger an error
        response = client.get(f"/api/collections/{seqs[0].id}/items?withPicture={seqs[1].pictures[0].id}")
        assert response.status_code == 400
        assert response.json == {"message": f"Picture with id {seqs[1].pictures[0].id} does not exist", "status_code": 400}


@conftest.SEQ_IMGS
def test_items_pagination_nonconsecutive(datafiles, initSequenceApp, dburl):
    """Pagination over non-consecutive pictures ranks"""

    with initSequenceApp(datafiles, preprocess=False) as client:
        with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
            seq = conftest.getPictureIds(dburl)[0]

            cursor.execute("DELETE FROM sequences_pictures WHERE rank IN (1, 3)")
            conn.commit()

        # Calling on sequence start
        response = client.get(f"/api/collections/{seq.id}/items?limit=2")

        assert response.status_code == 200
        clc = ItemCollection.from_dict(response.json)
        assert len(clc) == 2
        clc.extra_fields["links"]

        assert clc[0].id == seq.pictures[1].id
        assert clc[1].id == seq.pictures[3].id

        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "last": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
            "next": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=4",
        }
        # Calling on the middle
        response = client.get(f"/api/collections/{seq.id}/items?limit=2&startAfterRank=2")

        assert response.status_code == 200
        clc = ItemCollection.from_dict(response.json)
        assert len(clc) == 2
        clc.extra_fields["links"]

        assert clc[0].id == seq.pictures[3].id
        assert clc[1].id == seq.pictures[4].id

        # no `last` link since it's the last page
        assert {l["rel"]: l["href"] for l in clc.extra_fields["links"]} == {
            "root": "http://localhost:5000/api/",
            "parent": f"http://localhost:5000/api/collections/{seq.id}",
            "self": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=2",
            "first": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2",
            "prev": f"http://localhost:5000/api/collections/{seq.id}/items?limit=2&startAfterRank=1",
        }


@conftest.SEQ_IMGS
def test_item(datafiles, initSequenceApp, dburl, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = getFirstPictureIds(dburl)

        response = client.get(f"/api/collections/{seqId}/items/{str(picId)}")
        assert response.status_code == 200
        data = response.json

        assert data["type"] == "Feature"
        assert data["geometry"]["type"] == "Point"
        assert len(str(data["id"])) > 0
        assert data["properties"]["datetime"] == "2021-07-29T09:16:54+00:00"
        assert data["properties"]["datetimetz"] == "2021-07-29T11:16:54+02:00"
        assert data["properties"]["view:azimuth"] >= 0
        assert data["properties"]["view:azimuth"] <= 360
        assert re.match(
            r"^https?://.*/api/pictures/" + str(picId) + r"/tiled/\{TileCol\}_\{TileRow\}.jpg$",
            data["asset_templates"]["tiles"]["href"],
        )
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/hd.jpg$", data["assets"]["hd"]["href"])
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/sd.jpg$", data["assets"]["sd"]["href"])
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/thumb.jpg$", data["assets"]["thumb"]["href"])
        assert data["properties"]["tiles:tile_matrix_sets"]["geovisio"]["tileMatrix"][0]["tileWidth"] == 720
        assert data["properties"]["tiles:tile_matrix_sets"]["geovisio"]["tileMatrix"][0]["tileHeight"] == 720
        assert data["properties"]["tiles:tile_matrix_sets"]["geovisio"]["tileMatrix"][0]["matrixHeight"] == 4
        assert data["properties"]["tiles:tile_matrix_sets"]["geovisio"]["tileMatrix"][0]["matrixWidth"] == 8
        assert data["properties"]["pers:interior_orientation"]["camera_manufacturer"] == "GoPro"
        assert data["properties"]["pers:interior_orientation"]["camera_model"] == "Max"
        assert data["properties"]["pers:interior_orientation"]["field_of_view"] == 360
        assert data["properties"]["pers:interior_orientation"]["sensor_array_dimensions"] == [5760, 2880]
        assert data["properties"]["original_file:name"] == "1.jpg"
        assert data["properties"]["original_file:size"] == 3296115
        assert data["properties"]["panoramax:horizontal_pixel_density"] == 16
        assert data["properties"]["quality:horizontal_accuracy"] == 4
        assert data["properties"]["created"].startswith(date.today().isoformat())
        assert data["properties"]["updated"].startswith(date.today().isoformat())
        assert data["properties"]["geovisio:status"] == "ready"
        assert data["properties"]["geovisio:rank_in_collection"] == 1
        assert data["providers"] == [
            {"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)},
        ]
        assert data["properties"]["geovisio:producer"] == "Default account"
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/hd.jpg$", data["properties"]["geovisio:image"])
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/thumb.jpg$", data["properties"]["geovisio:thumbnail"])
        assert len(data["properties"]["exif"]) > 0
        assert "Exif.Photo.MakerNote" not in data["properties"]["exif"]

        item = Item.from_dict(data)
        assert len(item.links) == 5
        assert len([l for l in item.links if l.rel == "next"]) == 1

        shortcut_response = client.get(f"/api/pictures/{str(picId)}")
        assert shortcut_response.status_code == 200
        assert shortcut_response.json == data

        # Make picture not available
        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])
                conn.commit()

                response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
                assert response.status_code == 404


@conftest.SEQ_IMGS_FLAT
def test_item_flat(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = getFirstPictureIds(dburl)

        response = client.get(f"/api/collections/{seqId}/items/{picId}")
        data = response.json

        assert response.status_code == 200

        assert data["type"] == "Feature"
        assert data["geometry"]["type"] == "Point"
        assert len(str(data["id"])) > 0
        assert data["properties"]["datetime"] == "2015-04-25T13:37:48+00:00"
        assert data["properties"]["datetimetz"] == "2015-04-25T15:37:48+02:00"
        assert data["properties"]["view:azimuth"] >= 0
        assert data["properties"]["view:azimuth"] <= 360
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/hd.jpg$", data["assets"]["hd"]["href"])
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/sd.jpg$", data["assets"]["sd"]["href"])
        assert re.match(r"^https?://.*/api/pictures/" + str(picId) + "/thumb.jpg$", data["assets"]["thumb"]["href"])
        assert "assert_templates" not in data
        assert "tiles:tile_matrix_sets" not in data["properties"]
        assert data["properties"]["pers:interior_orientation"]["camera_manufacturer"] == "OLYMPUS IMAGING CORP."
        assert data["properties"]["pers:interior_orientation"]["camera_model"] == "SP-720UZ"
        assert data["properties"]["pers:interior_orientation"]["field_of_view"] == 67
        assert data["properties"]["pers:interior_orientation"]["sensor_array_dimensions"] == [4288, 3216]
        assert "pers:pitch" not in data["properties"]
        assert "pers:roll" not in data["properties"]
        assert data["properties"]["panoramax:horizontal_pixel_density"] == 64
        assert "quality:horizontal_accuracy" not in data["properties"]
        assert data["properties"]["created"].startswith(date.today().isoformat())
        assert len(data["properties"]["exif"]) > 0
        assert "Exif.Photo.MakerNote" not in data["properties"]["exif"]

        item = Item.from_dict(data)
        assert len(item.links) == 5
        assert len([l for l in item.links if l.rel == "next"]) == 1


@conftest.SEQ_IMG_FLAT
def test_item_flat_fov(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
        data = response.json

        assert response.status_code == 200

        assert len(str(data["id"])) > 0
        assert data["properties"]["pers:interior_orientation"]["camera_manufacturer"] == "Canon"
        assert data["properties"]["pers:interior_orientation"]["camera_model"] == "EOS 6D0"
        assert data["properties"]["pers:interior_orientation"]["sensor_array_dimensions"] == [4104, 2736]
        assert data["properties"]["panoramax:horizontal_pixel_density"] == 76
        assert data["properties"]["pers:interior_orientation"]["field_of_view"] == 54


@conftest.SEQ_IMG_ARTIST
def test_item_artist(datafiles, initSequenceApp, dburl, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
        data = response.json
        assert response.status_code == 200

        assert data["providers"] == [
            {"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)},
            {"name": "Adrien Pavie", "roles": ["producer"]},
        ]
        assert data["properties"]["quality:horizontal_accuracy"] == 3.4


@conftest.SEQ_IMG_CROP
def test_item_crop(datafiles, initSequenceApp, dburl, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
        data = response.json

        assert response.status_code == 200

        assert data["properties"]["pers:interior_orientation"] == {
            "visible_area": [0, 2538, 0, 2792],
            "field_of_view": 360,
            "sensor_array_dimensions": [15872, 7936],
            "camera_manufacturer": "Google",
            "camera_model": "Pixel 6a",
        }


@conftest.SEQ_IMGS
def test_item_related(app, datafiles, client, dburl, bobAccountToken):
    # Simulate two nearby sequences
    seq1path = datafiles / "seq1"
    seq1path.mkdir()
    seq2path = datafiles / "seq2"
    seq2path.mkdir()
    os.rename(datafiles / "1.jpg", seq1path / "1.jpg")
    os.rename(datafiles / "2.jpg", seq1path / "2.jpg")
    os.rename(datafiles / "3.jpg", seq2path / "3.jpg")
    os.rename(datafiles / "4.jpg", seq2path / "4.jpg")
    os.rename(datafiles / "5.jpg", seq2path / "5.jpg")

    # Upload them
    conftest.uploadSequence(client, seq1path, wait=True, jwtToken=bobAccountToken())
    conftest.uploadSequence(client, seq2path, wait=True, jwtToken=bobAccountToken())

    # Get sequences + pictures IDs
    seqs = conftest.getPictureIds(dburl)
    firstSeq = seqs[0] if len(seqs[0].pictures) == 2 else seqs[1]
    secondSeq = seqs[1] if len(seqs[0].pictures) == 2 else seqs[0]

    # Check pic 2 = prev link + related to 3
    response = client.get("/api/collections/" + str(firstSeq.id) + "/items/" + str(firstSeq.pictures[1].id))
    links = response.json["links"]
    assert response.status_code == 200
    # print(f"Sequence 1 {firstSeq.id} : {', '.join([p.id for p in firstSeq.pictures])}")
    # print(f"Sequence 2 {secondSeq.id} : {', '.join([p.id for p in secondSeq.pictures])}")
    assert sorted([l["rel"] for l in links]) == ["collection", "license", "parent", "prev", "related", "root", "self"]
    assert next(l for l in links if l["rel"] == "prev") == {
        "rel": "prev",
        "id": firstSeq.pictures[0].id,
        "geometry": {"coordinates": [1.919185442, 49.00688962], "type": "Point"},
        "href": f"http://localhost:5000/api/collections/{str(firstSeq.id)}/items/{str(firstSeq.pictures[0].id)}",
        "type": "application/geo+json",
    }
    assert next(l for l in links if l["rel"] == "related") == {
        "rel": "related",
        "id": secondSeq.pictures[0].id,
        "geometry": {"coordinates": [1.919196361, 49.00692626], "type": "Point"},
        "href": f"http://localhost:5000/api/collections/{str(secondSeq.id)}/items/{str(secondSeq.pictures[0].id)}",
        "type": "application/geo+json",
        "datetime": "2021-07-29T09:16:58Z",
    }

    # Check pic 3 = next link + related to 2
    response = client.get("/api/collections/" + str(secondSeq.id) + "/items/" + str(secondSeq.pictures[0].id))
    links = response.json["links"]
    assert response.status_code == 200
    assert sorted([l["rel"] for l in links]) == ["collection", "license", "next", "parent", "related", "root", "self"]
    assert next(l for l in links if l["rel"] == "next") == {
        "rel": "next",
        "id": secondSeq.pictures[1].id,
        "geometry": {"coordinates": [1.919199781, 49.00695485], "type": "Point"},
        "href": f"http://localhost:5000/api/collections/{str(secondSeq.id)}/items/{str(secondSeq.pictures[1].id)}",
        "type": "application/geo+json",
    }
    assert next(l for l in links if l["rel"] == "related") == {
        "rel": "related",
        "id": firstSeq.pictures[1].id,
        "geometry": {"coordinates": [1.919189623, 49.006898646], "type": "Point"},
        "href": f"http://localhost:5000/api/collections/{str(firstSeq.id)}/items/{str(firstSeq.pictures[1].id)}",
        "type": "application/geo+json",
        "datetime": "2021-07-29T09:16:56Z",
    }

    # and if we delete the first sequence, we shouldn't have links between the 2 items anymore
    response = client.delete(f"/api/collections/{firstSeq.id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 204

    # note: the results should be hidden directly (without needing to wait for the pictures to be really deleted)
    response = client.get("/api/collections/" + str(secondSeq.id) + "/items/" + str(secondSeq.pictures[0].id))
    links = response.json["links"]
    assert response.status_code == 200
    # no more related link
    assert sorted([l["rel"] for l in links]) == ["collection", "license", "next", "parent", "root", "self"]


@conftest.SEQ_IMG_FLAT
def test_item_missing_all_metadata(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            seqId, picId = conftest.getFirstPictureIds(dburl)
            # Remove EXIF metadata from DB
            cursor.execute(
                "UPDATE pictures SET metadata = %s WHERE id = %s",
                [
                    '{"ts": 1430744932.0, "lat": 48.85779642035038, "lon": 2.3392783047650747, "type": "flat", "heading": 302}',
                    picId,
                ],
            )
            conn.commit()

            response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
            data = response.json

            assert response.status_code == 200

            assert len(str(data["id"])) > 0
            assert len(data["properties"]["pers:interior_orientation"]) == 0


@conftest.SEQ_IMG_FLAT
@pytest.mark.parametrize(("status", "httpCode"), (("ready", 200), ("hidden", 404), ("broken", 500)))
def test_item_status_httpcode(datafiles, initSequenceApp, dburl, status, httpCode):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                # Remove EXIF metadata from DB
                cursor.execute("UPDATE pictures SET status = %s WHERE id = %s", [status, picId])
                conn.commit()

                response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
                assert response.status_code == httpCode


@conftest.SEQ_IMG_FLAT
def test_item_missing_partial_metadata(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                # Remove EXIF metadata from DB
                cursor.execute(
                    "UPDATE pictures SET metadata = %s WHERE id = %s",
                    [
                        '{"ts": 1430744932.0, "lat": 48.85779642035038, "lon": 2.3392783047650747, "make": "Canon", "type": "flat", "width": 4104, "height": 2736, "heading": 302}',
                        picId,
                    ],
                )
                conn.commit()

                response = client.get("/api/collections/" + str(seqId) + "/items/" + str(picId))
                data = response.json

                assert response.status_code == 200

                assert len(str(data["id"])) > 0
                assert data["properties"]["pers:interior_orientation"] == {
                    "camera_manufacturer": "Canon",
                    "sensor_array_dimensions": [4104, 2736],
                }


def test_post_collection_nobody(client, dburl, defaultAccountID):
    response = client.post("/api/collections")

    assert response.status_code == 200
    assert response.headers.get("Location").startswith("http://localhost:5000/api/collections/")
    seqId = UUID(response.headers.get("Location").split("/").pop())
    assert seqId != ""

    # Check if JSON is a valid STAC collection
    assert response.json["type"] == "Collection"
    assert response.json["id"] == str(seqId)
    # the collection is associated to the default account since no auth was done
    assert response.json["providers"] == [{"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)}]

    # Check if collection exists in DB
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            seqStatus = cursor.execute("SELECT status FROM sequences WHERE id = %s", [seqId]).fetchone()[0]
            assert seqStatus == "waiting-for-process"


@conftest.SEQ_IMGS
def test_search_hidden_pic(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        assert len(sequence.pictures) == 5

        # hide sequence
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        # searching the sequence should result in an empty set
        response = client.get(f'/api/search?collections=["{sequence.id}"]')
        assert response.status_code == 200, response
        assert len(response.json["features"]) == 0

        # searching the picture should result in an empty set
        for p in sequence.pictures:
            response = client.get(f'/api/search?ids=["{p.id}"]')
            assert response.status_code == 200
            assert len(response.json["features"]) == 0


@conftest.SEQ_IMGS
def test_search_hidden_pic_as_owner(datafiles, initSequenceApp, dburl, bobAccountToken):
    """
    Searching for hidden pic change if it's the owner that searches
    """
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        assert len(sequence.pictures) == 5

        # hide sequence
        response = client.patch(
            f"/api/collections/{sequence.id}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        # searching the sequence as Bob should return all pictures
        response = client.get(f'/api/search?collections=["{sequence.id}"]', headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200
        assert len(response.json["features"]) == 5

        # searching the picture as Bob should also result in an empty set, event if it's the owner
        for p in sequence.pictures:
            response = client.get(f'/api/search?ids=["{p.id}"]', headers={"Authorization": f"Bearer {bobAccountToken()}"})
            assert response.status_code == 200
            assert len(response.json["features"]) == 1


@conftest.SEQ_IMGS
def test_picture_next_hidden(datafiles, initSequenceApp, dburl, bobAccountToken):
    """
    if pic n°3 is hidden:
    * for anonymous call, the next link of pic n°2 should be pic n°4 and previous link of pic n°4 should be pic n°2
    * for the owner, the next link of pic n°2 should be pic n°3 and previous link of pic n°4 should be pic n°3
    """
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        assert len(sequence.pictures) == 5

        response = client.patch(
            f"/api/collections/{str(sequence.id)}/items/{sequence.pictures[2].id}",
            data={"visible": "false"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        r = client.get(f"/api/collections/{sequence.id}/items/{sequence.pictures[2].id}")
        assert r.status_code == 404

        def _get_prev_link(r):
            return next(l for l in r.json["links"] if l["rel"] == "prev")

        def _get_next_link(r):
            return next(l for l in r.json["links"] if l["rel"] == "next")

        pic2 = client.get(f"/api/collections/{sequence.id}/items/{sequence.pictures[1].id}")
        assert pic2.status_code == 200
        next_link = _get_next_link(pic2)
        assert next_link["id"] == str(sequence.pictures[3].id)
        pic4 = client.get(f"/api/collections/{sequence.id}/items/{sequence.pictures[3].id}")
        assert pic4.status_code == 200
        prev_link = _get_prev_link(pic4)
        assert prev_link["id"] == str(sequence.pictures[1].id)

        # but calling this as the owner should return the right links
        pic2 = client.get(
            f"/api/collections/{sequence.id}/items/{sequence.pictures[1].id}", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert pic2.status_code == 200
        next_link = _get_next_link(pic2)
        assert next_link["id"] == str(sequence.pictures[2].id)
        pic4 = client.get(
            f"/api/collections/{sequence.id}/items/{sequence.pictures[3].id}", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert pic4.status_code == 200
        prev_link = _get_prev_link(pic4)
        assert prev_link["id"] == str(sequence.pictures[2].id)


@conftest.SEQ_IMGS_FLAT
def test_search_place_flat(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # Should return pictures looking at POI
        response = client.get("/api/search?place_position=-1.9499096,48.1397572&limit=2")
        assert response.status_code == 200, response
        pics = response.json["features"]
        assert len(pics) == 1
        assert pics[0]["id"] == sequence.pictures[0].id

        # Should not return picture (near first one, but out of sight)
        response = client.get("/api/search?place_position=-1.9499029,48.1398476&limit=2")
        assert response.status_code == 200, response
        pics = response.json["features"]
        assert len(pics) == 0

        # Single picture visible, with extended fov tolerance
        response = client.get("/api/search?place_position=-1.9499029,48.1398476&place_fov_tolerance=180&limit=2")
        assert response.status_code == 200, response
        pics = response.json["features"]
        assert len(pics) == 1
        assert pics[0]["id"] == sequence.pictures[0].id

        # Works with POST as well
        response = client.post("/api/search", json={"limit": 2, "place_position": "-1.9499029,48.1398476", "place_fov_tolerance": 180})
        assert response.status_code == 200, response
        pics = response.json["features"]
        assert len(pics) == 1
        assert pics[0]["id"] == sequence.pictures[0].id


@conftest.SEQ_IMGS
def test_patch_collection_contenttype(datafiles, initSequenceApp, dburl, bobAccountToken):
    """Setting an already visible sequence to visible is valid, and change nothing"""
    with initSequenceApp(datafiles, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        # hide sequence
        p = client.patch(
            f"/api/collections/{sequence.id}",
            data={"visible": "false"},
            headers={"Content-Type": "multipart/form-data; whatever=blabla", "Authorization": f"Bearer {bobAccountToken()}"},
        )

        assert p.status_code == 200

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                newStatus = cursor.execute("SELECT status FROM sequences WHERE id = %s", [sequence.id]).fetchone()[0]
                assert newStatus == "hidden"


@conftest.SEQ_IMG_FLAT
def test_post_item_nobody(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)
        response = client.post(f"/api/collections/{seqId}/items")
        assert response.status_code == 415


@pytest.mark.parametrize(
    ("filename", "position", "httpCode"),
    (
        ("1.jpg", 2, 202),
        ("1.jpg", 1, 409),
        (None, 2, 400),
        ("1.jpg", -1, 400),
        ("1.jpg", "bla", 400),
        ("1.txt", 2, 400),
    ),
)
@conftest.SEQ_IMG_FLAT
def test_post_item_body_formdata(datafiles, initSequenceApp, dburl, filename, position, httpCode, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            seqId = cursor.execute("SELECT id FROM sequences LIMIT 1").fetchone()[0]

            # Make sequence marked as preparing
            cursor.execute("UPDATE sequences SET status='preparing' WHERE id = %s", [seqId])
            conn.commit()

            if filename is not None and filename != "1.jpg":
                os.mknod(datafiles / "seq1" / filename)

            origMetadata = None
            if filename == "1.jpg":
                with open(datafiles / "seq1" / filename, "rb") as img:
                    origMetadata = reader.readPictureMetadata(img.read())
                assert len(origMetadata.exif) > 0

            response = client.post(
                f"/api/collections/{seqId}/items",
                headers={"Content-Type": "multipart/form-data"},
                data={"position": position, "picture": (datafiles / "seq1" / filename).open("rb") if filename is not None else None},
            )

            assert response.status_code == httpCode

            # Further testing if picture was accepted
            if httpCode == 202:
                assert response.headers.get("Location").startswith(f"http://localhost:5000/api/collections/{seqId}/items/")
                picId = UUID(response.headers.get("Location").split("/").pop())
                assert str(picId) != ""

                # Check the returned JSON
                assert response.json["type"] == "Feature"
                assert response.json["id"] == str(picId)
                assert response.json["collection"] == str(seqId)
                # since the upload was not authenticated, the pictures are associated to the default account
                assert response.json["providers"] == [{"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)}]
                # Check if EXIF naming scheme is Exiv2
                assert response.json["properties"]["exif"]["Exif.GPSInfo.GPSImgDirection"] == "302/1"

                # Check that picture has been correctly processed
                retries = 0
                while retries < 10 and retries != -1:
                    dbStatus = cursor.execute("SELECT status FROM pictures WHERE id = %s", [picId]).fetchone()[0]

                    if dbStatus == "ready":
                        retries = -1
                        laterResponse = client.get(f"/api/collections/{seqId}/items/{picId}")
                        assert laterResponse.status_code == 200

                        # Check file is available on filesystem
                        assert os.path.isfile(datafiles / "permanent" / geovisio.utils.pictures.getHDPicturePath(picId).strip("/"))
                        assert not os.path.isdir(datafiles / "permanent" / geovisio.utils.pictures.getPictureFolderPath(picId).strip("/"))

                        # Check sequence is marked as ready
                        seqStatus = cursor.execute("SELECT status FROM sequences WHERE id = %s", [seqId]).fetchone()
                        assert seqStatus and seqStatus[0] == "ready"

                        # Check picture has its metadata still stored
                        with open(datafiles / "permanent" / geovisio.utils.pictures.getHDPicturePath(picId).strip("/"), "rb") as img:
                            storedMetadata = reader.readPictureMetadata(img.read())
                        assert str(storedMetadata) == str(origMetadata)

                    else:
                        retries += 1
                        time.sleep(2)

                if retries == 10:
                    raise Exception("Picture has never been processed")

                # md5sum should have been computed
                md5 = cursor.execute("SELECT original_content_md5 FROM pictures where id = %s", [picId]).fetchone()
                assert md5 and md5[0] == UUID(
                    "5726ea34eb5750af7a78a73ad966cf86"
                )  # value fetched from calling `md5sum` on the `c1.jpg` file


@conftest.SEQ_IMGS_FLAT
def test_upload_pictures_with_external_metadata(datafiles, client, dburl):
    # Create sequence
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]

    external_ts = "2023-07-03T10:12:01.001Z"
    # Post an image, overloading it's datetime
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={
            "position": 1,
            "picture": (datafiles / "b1.jpg").open("rb"),
            "override_capture_time": external_ts,
            "override_Exif.Image.Artist": "R. Doisneau",
            "override_Xmp.xmp.Rating": "5",
        },
    )

    assert resPostImg1.status_code == 202

    # Check upload status
    conftest.waitForSequence(client, resPostSeq.headers["Location"])
    sequence = conftest.getPictureIds(dburl)[0]

    r = client.get(f"/api/collections/{seqId}/items")
    assert r.status_code == 200
    assert len(r.json["features"]) == 1
    # the picture should have the given datetime
    expected_date = "2023-07-03T10:12:01.001000+00:00"
    assert r.json["features"][0]["properties"]["datetime"] == expected_date
    assert r.json["features"][0]["providers"][1]["name"] == "R. Doisneau"
    assert r.json["features"][0]["properties"]["exif"]["Exif.Image.Artist"] == "R. Doisneau"
    assert r.json["features"][0]["properties"]["exif"]["Xmp.xmp.Rating"] == "5"

    # we also check that the stored picture has the correct exif tags
    perm_pic = sequence.pictures[0].get_permanent_file(datafiles)
    with open(perm_pic, "rb") as img:
        tags = reader.readPictureMetadata(img.read())
    assert tags.ts == datetime.fromisoformat(expected_date)
    assert tags.exif["Exif.Image.Artist"] == "R. Doisneau"

    with psycopg.connect(dburl) as conn:
        # md5sum should be the same as when posting file without external metadata
        md5 = conn.execute("SELECT original_content_md5 FROM pictures where id = %s", [sequence.pictures[0].id]).fetchone()
        assert md5
        assert md5[0] == UUID("0426c1cf58ae274c300346e040f9f5c2")  # value fetched from calling `md5sum` on the `b1.jpg` file


@pytest.mark.parametrize(
    ("date", "error"),
    (
        (
            "a bad date",
            {
                "message": "Parameter `override_capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z').",
                "status_code": 400,
                "details": {"error": "Unknown string format: a bad date"},
            },
        ),
        (
            "",
            {
                "message": "Parameter `override_capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z').",
                "status_code": 400,
                "details": {"error": "String does not contain a date: "},
            },
        ),
    ),
)
@conftest.SEQ_IMGS_FLAT
def test_upload_pictures_with_bad_external_ts(datafiles, client, date, error):
    """Test sending bad external datetime while uploading picutre, it should results in detailed errors"""
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    r = client.post(
        f"/api/collections/{resPostSeq.json['id']}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "b1.jpg").open("rb"), "override_capture_time": date},
    )
    assert r.status_code == 400
    assert r.json == error


@conftest.SEQ_IMGS_FLAT
def test_upload_pictures_with_external_position(datafiles, client, dburl):
    # Create sequence
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]

    lat = 42.42
    lon = 4.42
    # Post an image, overloading it's position
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "b1.jpg").open("rb"), "override_longitude": lon, "override_latitude": lat},
    )

    assert resPostImg1.status_code == 202

    # Check upload status
    conftest.waitForSequence(client, resPostSeq.headers["Location"])
    sequence = conftest.getPictureIds(dburl)[0]

    r = client.get(f"/api/collections/{seqId}/items")
    assert r.status_code == 200
    assert len(r.json["features"]) == 1
    # the picture should have the given position
    assert r.json["features"][0]["geometry"] == {"type": "Point", "coordinates": [lon, lat]}

    # we also check that the stored picture has the correct exif tags
    perm_pic = sequence.pictures[0].get_permanent_file(datafiles)
    with open(perm_pic, "rb") as img:
        tags = reader.readPictureMetadata(img.read())
    assert math.isclose(tags.lat, lat)
    assert math.isclose(tags.lon, lon)


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"))
def test_upload_pictures_i18n_error(datafiles, client, dburl):
    # Create sequence
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]

    # Post an image, overloading it's position
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data", "Accept-Language": "fr_FR, fr, en"},
        data={"position": 1, "picture": (datafiles / "e1_without_exif.jpg").open("rb")},
    )

    assert resPostImg1.status_code == 400
    assert resPostImg1.json == {
        "details": {
            "error": "Des métadonnées obligatoires sont manquantes\u202f:\n\t- Coordonnées GPS absentes ou invalides dans les attributs EXIF de l'image\n\t- Aucune date valide dans les attributs EXIF de l'image"
        },
        "message": "Impossible de lire les métadonnées de la photo",
        "status_code": 400,
    }


@pytest.mark.parametrize(
    ("lon", "lat", "error"),
    (
        (
            "43.12",
            None,
            {
                "message": "Longitude cannot be overridden alone, override_latitude also needs to be set",
                "status_code": 400,
            },
        ),
        (
            None,
            "43.12",
            {
                "message": "Latitude cannot be overridden alone, override_longitude also needs to be set",
                "status_code": 400,
            },
        ),
        (
            "pouet",
            "43.12",
            {
                "message": "For parameter `override_longitude`, `pouet` is not a valid longitude",
                "details": {"error": "could not convert string to float: 'pouet'"},
                "status_code": 400,
            },
        ),
        (
            "192.2",
            "43.12",
            {
                "message": "For parameter `override_longitude`, `192.2` is not a valid longitude",
                "details": {"error": "longitude needs to be between -180 and 180"},
                "status_code": 400,
            },
        ),
    ),
)
@conftest.SEQ_IMGS_FLAT
def test_upload_pictures_with_bad_external_position(datafiles, client, lon, lat, error):
    """Test sending bad external datetime while uploading picutre, it should results in detailed errors"""
    data = {"position": 1, "picture": (datafiles / "b1.jpg").open("rb")}
    if lon is not None:
        data["override_longitude"] = lon
    if lat is not None:
        data["override_latitude"] = lat
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    r = client.post(
        f"/api/collections/{resPostSeq.json['id']}/items",
        headers={"Content-Type": "multipart/form-data"},
        data=data,
    )
    assert r.status_code == 400
    assert r.json == error


@pytest.mark.datafiles(os.path.join(conftest.FIXTURE_DIR, "e1_without_exif.jpg"))
def test_upload_pictures_without_exif_but_external_metadatas(datafiles, client, dburl):
    """Uploading pictures without metadatas shouldn't be a problem if the mandatory metadatas are provided by the API as external metadatas"""
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]

    lat = 42.42
    lon = 4.42
    external_ts = "2023-07-03T10:12:01.001Z"
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={
            "position": 1,
            "picture": (datafiles / "e1_without_exif.jpg").open("rb"),
            "override_longitude": lon,
            "override_latitude": lat,
            "override_capture_time": external_ts,
        },
    )

    assert resPostImg1.status_code == 202, resPostSeq.text

    # Check upload status
    conftest.waitForSequence(client, resPostSeq.headers["Location"])
    sequence = conftest.getPictureIds(dburl)[0]

    r = client.get(f"/api/collections/{seqId}/items")
    assert r.status_code == 200
    assert len(r.json["features"]) == 1
    # the picture should have the given position
    assert r.json["features"][0]["geometry"] == {"type": "Point", "coordinates": [lon, lat]}

    # we also check that the stored picture has the correct exif tags
    perm_pic = sequence.pictures[0].get_permanent_file(datafiles)
    with open(perm_pic, "rb") as img:
        tags = reader.readPictureMetadata(img.read())
    assert math.isclose(tags.lat, lat)
    assert math.isclose(tags.lon, lon)
    expected_date = "2023-07-03T10:12:01.001000+00:00"
    assert r.json["features"][0]["properties"]["datetime"] == expected_date


@pytest.mark.datafiles(os.path.join(conftest.FIXTURE_DIR, "e1_without_exif.jpg"))
def test_upload_pictures_without_complete_exif_but_external_metadatas(datafiles, client, dburl):
    """
    Uploading pictures should be an error if we don't find all mandatory metadata in the picture + it's external metadata

    There we upload a picture without exif metadata, and override only the timestamp, so we lack the coordinate
    """
    resPostSeq = client.post("/api/collections")
    assert resPostSeq.status_code == 200
    seqId = resPostSeq.json["id"]

    external_ts = "2023-07-03T10:12:01.001Z"
    resPostImg1 = client.post(
        f"/api/collections/{seqId}/items",
        headers={"Content-Type": "multipart/form-data"},
        data={
            "position": 1,
            "picture": (datafiles / "e1_without_exif.jpg").open("rb"),
            "override_capture_time": external_ts,  # only a timestamp
        },
    )

    assert resPostImg1.status_code == 400
    assert resPostImg1.json == {
        "details": {"error": "No GPS coordinates or broken coordinates in picture EXIF tags"},
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
    }


@conftest.SEQ_IMGS_FLAT
def test_upload_on_unknown_sequence(datafiles, client, dburl):
    # add image on unexisting sequence
    resPostImg = client.post(
        "/api/collections/00000000-0000-0000-0000-000000000000/items",
        headers={"Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "b1.jpg").open("rb")},
    )

    assert resPostImg.status_code == 404
    assert resPostImg.json["message"] == "Collection 00000000-0000-0000-0000-000000000000 wasn't found in database"


def mockBlurringAPIPostKO(requests_mock):
    """accessing the blurring api result in a connection timeout"""
    requests_mock.post(
        conftest.MOCK_BLUR_API + "/blur/",
        exc=requests.exceptions.ConnectTimeout,
    )


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_upload_picture_skip_blurring(requests_mock, datafiles, tmp_path, dburl):
    """
    Inserting a picture which is already blurred should not call the KO Blur API, thus leading to no error
    """
    mockBlurringAPIPostKO(requests_mock)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, isBlurred=True)

            conftest.waitForSequence(client, seq_location)

            with psycopg.connect(dburl) as conn:
                with conn.cursor() as cursor:
                    blurred = cursor.execute(
                        "SELECT (metadata->>'blurredByAuthor')::boolean FROM pictures WHERE metadata->>'originalFileName' = '1.jpg'"
                    ).fetchone()
                    assert blurred and blurred[0] is True


def mockBlurringAPIPostOkay(requests_mock, datafiles):
    """Mock a working blur API call"""
    requests_mock.post(
        conftest.MOCK_BLUR_API + "/blur/",
        body=open(datafiles / "1_blurred.jpg", "rb"),
    )


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_upload_picture_blurring_okay(requests_mock, datafiles, tmp_path, dburl, defaultAccountID):
    mockBlurringAPIPostOkay(requests_mock, datafiles)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        with app.test_client() as client, psycopg.connect(dburl) as conn:
            with conn.cursor():
                seq_location = conftest.createSequence(client, "a_sequence")

                with open(datafiles / "1_blurred.jpg", "rb") as img:
                    origMetadata = reader.readPictureMetadata(img.read())
                    assert len(origMetadata.exif) > 0

                response = client.post(
                    f"{seq_location}/items",
                    headers={"Content-Type": "multipart/form-data"},
                    data={"position": 1, "picture": (datafiles / "1.jpg").open("rb")},
                )

                assert response.status_code == 202 and response.json

                assert response.headers["Location"].startswith(f"{seq_location}/items/")
                picId = UUID(response.headers["Location"].split("/").pop())
                assert str(picId) != ""

                # Check the returned JSON
                assert response.json["type"] == "Feature"
                assert response.json["id"] == str(picId)
                # since the upload was not authenticated, the pictures are associated to the default account
                assert response.json["providers"] == [{"name": "Default account", "roles": ["producer"], "id": str(defaultAccountID)}]

                conftest.waitForSequence(client, seq_location)

                # Check that picture has been correctly processed
                laterResponse = client.get(f"{seq_location}/items/{picId}")
                assert laterResponse.status_code == 200

                # Check if picture sent to blur API is same as one from FS
                reqSize = int(requests_mock.request_history[0].headers["Content-Length"])
                picSize = os.path.getsize(datafiles / "1.jpg")
                assert reqSize <= picSize * 1.01

                # Check file is available on filesystem
                assert os.path.isfile(datafiles / "permanent" / geovisio.utils.pictures.getHDPicturePath(picId).strip("/"))
                assert not os.path.isdir(datafiles / "permanent" / geovisio.utils.pictures.getPictureFolderPath(picId).strip("/"))

                # Check picture has its metadata still stored
                with open(datafiles / "permanent" / geovisio.utils.pictures.getHDPicturePath(picId).strip("/"), "rb") as img:
                    storedMetadata = reader.readPictureMetadata(img.read())
                    assert storedMetadata == origMetadata
                    assert str(storedMetadata) == str(origMetadata)


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_pic_process_ko_1(requests_mock, datafiles, tmp_path, dburl):
    """
    Inserting a picture with the bluring api ko should result in the image having a broken status
    """
    mockBlurringAPIPostKO(requests_mock)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            s = client.get(f"{seq_location}/geovisio_status")
            assert s.status_code < 400
            conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1)

            def wanted_state(seq):
                pic_status = {p["rank"]: (p["status"], p.get("nb_errors")) for p in seq.json["items"]}
                return pic_status == {1: ("broken", 6)}

            conftest.waitForSequenceState(client, seq_location, wanted_state)

            s = client.get(f"{seq_location}/geovisio_status")

            assert s.json
            pic = s.json["items"][0]

            assert pic["status"] == "broken"
            assert pic["nb_errors"] == 6
            assert pic["processed_at"].startswith(date.today().isoformat())
            assert pic["process_error"] == "Blur API failure: ConnectTimeout"

            assert (
                s.json["status"] == "waiting-for-process"
            )  # since no pictures have been uploaded for the sequence, it's still in the 'waiting-for-processs' status


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_pic_process_ko_2(datafiles, dburl, tmp_path, monkeypatch):
    """
    Inserting 2 pictures ('1.jpg' and '2.jpg'), and '1.jpg' cannot have its derivates generated should result in
    * '1.jpg' being in a 'broken' state
    * '2.jpg' being 'ready'
    * the sequence being 'ready'
    """
    from geovisio.workers import runner_pictures

    def new_processPictureFiles(dbJob, _config):
        """Mock function that raises an exception for 1.jpg"""
        with psycopg.connect(dburl) as db:
            pic_name = db.execute("SELECT metadata->>'originalFileName' FROM pictures WHERE id = %s", [dbJob.pic.id]).fetchone()
            assert pic_name
            pic_name = pic_name[0]
            if pic_name == "1.jpg":
                raise Exception("oh no !")
            elif pic_name == "2.jpg":
                return  # all good
            raise Exception(f"picture {pic_name} not handled")

    monkeypatch.setattr(runner_pictures, "processPictureFiles", new_processPictureFiles)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1)
            conftest.uploadPicture(client, seq_location, open(datafiles / "2.jpg", "rb"), "2.jpg", 2)

            import time

            time.sleep(1)

            s = client.get(f"{seq_location}/geovisio_status")
            assert s and s.status_code == 200 and s.json
            pic_status = {p["rank"]: p["status"] for p in s.json["items"]}

            assert pic_status == {1: "broken", 2: "ready"}
            assert s.json["status"] == "ready"


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_3_pictures(datafiles, dburl, tmp_path, monkeypatch):
    """
    Inserting 3 pictures ('1.jpg', '2.jpg' and '3.jpg" )
    No problem in inserting all pictures, the sequence should be marked as 'ready'
    and it's metadata should be generated (shapes for example)
    """
    from geovisio.workers import runner_pictures

    def new_processPictureFiles(dbPic, _config):
        """Mock function that is always happy"""
        return

    monkeypatch.setattr(runner_pictures, "processPictureFiles", new_processPictureFiles)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1)
            conftest.uploadPicture(client, seq_location, open(datafiles / "2.jpg", "rb"), "2.jpg", 2)
            conftest.uploadPicture(client, seq_location, open(datafiles / "3.jpg", "rb"), "3.jpg", 3)

            def wanted_state(seq):
                pic_status = {p["rank"]: p["status"] for p in seq.json["items"]}
                return pic_status == {1: "ready", 2: "ready", 3: "ready"} and seq.json["status"] == "ready"

            conftest.waitForSequenceState(client, seq_location, wanted_state)
            time.sleep(0.1)
            seq = client.get(seq_location)
            assert seq.status_code == 200 and seq.json

            pics = client.get(f"{seq_location}/items")
            assert pics.status_code == 200 and pics.json
            assert len(pics.json["features"]) == 3
            assert pics.json["features"][0]["geometry"]["coordinates"] == [1.919185442, 49.00688962]
            assert pics.json["features"][1]["geometry"]["coordinates"] == [1.919189623, 49.006898646]
            assert pics.json["features"][2]["geometry"]["coordinates"] == [1.919196361, 49.00692626]

            # the sequence should have been processed, and it's sequence computed
            # Note: round a bit to avoid random failures
            assert [round(f, 3) for f in seq.json["extent"]["spatial"]["bbox"][0]] == [1.919, 49.007, 1.919, 49.007]


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_last_picture_ko(datafiles, dburl, tmp_path, monkeypatch):
    """
    Inserting 3 pictures ('1.jpg', '2.jpg' and '3.jpg" ), and '3.jpg' cannot have its derivates generated should result in
    * '1.jpg' and '2.jpg' being in a 'ready' state
    * '3.jpg' being 'broken'
    * the sequence being 'ready', and with it's metadata generated (shapes for example)
    """
    from geovisio.workers import runner_pictures

    def new_processPictureFiles(dbJob, _config):
        """Mock function that raises an exception for 1.jpg"""
        with psycopg.connect(dburl) as db:
            pic_name = db.execute("SELECT metadata->>'originalFileName' FROM pictures WHERE id = %s", [dbJob.pic.id]).fetchone()
            assert pic_name
            pic_name = pic_name[0]
            if pic_name in ("1.jpg", "2.jpg"):
                return  # all good
            elif pic_name == "3.jpg":
                raise Exception("oh no !")
            raise Exception(f"picture {pic_name} not handled")

    monkeypatch.setattr(runner_pictures, "processPictureFiles", new_processPictureFiles)
    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
            "PICTURE_PROCESS_THREADS_LIMIT": 0,  # to avoid randomness in this test, we process the pictures using async workers
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            seq_id = UUID(seq_location.split("/")[-1])
            pic1_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1))
            pic2_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "2.jpg", "rb"), "2.jpg", 2))
            pic3_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "3.jpg", "rb"), "3.jpg", 3))

            w = runner_pictures.PictureProcessor(app=app, stop=True)

            w.process_jobs()
            # We run another runner to process the pictures, even after the last one has return with an error
            w.process_jobs()

            with psycopg.connect(dburl, row_factory=dict_row) as conn:
                jobs = conn.execute("SELECT * FROM job_queue").fetchall()

                assert jobs == []

                job_history = conftest.get_job_history()
                pic_history = [j for j in job_history if "picture_id" in j]
                assert pic_history == [
                    {"picture_id": pic1_id, "job_task": "prepare"},
                    {"picture_id": pic2_id, "job_task": "prepare"},
                    {"picture_id": pic3_id, "job_task": "prepare", "error": "oh no !"},
                ]

                seq = client.get(seq_location)
                assert seq.status_code == 200 and seq.json

                pics = client.get(f"{seq_location}/items")
                assert pics.status_code == 200 and pics.json
                assert len(pics.json["features"]) == 2
                assert pics.json["features"][0]["geometry"]["coordinates"] == [1.919185442, 49.00688962]
                assert pics.json["features"][1]["geometry"]["coordinates"] == [1.919189623, 49.006898646]

                all_jobs = conn.execute(
                    "SELECT picture_id, sequence_id, upload_set_id, job_task, started_at, finished_at, error FROM job_history ORDER BY finished_at"
                ).fetchall()

                # the sequence should have been processed, and its shape computed
                # Note: the computed bbox should be the same as test_process_picture_3_pictures test even if the last picture has not been processed
                # because the sequence geom also consider the broken pictures

                # Note: since there are random failure in this test, we display the run job to debug it
                assert seq.json["extent"]["spatial"]["bbox"] == [
                    [1.9191854417991367, 49.00688961988304, 1.9191963606027425, 49.00692625960235]
                ], f"sequence geom is not correct, jobs -> {conftest.get_job_history(with_time=True)}"

                jobs = conn.execute(
                    "SELECT id, picture_id, job_task, started_at, finished_at, error FROM job_history WHERE picture_id IS NOT NULL ORDER BY started_at"
                ).fetchall()
                assert jobs and len(jobs) == 3

                for job in jobs:
                    assert job["job_task"] == "prepare"
                    assert job["started_at"].date() == date.today()
                    assert job["finished_at"].date() == date.today()
                    assert job["started_at"] < job["finished_at"]

                assert jobs[0]["picture_id"] == pic1_id
                assert jobs[0]["error"] is None
                assert jobs[1]["picture_id"] == pic2_id
                assert jobs[1]["error"] is None
                assert jobs[2]["picture_id"] == pic3_id
                assert jobs[2]["error"] == "oh no !"

            # there should also be a sequence finalization job, even if the last picture was ko (and there can be more than one, since it depends on async workers)
            with psycopg.connect(dburl, row_factory=dict_row) as conn:
                jobs = conn.execute(
                    "SELECT id, sequence_id, job_task, started_at, finished_at, error FROM job_history WHERE sequence_id IS NOT NULL AND finished_at IS NOT NULL ORDER BY started_at"
                ).fetchall()
                assert jobs and len(jobs) >= 1

                assert jobs[-1]["job_task"] == "finalize"
                assert jobs[-1]["started_at"].date() == date.today()
                assert jobs[-1]["finished_at"].date() == date.today()
                assert jobs[-1]["started_at"] < jobs[-1]["finished_at"]
                assert jobs[-1]["sequence_id"] == seq_id
                assert jobs[-1]["error"] is None


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_upload_picture_storage_ko(datafiles, dburl, tmp_path, monkeypatch):
    """
    Failing to save a picture in the storage should result in a 500 and no changes in the database
    """

    class StorageException(Exception):
        pass

    # files will be stored in permanent storage as there is no bluring
    def new_writefile(*args, **kwargs):
        """Mock function that fails to store file"""
        raise StorageException("oh no !")

    with create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": "",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        }
    ) as app:
        permanent_storage = app.config["FILESYSTEMS"].permanent

        monkeypatch.setattr(permanent_storage, "writebytes", new_writefile)
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")

            # with pytest.raises(StorageException):
            picture_response = client.post(
                f"{seq_location}/items",
                data={"position": 1, "picture": (open(datafiles / "1.jpg", "rb"), "1.jpg")},
                content_type="multipart/form-data",
            )
            assert picture_response.status_code == 500

            # we post again the picture, now it should work, even with the same position
            picture_response = client.post(
                f"{seq_location}/items",
                data={"position": 1, "picture": (open(datafiles / "1.jpg", "rb"), "1.jpg")},
                content_type="multipart/form-data",
            )
            assert picture_response.status_code == 500  # and not a 409, conflict

            # there should be nothing in the database
            with psycopg.connect(dburl) as conn:
                with conn.cursor() as cursor:
                    nb_pic = cursor.execute("SELECT count(*) from pictures").fetchone()
                    assert nb_pic is not None and nb_pic[0] == 0
                    nb_pic_in_seq = cursor.execute("SELECT count(*) from sequences_pictures").fetchone()
                    assert nb_pic_in_seq is not None and nb_pic_in_seq[0] == 0


@pytest.mark.datafiles(os.path.join(conftest.FIXTURE_DIR, "invalid_exif.jpg"))
def test_upload_picture_invalid_metadata(datafiles, client):
    """
    Inserting a picture with invalid metada should result in a 400 error with details about why the picture has been rejected
    """

    seq_location = conftest.createSequence(client, "a_sequence")

    picture_response = client.post(
        f"{seq_location}/items",
        data={"position": 1, "picture": (open(datafiles / "invalid_exif.jpg", "rb"), "invalid_exif.jpg")},
        content_type="multipart/form-data",
    )

    assert picture_response.status_code == 400
    assert picture_response.json == {
        "details": {"error": "No GPS coordinates or broken coordinates in picture EXIF tags"},
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
    }


@conftest.SEQ_IMGS
def test_patch_item_noauth(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)
        response = client.get(itemRoute)
        assert response.status_code == 200

        # Lacks authentication
        response = client.patch(itemRoute, data={"visible": "false"})
        assert response.status_code == 401


@conftest.SEQ_IMGS
def test_add_items_as_another_user(datafiles, initSequenceApp, dburl, defaultAccountToken):
    """
    Adding picture to a non owned collection should be forbidden
    Here the pictures are owned by Bob and the default account tries to add more
    """
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        response = client.post(
            f"/api/collections/{sequence.id}/items",
            data={"position": 101, "picture": (datafiles / "seq1" / "1.jpg").open("rb")},
            headers={"Content-Type": "multipart/form-data", "Authorization": f"Bearer {defaultAccountToken()}"},
        )
        assert response.status_code == 403
        assert response.json == {"message": "You're not authorized to add picture to this collection", "status_code": 403}


@conftest.SEQ_IMGS
def test_patch_item_authtoken(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)
        response = client.get(itemRoute)
        assert response.status_code == 200

        # Prepare auth headers
        headers = {"Authorization": "Bearer " + bobAccountToken()}

        # Make picture not visible
        response = client.patch(itemRoute, data={"visible": "false"}, headers=headers)
        assert response.status_code == 200
        data = response.json
        assert data["id"] == str(picId)
        assert data["properties"]["geovisio:status"] == "hidden"

        # Try to retrieve hidden picture as public
        response = client.get(itemRoute)
        assert response.status_code == 404

        # we should also be able to see the picture from the /items route as bob
        all_pics_as_bob = client.get(f"/api/collections/{str(seqId)}/items", headers=headers)
        assert all_pics_as_bob.status_code == 200
        assert len(all_pics_as_bob.json["features"]) == 5
        assert all_pics_as_bob.json["features"][0]["id"] == str(picId)
        assert all_pics_as_bob.json["features"][0]["properties"]["geovisio:status"] == "hidden"
        for f in all_pics_as_bob.json["features"][1:]:
            assert f["properties"]["geovisio:status"] == "ready"

        # but an unauthentified call should see only 1 pic in the collection
        all_pics_unauthentified = client.get(f"/api/collections/{str(seqId)}/items")
        assert all_pics_unauthentified.status_code == 200
        assert len(all_pics_unauthentified.json["features"]) == 4
        assert picId not in [f["id"] for f in all_pics_unauthentified.json["features"]]
        for f in all_pics_unauthentified.json["features"]:
            assert f["properties"]["geovisio:status"] == "ready"

        # we should also be able to see the picture from the /items route as bob
        all_pics_as_bob = client.get(f"/api/collections/{str(seqId)}/items", headers=headers)
        assert all_pics_as_bob.status_code == 200
        assert len(all_pics_as_bob.json["features"]) == 5
        assert all_pics_as_bob.json["features"][0]["id"] == str(picId)
        assert all_pics_as_bob.json["features"][0]["properties"]["geovisio:status"] == "hidden"
        for f in all_pics_as_bob.json["features"][1:]:
            assert f["properties"]["geovisio:status"] == "ready"

        # but an unauthentified call should see only 1 pic in the collection
        all_pics_unauthentified = client.get(f"/api/collections/{str(seqId)}/items")
        assert all_pics_unauthentified.status_code == 200
        assert len(all_pics_unauthentified.json["features"]) == 4
        assert picId not in [f["id"] for f in all_pics_unauthentified.json["features"]]
        for f in all_pics_unauthentified.json["features"]:
            assert f["properties"]["geovisio:status"] == "ready"

        # Re-enable picture
        response = client.patch(itemRoute, data={"visible": "true"}, headers=headers)
        assert response.status_code == 200
        data = response.json
        assert data["id"] == str(picId)
        assert data["properties"]["geovisio:status"] == "ready"


def test_patch_item_missing(client, app, bobAccountToken):
    response = client.patch(
        "/api/collections/00000000-0000-0000-0000-000000000000/items/00000000-0000-0000-0000-000000000000",
        data={"visible": "false"},
        headers={"Authorization": "Bearer " + bobAccountToken()},
    )
    assert response.status_code == 404


@conftest.SEQ_IMGS
def test_patch_item_invalidVisible(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)

        response = client.patch(itemRoute, data={"visible": "pouet"}, headers={"Authorization": "Bearer " + bobAccountToken()})

        assert response.status_code == 400
        assert response.json == {
            "message": "Picture visibility parameter (visible) should be either unset, true or false",
            "status_code": 400,
        }


@conftest.SEQ_IMGS
def test_patch_item_nullvisibility(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)
        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)

        response = client.patch(itemRoute, data={}, headers={"Authorization": "Bearer " + bobAccountToken()})

        assert response.status_code == 304


@conftest.SEQ_IMGS
def test_patch_item_unchangedvisibility(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)
        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)

        response = client.patch(itemRoute, data={"visible": "true"}, headers={"Authorization": "Bearer " + bobAccountToken()})

        assert response.status_code == 200


@conftest.SEQ_IMGS
def test_patch_item_contenttype(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)
        itemRoute = "/api/collections/" + str(seqId) + "/items/" + str(picId)

        response = client.patch(
            itemRoute,
            data={"visible": "false"},
            headers={"Content-Type": "multipart/form-data; whatever=blabla", "Authorization": "Bearer " + bobAccountToken()},
        )

        assert response.status_code == 200

        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                newStatus = cursor.execute("SELECT status FROM pictures WHERE id = %s", [picId]).fetchone()
                assert newStatus and newStatus[0] == "hidden"


@conftest.SEQ_IMGS
def test_delete_picture_on_demand(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        # before the delte, we can query the first picture
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 200

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert len(response.json["features"]) == 5
        assert first_pic_id in [f["id"] for f in response.json["features"]]

        assert os.path.exists(
            datafiles / "derivates" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8] / first_pic_id[9:]
        )
        assert os.path.exists(datafiles / "permanent" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8])

        response = client.delete(
            f"/api/collections/{sequence.id}/items/{first_pic_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 204

        # The first picture should not be returned in any response
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert len(response.json["features"]) == 4
        assert first_pic_id not in [f["id"] for f in response.json["features"]]

        # requesting the picture now should result in a 404
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        # and we should not see it anymore in the collection's item
        all_pics = client.get(f"/api/collections/{sequence.id}/items")
        assert all_pics.status_code == 200
        assert len(all_pics.json["features"]) == 4
        assert first_pic_id not in [f["id"] for f in all_pics.json["features"]]

        # same for deleting it again
        response = client.delete(
            f"/api/collections/{sequence.id}/items/{first_pic_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 404

        waitForAllJobsDone(current_app)
        # after a while, check that all files have correctly been deleted
        assert not os.path.exists(
            datafiles / "derivates" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8] / first_pic_id[9:]
        )
        assert not os.path.exists(datafiles / "permanent" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8])
        # there should be no empty directory
        for dirpath, dirname, files in itertools.chain(os.walk(datafiles / "permanent"), os.walk(datafiles / "derivates")):
            assert files or dirname, f"directory {dirpath} is empty"


@conftest.SEQ_IMGS
def test_delete_picture_preprocess(datafiles, initSequenceApp, dburl, bobAccountToken):
    """Deleting a picture with the API configured as preprocess should work fine, and all derivates should be deleted"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        # before the delte, we can query the first picture
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 200

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert len(response.json["features"]) == 5
        assert first_pic_id in [f["id"] for f in response.json["features"]]

        assert os.path.exists(
            datafiles / "derivates" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8] / first_pic_id[9:]
        )
        assert os.path.exists(datafiles / "permanent" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8])

        response = client.delete(
            f"/api/collections/{sequence.id}/items/{first_pic_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 204

        # The first picture should not be returned in any response
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert len(response.json["features"]) == 4
        assert first_pic_id not in [f["id"] for f in response.json["features"]]

        # requesting the picture now should result in a 404
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        # and after a while since it's asynchrone, the files will be deleted
        waitForAllJobsDone(current_app)

        assert not os.path.exists(
            datafiles / "derivates" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8] / first_pic_id[9:]
        )
        assert not os.path.exists(datafiles / "permanent" / first_pic_id[0:2] / first_pic_id[2:4] / first_pic_id[4:6] / first_pic_id[6:8])
        # there should be no empty directory
        for dirpath, dirname, files in itertools.chain(os.walk(datafiles / "permanent"), os.walk(datafiles / "derivates")):
            assert files or dirname, f"directory {dirpath} is empty"


@conftest.SEQ_IMGS
def test_delete_picture_no_auth(datafiles, initSequenceApp, dburl):
    """Deleting a picture wihout being identified is forbidden"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id
        response = client.delete(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 401


@conftest.SEQ_IMGS
def test_delete_picture_as_another_user(datafiles, initSequenceApp, dburl, defaultAccountToken):
    """
    Deleting a not owned picture should be forbidden
    Here the pictures are owned by Bob and the default account tries to delete them
    """
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id
        response = client.delete(
            f"/api/collections/{sequence.id}/items/{first_pic_id}", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
        )
        assert response.status_code == 403


@conftest.SEQ_IMGS
def test_delete_picture_still_waiting_for_process(datafiles, tmp_path, initSequenceApp, dburl, bobAccountToken):
    """Deleting a picture that is still waiting to be processed should be fine (and the picture should be removed from the process queue)"""

    with create_test_app(
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
    ) as app:
        with app.test_client() as client, psycopg.connect(dburl) as conn:
            seq_location = conftest.createSequence(client, os.path.basename(datafiles), jwtToken=bobAccountToken())
            seq_id = seq_location.split("/")[-1]
            pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, jwtToken=bobAccountToken())

            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 1

            r = conn.execute("SELECT id, status FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "waiting-for-process")]

            assert os.path.exists(datafiles / "permanent" / pic_id[0:2] / pic_id[2:4] / pic_id[4:6] / pic_id[6:8])
            assert not os.path.exists(datafiles / "derivates" / pic_id[0:2] / pic_id[2:4] / pic_id[4:6] / pic_id[6:8] / pic_id[9:])

            response = client.delete(f"/api/collections/{seq_id}/items/{pic_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
            assert response.status_code == 204

            # the picture has been removed right away from the database
            r = conn.execute("SELECT count(*) FROM pictures").fetchone()
            assert r and r[0] == 0

            # but an async task asking for delete should be in the queue
            r = conn.execute("SELECT picture_id, picture_to_delete_id, task FROM job_queue").fetchall()
            assert r == [(None, UUID(pic_id), "delete")]

            # pic should not have been deleted, since for this test there is no background workers
            assert os.path.exists(datafiles / "permanent" / pic_id[0:2] / pic_id[2:4] / pic_id[4:6] / pic_id[6:8])


@conftest.SEQ_IMGS
def test_patch_item_history(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            # at first there is nothing
            assert cursor.execute("SELECT sequences_changes_id, previous_value_changed FROM pictures_changes", []).fetchall() == []

            r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
            initial_updated_at = r.json["properties"]["updated"]

            # hiding a value should add an entry to the pictures_changes table
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{first_pic_id}",
                data={"visible": "false"},
                headers={"Authorization": "Bearer " + bobAccountToken()},
            )
            assert response.status_code == 200
            # updating the visibility updates the updated_at field
            assert response.json["properties"]["updated"] > initial_updated_at

            pic_changes = cursor.execute("SELECT sequences_changes_id, previous_value_changed FROM pictures_changes", []).fetchall()
            assert pic_changes == [
                {"sequences_changes_id": None, "previous_value_changed": {"status": "ready"}},
            ]
            seq_changes = cursor.execute(
                "SELECT previous_value_changed, sequence_id::text, account_id FROM sequences_changes", []
            ).fetchall()
            assert seq_changes == []  # no associated sequences_changes, only a picture has been modified

            # hiding again should not do anything
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{first_pic_id}",
                data={"visible": "false"},
                headers={"Authorization": "Bearer " + bobAccountToken()},
            )
            assert response.status_code == 200

            pic_changes = cursor.execute(
                "SELECT picture_id::text, sequences_changes_id, previous_value_changed FROM pictures_changes", []
            ).fetchall()
            assert pic_changes == [
                {"picture_id": first_pic_id, "sequences_changes_id": None, "previous_value_changed": {"status": "ready"}},
            ]

            # setting the picture back to visible should add another entry
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{first_pic_id}",
                data={"visible": "true"},
                headers={"Authorization": "Bearer " + bobAccountToken()},
            )
            assert response.status_code == 200

            pic_changes = cursor.execute(
                "SELECT picture_id::text, sequences_changes_id, previous_value_changed FROM pictures_changes ORDER BY ts", []
            ).fetchall()
            assert pic_changes == [
                {"picture_id": first_pic_id, "sequences_changes_id": None, "previous_value_changed": {"status": "ready"}},
                {"picture_id": first_pic_id, "sequences_changes_id": None, "previous_value_changed": {"status": "hidden"}},
            ]


@conftest.SEQ_IMGS
def test_patch_item_heading(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")

            heading = r.json["properties"]["view:azimuth"]
            assert heading == 349

            pic = cursor.execute("SELECT heading, heading_computed FROM pictures WHERE id = %s", [first_pic_id]).fetchone()
            assert pic and pic["heading"] == 349 and pic["heading_computed"] is False

            # we change the heading
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{first_pic_id}",
                data={"heading": "66"},
                headers={"Authorization": "Bearer " + bobAccountToken()},
            )
            assert response.status_code == 200

            pic = cursor.execute("SELECT heading, heading_computed FROM pictures WHERE id = %s", [first_pic_id]).fetchone()
            assert pic and pic["heading"] == 66 and pic["heading_computed"] is False

            pic_changes = cursor.execute(
                "SELECT sequences_changes_id, previous_value_changed, account_id FROM pictures_changes", []
            ).fetchall()
            assert pic_changes == [
                {"sequences_changes_id": None, "previous_value_changed": {"heading": 349}, "account_id": bobAccountID},
            ]


@conftest.SEQ_IMGS
def test_patch_item_heading_computed(datafiles, initSequenceApp, dburl, bobAccountToken):
    """Changing the collection relative headings should mark all headings as computed,
    and them manually changing a heading should mark the heading as manually computed"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        with psycopg.connect(dburl, row_factory=dict_row) as conn, conn.cursor() as cursor:
            r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")

            heading = r.json["properties"]["view:azimuth"]
            assert heading == 349
            old_updated_at = r.json["properties"]["updated"]
            pic = cursor.execute("SELECT heading, heading_computed FROM pictures WHERE id = %s", [first_pic_id]).fetchone()
            assert pic and pic["heading"] == 349 and pic["heading_computed"] is False

            # we change all the collection's pictures heading relatively to the mouvement
            # all headings should be marked as computed
            response = client.patch(
                f"/api/collections/{sequence.id}",
                data={"relative_heading": 90},
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            )
            pic = cursor.execute("SELECT heading, heading_computed FROM pictures WHERE id = %s", [first_pic_id]).fetchone()
            assert pic and pic["heading"] == 114 and pic["heading_computed"] is True
            # the updated_at field should have been updated
            after_seq_updates = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}").json["properties"]["updated"]
            assert after_seq_updates > old_updated_at

            # then we change the heading
            response = client.patch(
                f"/api/collections/{sequence.id}/items/{first_pic_id}",
                data={"heading": "66"},
                headers={"Authorization": "Bearer " + bobAccountToken()},
            )
            assert response.status_code == 200
            assert response.json["properties"]["updated"] > after_seq_updates

            pic = cursor.execute("SELECT heading, heading_computed FROM pictures WHERE id = %s", [first_pic_id]).fetchone()
            assert pic and pic["heading"] == 66 and pic["heading_computed"] is False

            pic_changes = cursor.execute(
                "SELECT previous_value_changed FROM pictures_changes WHERE picture_id = %s ORDER BY ts", [first_pic_id]
            ).fetchall()
            assert pic_changes == [
                # 2 changes, the first one for the relative headings, the second one manually
                {"previous_value_changed": {"heading": 349, "heading_computed": False}},
                {"previous_value_changed": {"heading": 114, "heading_computed": True}},
            ]


@conftest.SEQ_IMGS
def test_patch_item_invalid_headings(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"heading": "pouet"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Heading is not valid, should be an integer in degrees from 0° to 360°. North is 0°, East = 90°, South = 180° and West = 270°.",
            "status_code": 400,
        }

        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"heading": -2},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Heading is not valid, should be an integer in degrees from 0° to 360°. North is 0°, East = 90°, South = 180° and West = 270°.",
            "status_code": 400,
        }
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"heading": 400},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "message": "Heading is not valid, should be an integer in degrees from 0° to 360°. North is 0°, East = 90°, South = 180° and West = 270°.",
            "status_code": 400,
        }


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "focal_zero.jpg"))
def test_post_item_with_fov_zero(app, dburl, bobAccountToken):
    """Importing a picture with a fov=0 should not crash"""
    with app.app_context():
        pics = [Path(conftest.FIXTURE_DIR) / "focal_zero.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        r = client.get(f"/api/collections/{seqId}/items/{picId}")

        print(r.json["properties"]["pers:interior_orientation"])
        assert r.json["properties"]["pers:interior_orientation"]["focal_length"] == 0
        assert r.json["properties"]["pers:interior_orientation"].get("field_of_view") is None  # fov is not computed since the is no focal


@conftest.SEQ_IMGS
def test_patch_item_new_capture_time(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert r.status_code == 200
        old_capture_time = "2021-07-29T09:16:54+00:00"
        assert old_capture_time == r.json["properties"]["datetime"]
        old_updated_at = r.json["properties"]["updated"]
        new_ts = "2023-07-03T10:12:01.001Z"
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"capture_time": new_ts},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert r.status_code == 200
        c = r.json["properties"]["datetime"]
        assert c == "2023-07-03T10:12:01.001000+00:00"  # formated with timezone shift

        # the change should be recorded in the pictures_changes table
        pic_changes = db.fetchall(current_app, "SELECT previous_value_changed FROM pictures_changes", [])
        assert pic_changes == [
            ({"ts": old_capture_time},),
        ]
        # and the updated_at field should have been updated
        assert r.json["properties"]["updated"] > old_updated_at


@conftest.SEQ_IMGS
def test_patch_item_new_invalid_capture_time(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"capture_time": "pouet"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400
        assert response.json == {
            "details": {
                "error": "Unknown string format: pouet",
            },
            "message": "Parameter `capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z').",
            "status_code": 400,
        }
        # the change should not be recorded in the pictures_changes table
        pic_changes = db.fetchall(current_app, "SELECT sequences_changes_id, previous_value_changed FROM pictures_changes", [])
        assert pic_changes == []


@conftest.SEQ_IMGS
def test_patch_item_new_position(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert r.status_code == 200
        old_lat, old_lon = 1.919185442, 49.00688962
        assert old_lat == r.json["geometry"]["coordinates"][0]
        assert old_lon == r.json["geometry"]["coordinates"][1]

        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={"longitude": "42.2", "latitude": "4.2"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        r = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert r.status_code == 200
        assert 42.2 == r.json["geometry"]["coordinates"][0]
        assert 4.2 == r.json["geometry"]["coordinates"][1]

        # the change should not be recorded in the pictures_changes table
        pic_changes = db.fetchall(current_app, "SELECT previous_value_changed FROM pictures_changes", [])
        assert len(pic_changes) == 1
        assert round(pic_changes[0][0]["geom"]["coordinates"][0], 6) == round(old_lat, 6)
        assert round(pic_changes[0][0]["geom"]["coordinates"][1], 6) == round(old_lon, 6)


@pytest.mark.parametrize(
    ("lon", "lat", "error"),
    (
        (None, "42.3", {"message": "Latitude cannot be overridden alone, longitude also needs to be set", "status_code": 400}),
        ("42.3", None, {"message": "Longitude cannot be overridden alone, latitude also needs to be set", "status_code": 400}),
        (
            "-299",
            "42.3",
            {
                "details": {
                    "error": "longitude needs to be between -180 and 180",
                },
                "message": "For parameter `longitude`, `-299.0` is not a valid longitude",
                "status_code": 400,
            },
        ),
        (
            "42.3",
            "prout",
            {
                "details": [
                    {
                        "error": "Input should be a valid number, unable to parse string as a number",
                        "fields": ["latitude"],
                        "input": "prout",
                    }
                ],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
    ),
)
@conftest.SEQ_IMGS
def test_patch_item_new_position_errors(datafiles, initSequenceApp, dburl, bobAccountToken, lon, lat, error):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        override = {k: v for k, v in {"longitude": lon, "latitude": lat}.items() if v is not None}
        response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data=override,
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 400

        assert response.json == error

        # this should not change the history of the picture
        pic_changes = db.fetchall(current_app, "SELECT previous_value_changed FROM pictures_changes", [])
        assert pic_changes == []


@conftest.SEQ_IMGS
def test_patch_item_update_tags(datafiles, initSequenceApp, dburl, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value"},
                    {"key": "some_tag", "value": "another_value"},
                    {"key": "some_other_tag", "value": "some_other_value"},
                ]
            },
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert patch_response.status_code == 200, patch_response.text
        assert patch_response.json["properties"]["semantics"] == [
            {"key": "some_other_tag", "value": "some_other_value"},
            {"key": "some_tag", "value": "another_value"},
            {"key": "some_tag", "value": "some_value"},
        ]
        get_resp = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert get_resp.status_code == 200
        assert get_resp.json == patch_response.json

        # all those updated tags should be in the history
        assert get_tags_history() == {
            "pictures": [
                (
                    UUID(first_pic_id),
                    "bob",
                    [
                        {"action": "add", "key": "some_tag", "value": "some_value"},
                        {"action": "add", "key": "some_tag", "value": "another_value"},
                        {"action": "add", "key": "some_other_tag", "value": "some_other_value"},
                    ],
                ),
            ],
        }

        # we can also remove tags
        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
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
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert patch_response.status_code == 200, patch_response.text
        assert patch_response.json["properties"]["semantics"] == [
            {"key": "another_great_tag", "value": "we can also add tags in the meantime"},
            {"key": "some_tag", "value": "another_value"},
        ]
        get_resp = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert get_resp.status_code == 200
        assert get_resp.json == patch_response.json

        # all those updated tags should be in the history
        assert get_tags_history() == {
            "pictures": [
                (
                    UUID(first_pic_id),
                    "bob",
                    [
                        {"action": "add", "key": "some_tag", "value": "some_value"},
                        {"action": "add", "key": "some_tag", "value": "another_value"},
                        {"action": "add", "key": "some_other_tag", "value": "some_other_value"},
                    ],
                ),
                (
                    UUID(first_pic_id),
                    "bob",
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

        # we can also find the tags when querying for several items
        get_resp = client.get(f"/api/collections/{sequence.id}/items")
        assert get_resp.status_code == 200

        first_pic = next(p for p in get_resp.json["features"] if p["id"] == first_pic_id)
        assert first_pic["properties"]["semantics"] == [
            {"key": "another_great_tag", "value": "we can also add tags in the meantime"},
            {"key": "some_tag", "value": "another_value"},
        ]

        # or when searching for a picture
        r = client.get(f'/api/search?ids=["{first_pic_id}"]')
        assert r.status_code == 200
        assert len(r.json["features"]) == 1
        assert r.json["features"][0]["properties"]["semantics"] == [
            {"key": "another_great_tag", "value": "we can also add tags in the meantime"},
            {"key": "some_tag", "value": "another_value"},
        ]

        # test that we can delete the collection afterward
        r = client.delete(f"/api/collections/{sequence.id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 204

        # there is nothing in the db afterthis
        assert db.fetchall(current_app, "SELECT * FROM sequences_semantics WHERE sequence_id = %s", [sequence.id]) == []
        assert db.fetchall(current_app, "SELECT * FROM sequences_semantics_history WHERE sequence_id = %s", [sequence.id]) == []
        assert db.fetchall(current_app, "SELECT * FROM pictures_semantics WHERE picture_id = %s", [first_pic_id]) == []
        assert db.fetchall(current_app, "SELECT * FROM pictures_semantics_history WHERE picture_id = %s", [first_pic_id]) == []


@conftest.SEQ_IMG
def test_patch_item_update_tags_no_logged(datafiles, initSequenceApp, dburl, bobAccountToken):
    """As for the other editing APIs, for the moment you need to be logged in to edit tags"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
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


@conftest.SEQ_IMG
def test_patch_item_update_tags_another_user(datafiles, initSequenceApp, dburl, defaultAccountToken):
    """As for the other editing APIs anyone can edit the tags"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id
        initial_updated_at = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}").json["properties"]["updated"]

        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value"},
                ]
            },
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
        )
        assert patch_response.status_code == 200, patch_response.text
        assert patch_response.json["properties"]["semantics"] == [
            {"key": "some_tag", "value": "some_value"},
        ]
        assert patch_response.json["properties"]["updated"] > initial_updated_at


@conftest.SEQ_IMG
def test_patch_item_update_tags_form(datafiles, initSequenceApp, dburl, bobAccountToken):
    """Tags cannot be added as form-data for the moment"""
    with initSequenceApp(datafiles, preprocess=True, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            data={
                "semantics": [
                    {"key": "some_tag", "value": "some_value"},
                ]
            },
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert patch_response.status_code == 400, patch_response.text


@pytest.mark.parametrize(
    ("tags", "error"),
    (
        ([{"key": "some_tag", "value": "some_value"}], None),
        (
            [{"key": "a" * 257, "value": "some_value"}],
            {
                "details": [
                    {
                        "error": "String should have at most 256 characters",
                        "fields": [
                            "semantics",
                            0,
                            "key",
                        ],
                    },
                ],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        (
            [{"key": "some key with too long value", "value": "a" * 2049}],
            {
                "details": [
                    {
                        "error": "String should have at most 2048 characters",
                        "fields": [
                            "semantics",
                            0,
                            "value",
                        ],
                    },
                ],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        ([{"key": "🙊", "value": "🥳"}], None),  # utf8 accepted
        (
            [{"key": "dup", "value": "👥"}, {"key": "dup", "value": "👥"}],
            {
                "details": {"duplicate": "Key (picture_id, key, value)=({pic_id}, dup, 👥) already exists."},
                "message": "Impossible to add semantic tags because of duplicates",
                "status_code": 400,
            },
        ),
    ),
)
@conftest.SEQ_IMGS
def test_patch_item_update_tags_cases(datafiles, initSequenceApp, dburl, bobAccountToken, tags, error):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        patch_response = client.patch(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            json={"semantics": tags},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        if error is None:
            assert patch_response.status_code == 200, patch_response.text
        else:
            assert patch_response.status_code == 400, patch_response.text
            err = patch_response.json
            print(err)
            if isinstance(err["details"], list):
                for d in err["details"]:
                    if "input" in d:
                        del d["input"]  # input is too long, we don't want to compare it
            else:
                err["details"]["duplicate"] = err["details"]["duplicate"].replace(first_pic_id, "{pic_id}")
            assert err == error


@pytest.mark.parametrize(
    ("patch_payload", "owner_accept_collaborative_editing", "instance_default_collaborative_editing", "error"),
    [
        ({}, True, False, None),
        ({}, False, False, None),  # empty payload is accepted, even when collaborative editing is forbidden
        # changing the visibility is always forbidden
        (
            {"visible": "true", "semantics": [{"key": "t", "value": "some_value"}]},
            True,
            True,
            "You're not authorized to edit the visibility of this picture. Only the owner can change this.",
        ),
        (
            {"visible": "false", "sortby": "+gpsdate", "semantics": [{"key": "t", "value": "some_value"}]},
            True,
            True,
            "You're not authorized to edit the visibility of this picture. Only the owner can change this.",
        ),
        # changin the heading/capture_time/position depends on the account's collaborative editing if set, else it depend on the instance's default
        ({"heading": 12}, True, True, None),
        ({"heading": 12}, None, None, None),  # default to True
        ({"heading": 42, "semantics": [{"key": "t", "value": "some_value"}]}, None, True, None),
        (
            {"heading": 12, "semantics": [{"key": "t", "value": "some_value"}]},
            False,
            True,
            "You're not authorized to edit this picture, collaborative editing is not allowed",
        ),
        (
            {"heading": 12, "semantics": [{"key": "t", "value": "some_value"}]},
            None,
            False,
            "You're not authorized to edit this picture, collaborative editing is not allowed",
        ),
        (
            {"capture_time": "2023-07-03T10:12:01.001Z"},
            False,
            None,
            "You're not authorized to edit this picture, collaborative editing is not allowed",
        ),
        (
            {"longitude": "42.2", "latitude": "4.2"},
            False,
            None,
            "You're not authorized to edit this picture, collaborative editing is not allowed",
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
def test_patch_item_rights(
    app,
    dburl,
    camilleAccountToken,
    bobAccountID,
    patch_payload,
    owner_accept_collaborative_editing,
    instance_default_collaborative_editing,
    error,
):
    with app.test_client() as client:
        # Create a sequence wiht 1 picture owned by bob
        conftest.insert_db_model(
            conftest.ModelToInsert(
                upload_sets=[
                    conftest.UploadSetToInsert(
                        sequences=[conftest.SequenceToInsert(pictures=[conftest.PictureToInsert(original_file_name="1.jpg")])],
                        account_id=bobAccountID,
                    )
                ]
            )
        )
        seq, pic = getFirstPictureIds(dburl)
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
        r = client.patch(
            f"/api/collections/{seq}/items/{pic}", json=patch_payload, headers={"Authorization": f"Bearer {camilleAccountToken()}"}
        )
        if not error:
            assert r.status_code == 200 if patch_payload else 304
        else:
            assert r.status_code == 403
            assert r.json == {"message": error, "status_code": 403}


def test_search_sort_null_updated_at(app, dburl, bobAccountID):
    """Test that the sortby parameter in search is correct, even for null values"""

    with app.test_client() as client:
        # Create a sequence wiht 1 picture owned by bob
        inserted_at = datetime(year=2024, month=7, day=21, hour=10, minute=0, second=0)
        conftest.insert_db_model(
            conftest.ModelToInsert(
                upload_sets=[
                    conftest.UploadSetToInsert(
                        sequences=[
                            conftest.SequenceToInsert(
                                pictures=[
                                    conftest.PictureToInsert(original_file_name="1.jpg", ts=inserted_at + timedelta(minutes=1)),
                                    conftest.PictureToInsert(original_file_name="2.jpg", ts=inserted_at + timedelta(minutes=2)),
                                    conftest.PictureToInsert(original_file_name="3.jpg", ts=inserted_at + timedelta(minutes=3)),
                                    conftest.PictureToInsert(original_file_name="4.jpg", ts=inserted_at + timedelta(minutes=4)),
                                    conftest.PictureToInsert(original_file_name="5.jpg", ts=inserted_at + timedelta(minutes=5)),
                                ]
                            )
                        ],
                        account_id=bobAccountID,
                    )
                ]
            )
        )
        # set 2 and 3 updated_at to null
        with db.conn(app) as conn:
            conn.execute(
                SQL("UPDATE pictures SET updated_at = NULL WHERE metadata->>'originalFileName' IN ('2.jpg', '3.jpg')"),
            )
        seqs = getPictureIds(dburl)

        r = client.get(f"/api/search?sortby=updated")
        assert r.status_code == 200
        assert len(r.json["features"]) == 5
        pics_name = [p["properties"]["original_file:name"] for p in r.json["features"]]
        assert pics_name[:3] == ["1.jpg", "4.jpg", "5.jpg"]

        assert set(pics_name[3:]) == {"2.jpg", "3.jpg"}
