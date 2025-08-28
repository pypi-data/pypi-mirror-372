from datetime import datetime
import math
from dateutil.tz import UTC
import dateutil.parser
from fs import open_fs
from tests.conftest import (
    SEQ_IMGS,
    add_files_to_upload_set,
    create_upload_set,
    create_test_app,
    get_upload_set,
    is_valid_datetime,
    start_background_worker,
    waitForUploadSetState,
    waitForUploadSetStateReady,
    get_tags_history,
    get_job_history,
)
import psycopg
import pytest
import os
from uuid import UUID
from geopic_tag_reader import reader
import dateutil
from geovisio.utils import db
from flask import current_app
from psycopg.sql import SQL
from psycopg.rows import dict_row
from .conftest import FIXTURE_DIR, waitForAllJobsDone
from geopic_tag_reader.writer import writePictureMetadata, PictureMetadata, Direction


@pytest.fixture
def app_client_with_auth(dburl, tmp_path, fsesUrl):
    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "SECRET_KEY": "a very secret key",
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_FORCE_AUTH_ON_UPLOAD": "true",
            }
        ) as app,
        app.test_client() as client,
    ):
        yield client


@pytest.fixture
def app_client_without_auth(dburl, tmp_path, fsesUrl):
    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "SECRET_KEY": "a very secret key",
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_FORCE_AUTH_ON_UPLOAD": "false",
            }
        ) as app,
        app.test_client() as client,
    ):
        yield client


@pytest.mark.parametrize(
    ("params"),
    (
        ({"title": "some title"}),
        (
            {
                "title": "some title",
                "sort_method": "time-desc",
                "split_distance": 10,
                "split_time": 79,
                "duplicate_distance": 12,
                "duplicate_rotation": 42,
            }
        ),
        ({"title": "some title", "estimated_nb_files": 12}),
        ({"title": "metadata title", "metadata": {"dirnames": ["some", "dir", "names"]}}),
    ),
)
def test_post_upload_set_no_auth_mandatory(app_client_without_auth, params):
    response = app_client_without_auth.post("/api/upload_sets", json=params)
    assert response.status_code == 200, response.text
    # all upload set should have an id, a creation date and not be completed
    assert response.json["id"] and UUID(response.json["id"])
    assert response.json["created_at"] and dateutil.parser.parse(response.json["created_at"])
    assert response.json["completed"] is False
    assert response.json["links"] == [
        {
            "rel": "self",
            "type": "application/json",
            "href": f"http://localhost:5000/api/upload_sets/{response.json['id']}",
        }
    ]

    assert response.headers["Location"] == f"http://localhost:5000/api/upload_sets/{response.json['id']}"

    for k, v in params.items():
        assert response.json[k] == v

    u = db.fetchall(current_app, "SELECT * FROM upload_sets")
    assert len(u) == 1

    response = app_client_without_auth.get(f"/api/upload_sets/{response.json['id']}", json=params)
    assert response.status_code == 200, response.text
    for k, v in params.items():
        assert response.json[k] == v


def test_post_upload_set_no_auth_mandatory_no_json(app_client_without_auth):
    response = app_client_without_auth.post("/api/upload_sets")
    assert response.status_code == 415, response.text
    assert response.json == {"message": "Parameter for creating an UploadSet should be a valid JSON", "status_code": 415}


def test_post_upload_set_no_auth_mandatory_no_title(app_client_without_auth):
    response = app_client_without_auth.post("/api/upload_sets", json={})
    assert response.status_code == 400, response.text
    assert response.json == {
        "message": "Impossible to create an UploadSet",
        "status_code": 400,
        "details": [{"error": "Field required", "fields": ["title"]}],
    }


def test_post_upload_set_no_auth_mandatory_invalid_sort_method(app_client_without_auth):
    response = app_client_without_auth.post(
        "/api/upload_sets",
        json={"title": "some title", "sort_method": "pouet"},
    )
    assert response.status_code == 400, response.text
    assert response.json == {
        "message": "Impossible to create an UploadSet",
        "status_code": 400,
        "details": [
            {
                "error": "Input should be 'filename-asc', 'filename-desc', 'time-asc' or 'time-desc'",
                "fields": ["sort_method"],
                "input": "pouet",
            }
        ],
    }


def test_post_upload_set_no_auth_mandatory_invalid_duplicate_distance_and_duplicate_rotation(app_client_without_auth):
    response = app_client_without_auth.post(
        "/api/upload_sets",
        json={"title": "some title", "duplicate_distance": "pouet", "duplicate_rotation": "plop"},
    )
    assert response.status_code == 400, response.text
    assert response.json == {
        "details": [
            {
                "error": "Input should be a valid number, unable to parse string as a number",
                "fields": ["duplicate_distance"],
                "input": "pouet",
            },
            {
                "error": "Input should be a valid integer, unable to parse string as an integer",
                "fields": ["duplicate_rotation"],
                "input": "plop",
            },
        ],
        "message": "Impossible to create an UploadSet",
        "status_code": 400,
    }


@pytest.mark.parametrize(
    ("sort_method", "expected_names"),
    (
        (
            "filename-asc",
            [
                "some_names_001.jpg",
                "some_names_002.jpg",
                "some_names_010.jpg",
                "some_names_011.jpg",
                "some_names_312.jpg",
            ],
        ),
        (
            "filename-desc",
            [
                "some_names_312.jpg",
                "some_names_011.jpg",
                "some_names_010.jpg",
                "some_names_002.jpg",
                "some_names_001.jpg",
            ],
        ),
        (
            "time-asc",
            [
                "some_names_010.jpg",
                "some_names_001.jpg",
                "some_names_002.jpg",
                "some_names_312.jpg",
                "some_names_011.jpg",
            ],
        ),
        (
            "time-desc",
            [
                "some_names_011.jpg",
                "some_names_312.jpg",
                "some_names_002.jpg",
                "some_names_001.jpg",
                "some_names_010.jpg",
            ],
        ),
    ),
)
@SEQ_IMGS
def test_upload_set_sort_by_filename(datafiles, app_client_with_auth, bobAccountToken, bobAccountID, sort_method, expected_names):
    """Test the sort by filename. Filename should be sorted using natural sort"""
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, title="some title", sort_method=sort_method, estimated_nb_files=5, jwtToken=bobAccountToken())

    os.rename(datafiles / "1.jpg", datafiles / "some_names_010.jpg")
    os.rename(datafiles / "2.jpg", datafiles / "some_names_001.jpg")
    os.rename(datafiles / "3.jpg", datafiles / "some_names_002.jpg")
    os.rename(datafiles / "4.jpg", datafiles / "some_names_312.jpg")
    os.rename(datafiles / "5.jpg", datafiles / "some_names_011.jpg")

    # we add the pictures in a random order
    for name in ["some_names_010.jpg", "some_names_011.jpg", "some_names_312.jpg", "some_names_001.jpg", "some_names_002.jpg"]:
        add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / name, jwtToken=bobAccountToken())

    # since we have set the estimated_number_of_files, the upload set should be completed
    waitForUploadSetStateReady(app_client_with_auth, upload_set_id, timeout=10)

    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r["associated_collections"]
    assert len(associated_cols) == 1
    col_id = UUID(associated_cols[0]["id"])
    associated_cols[0].pop("extent")
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "associated_collections": [
            {
                "id": str(col_id),
                "nb_items": 5,
                "ready": True,
                "title": "some title",
                "items_status": {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0},
                "links": [{"rel": "self", "href": f"http://localhost:5000/api/collections/{str(col_id)}", "type": "application/json"}],
            }
        ],
        "completed": True,
        "dispatched": True,
        "estimated_nb_files": 5,
        "id": upload_set_id,
        "nb_items": 5,
        "semantics": [],
        "sort_method": sort_method,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query this collection, and find all the pictures
    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
    assert col_r.status_code == 200, col_r.text
    assert col_r.json["stats:items"] == {"count": 5}

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
    assert col_r.status_code == 200, col_r.text
    names = [f["properties"]["original_file:name"] for f in col_r.json["features"]]
    assert names == expected_names


@SEQ_IMGS
def test_post_upload_set_auth_mandatory_ok(app_client_with_auth, bobAccountToken, bobAccountID):
    response = app_client_with_auth.post(
        "/api/upload_sets",
        json={"title": "some title"},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    # all upload set should have an id, a creation date and not be completed
    assert response.json["id"] and UUID(response.json["id"])
    assert response.json["created_at"] and dateutil.parser.parse(response.json["created_at"])
    assert response.json["completed"] is False
    assert response.json["account_id"] == str(bobAccountID)
    u = db.fetchall(current_app, "SELECT * FROM upload_sets")
    assert len(u) == 1


@SEQ_IMGS
def test_post_upload_set_auth_mandatory_no_auth(app_client_with_auth):
    response = app_client_with_auth.post(
        "/api/upload_sets",
        json={"title": "some title"},
    )
    assert response.status_code == 401, response.text
    assert response.json == {"message": "Authentication is mandatory"}


@SEQ_IMGS
def test_add_item_to_upload_set_auth_mandatory_ok(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), metadata={"some": "metadata", "an_array": ["pouet"]})

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    # id must be valid uuid
    pic_id = UUID(r.pop("picture_id"))
    r.pop("inserted_at")
    assert r == {
        "file_name": "1.jpg",
        "content_md5": "d969aec7bc8f564173c767313150e499",
        "size": 3296115,
        "file_type": "picture",
        "links": [
            {
                "href": f"http://localhost:5000/api/upload_sets/{upload_set_id}",
                "rel": "parent",
                "type": "application/json",
            }
        ],
        # Note: no `rejected` field
    }

    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    items_status = upload_set_r.pop("items_status")
    assert items_status["broken"] == 0
    assert items_status["prepared"] + items_status["not_processed"] == 1
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "associated_collections": [],
        "ready": False,
        "created_at": created_at,
        "completed": False,
        "dispatched": False,
        "id": upload_set_id,
        "nb_items": 1,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "metadata": {"an_array": ["pouet"], "some": "metadata"},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # anonymous query to this upload set should be possible
    anonymous_upload_set_r = get_upload_set(client, upload_set_id, token=None)
    anonymous_upload_set_r.pop("items_status")  # we cannot compare the status as it is changing in the background
    assert anonymous_upload_set_r == upload_set_r

    # if we add the same file again, we get a conflict
    response = add_files_to_upload_set(client, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert response.status_code == 409, response.text
    assert response.json == {
        "existing_item": {"id": str(pic_id)},
        "message": "The item has already been added to this upload set",
        "status_code": 409,
    }

    # since it's in the same upload set, another `file` is not added in the uploadset
    f = _get_upload_set_files(client, upload_set_id, bobAccountToken())
    simplified_files = [{k: v for k, v in f.items() if k in {"file_name", "file_type", "size", "rejected"}} for f in f["files"]]
    assert simplified_files == [
        {"file_name": "1.jpg", "file_type": "picture", "size": 3296115},
    ]

    # at the end, we only sent 1 files to the first upload set, so it's not completed, but the pictures are prepared
    s = waitForUploadSetState(app_client_with_auth, upload_set_id, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)
    assert s["dispatched"] is False
    assert s["completed"] is False
    assert s["ready"] is False


@SEQ_IMGS
def test_add_item_to_upload_set_already_blurred(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

    r = add_files_to_upload_set(
        client, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken(), additional_data={"isBlurred": "true"}
    )

    r = db.fetchone(current_app, SQL("SELECT metadata FROM pictures WHERE id = %s"), [r["picture_id"]])
    assert r and r[0]["blurredByAuthor"] is True

    s = waitForUploadSetStateReady(app_client_with_auth, upload_set_id)
    assert s["ready"] is True


@SEQ_IMGS
def test_add_item_to_upload_set_external_metadata(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)
    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "1.jpg",
        jwtToken=bobAccountToken(),
        additional_data={
            "override_capture_time": "2023-07-03T10:12:01.001Z",
            "override_Exif.Image.Artist": "R. Doisneau",
            "override_Xmp.xmp.Rating": "5",
        },
    )

    r = db.fetchone(current_app, SQL("SELECT exif, ts FROM pictures WHERE id = %s"), [r["picture_id"]])
    assert r[0]["Exif.Image.Artist"] == "R. Doisneau"
    assert r[0]["Xmp.xmp.Rating"] == "5"
    assert r[1] == datetime(2023, 7, 3, 10, 12, 1, 1000, tzinfo=UTC)

    s = waitForUploadSetStateReady(app_client_with_auth, upload_set_id)

    assert s["ready"] is True
    assert s["nb_items"] == 1

    assert s["completed"] is True
    assert s["dispatched"] is True
    assert s["estimated_nb_files"] == 1
    assert s["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 0}
    assert len(s["associated_collections"]) == 1
    col_id = s["associated_collections"][0]["id"]
    assert s["associated_collections"][0] == {
        "id": col_id,
        "ready": True,
        "items_status": {
            "broken": 0,
            "not_processed": 0,
            "prepared": 1,
            "preparing": 0,
        },
        "extent": {
            "temporal": {"interval": [["2023-07-03T10:12:01.001000Z", "2023-07-03T10:12:01.001000Z"]]},
        },
        "nb_items": 1,
        "title": "some title",
        "links": [
            {
                "href": f"http://localhost:5000/api/collections/{col_id}",
                "rel": "self",
                "type": "application/json",
            }
        ],
    }


@SEQ_IMGS
def test_add_item_to_upload_set_external_lat_lon(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

    lat = 42.42
    lon = 4.42
    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "1.jpg",
        jwtToken=bobAccountToken(),
        additional_data={"override_longitude": lon, "override_latitude": lat},
    )
    file_id = r["picture_id"]

    r = db.fetchone(current_app, SQL("SELECT ST_X(geom), ST_Y(geom) FROM pictures WHERE id = %s"), [file_id])
    assert r and math.isclose(r[0], lon)
    assert r and math.isclose(r[1], lat)

    # we also check that the stored picture has the correct exif tags
    f = os.path.join(datafiles, "permanent", file_id[0:2], file_id[2:4], file_id[4:6], file_id[6:8], f"{file_id[9:]}.jpg")
    with open(f, "rb") as img:
        tags = reader.readPictureMetadata(img.read())
    assert math.isclose(tags.lat, lat)
    assert math.isclose(tags.lon, lon)

    s = waitForUploadSetStateReady(app_client_with_auth, upload_set_id)

    # at the end, the upload set should be dispatch, a collection created, and the picture prepared
    assert s["ready"] is True
    assert s["nb_items"] == 1

    assert s["completed"] is True
    assert s["dispatched"] is True
    assert s["estimated_nb_files"] == 1
    assert s["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 0}

    assert len(s["associated_collections"]) == 1
    assert {
        "ready": True,
        "items_status": {
            "broken": 0,
            "not_processed": 0,
            "prepared": 1,
            "preparing": 0,
        },
        "nb_items": 1,
    }.items() <= s[
        "associated_collections"
    ][0].items()


@SEQ_IMGS
def test_add_item_to_upload_set_external_lat_lon_missing(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "1.jpg",
        jwtToken=bobAccountToken(),
        additional_data={"override_longitude": 42},
        raw_response=True,
    )
    assert r.status_code == 400 and r.json == {
        "message": "Longitude cannot be overridden alone, override_latitude also needs to be set",
        "status_code": 400,
    }

    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "1.jpg",
        jwtToken=bobAccountToken(),
        additional_data={"override_latitude": 42},
        raw_response=True,
    )
    assert r.status_code == 400 and r.json == {
        "message": "Latitude cannot be overridden alone, override_longitude also needs to be set",
        "status_code": 400,
    }


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"))
def test_add_item_to_upload_set_i18n_error(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "e1_without_exif.jpg",
        jwtToken=bobAccountToken(),
        raw_response=True,
        headers={"Accept-Language": "fr, en"},
    )
    assert r.status_code == 400
    assert r.json == {
        "details": {
            "error": "Des métadonnées obligatoires sont manquantes\u202f:\n\t- Coordonnées GPS absentes ou invalides dans les attributs EXIF de l'image\n\t- Aucune date valide dans les attributs EXIF de l'image",
            "missing_fields": [
                "datetime",
                "location",
            ],
        },
        "message": "Impossible de lire les métadonnées de la photo",
        "status_code": 400,
    }


@SEQ_IMGS
def test_add_item_to_upload_no_auth(datafiles, app_client_without_auth, defaultAccountID):
    """It auth is not mandatory, we should be able to add anonymously to an upload set"""
    upload_set_id = create_upload_set(app_client_without_auth, jwtToken=None, estimated_nb_files=1)

    r = add_files_to_upload_set(app_client_without_auth, upload_set_id, datafiles / "1.jpg", jwtToken=None)

    # and all is linked to the default account
    a = db.fetchone(current_app, "SELECT account_id FROM pictures WHERE id = %s", [r["picture_id"]])
    assert a == (defaultAccountID,)
    a = db.fetchone(current_app, "SELECT account_id FROM upload_sets WHERE id = %s", [upload_set_id])
    assert a == (defaultAccountID,)

    # at the end, the upload set will be completed, and the picture prepared, and dispatched to some collection
    s = waitForUploadSetState(app_client_without_auth, upload_set_id, wanted_state=lambda x: x.json["dispatched"] is True)
    assert s["dispatched"] is True
    assert s["completed"] is True


@SEQ_IMGS
def test_item_already_added_in_another_upload_set(datafiles, app_client_with_auth, bobAccountToken):
    """If a file has already been added to an uploadset, we cannot add it into another uploadset"""
    upload_set_1_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=2)
    upload_set_2_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), title="some other title", estimated_nb_files=2)

    r = add_files_to_upload_set(app_client_with_auth, upload_set_1_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    # id must be valid uuid
    inserted_at = r.pop("inserted_at")
    is_valid_datetime(inserted_at)
    pic_id = r.pop("picture_id")

    assert r == {
        "file_name": "1.jpg",
        "content_md5": "d969aec7bc8f564173c767313150e499",
        "size": 3296115,
        "file_type": "picture",
        "links": [
            {
                "href": f"http://localhost:5000/api/upload_sets/{upload_set_1_id}",
                "rel": "parent",
                "type": "application/json",
            }
        ],
    }

    # we first add 1 valid file to this uploadset
    response = add_files_to_upload_set(app_client_with_auth, upload_set_2_id, datafiles / "2.jpg", jwtToken=bobAccountToken())

    # if we add the same file into the other upload_set, we get a conflict
    response = add_files_to_upload_set(
        app_client_with_auth, upload_set_2_id, datafiles / "1.jpg", jwtToken=bobAccountToken(), raw_response=True
    )
    assert response.status_code == 409, response.text
    assert response.json == {
        "message": "The same picture has already been sent in a past upload",
        "status_code": 409,
        "upload_sets": [{"existing_item_id": str(pic_id), "upload_set_id": str(upload_set_1_id)}],
    }

    # This error should be tracked as it's not a client error, so we should be able to find this `file` (but not the picture) in the uploadset
    f = _get_upload_set_files(app_client_with_auth, upload_set_2_id, bobAccountToken())
    simplified_files = [{k: v for k, v in f.items() if k in {"file_name", "file_type", "size", "rejected"}} for f in f["files"]]
    assert simplified_files == [
        {"file_name": "2.jpg", "file_type": "picture", "size": 3251027},
        {
            "file_name": "1.jpg",
            "file_type": "picture",
            "size": 3296115,
            "rejected": {
                "message": "The same picture has already been sent in a past upload",
                "reason": "file_duplicate",
                "severity": "error",
            },
        },
    ]

    # at the end, we only sent 1 files to the first upload set, so it's not completed, but the pictures are prepared
    s = waitForUploadSetState(app_client_with_auth, upload_set_1_id, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)
    assert s["dispatched"] is False
    assert s["completed"] is False
    assert s["ready"] is False

    # and the 2nd one should be completed since we expect 2 files and 2 files were sent
    s = waitForUploadSetState(app_client_with_auth, upload_set_2_id, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)
    assert s["completed"] is True  # should be completed since we expected 1 file and 1 file was sent


@pytest.fixture
def app_client_with_auth_and_duplicates(dburl, tmp_path, fsesUrl):
    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "SECRET_KEY": "a very secret key",
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_FORCE_AUTH_ON_UPLOAD": "true",
                "API_ACCEPT_DUPLICATE": "true",
            }
        ) as app,
        app.test_client() as client,
    ):
        yield client


@SEQ_IMGS
def test_duplicate_authorized(datafiles, app_client_with_auth_and_duplicates, bobAccountToken):
    """If a file has already been added to an uploadset, we can add it into another uploadset if the instance authorize duplicates
    We cannot however add it to the same uploadset
    """
    client = app_client_with_auth_and_duplicates
    upload_set_1_id = create_upload_set(client, jwtToken=bobAccountToken())
    upload_set_2_id = create_upload_set(client, jwtToken=bobAccountToken(), title="some other title")

    add_files_to_upload_set(client, upload_set_1_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    r2 = add_files_to_upload_set(client, upload_set_2_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    # we can also add it on the same uploadset
    r = add_files_to_upload_set(client, upload_set_2_id, datafiles / "1.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 409, r.text
    assert r.json == {
        "existing_item": {"id": r2["picture_id"]},
        "message": "The item has already been added to this upload set",
        "status_code": 409,
    }

    _complete_upload_set(client, upload_set_1_id, token=bobAccountToken())
    _complete_upload_set(client, upload_set_2_id, token=bobAccountToken())

    # at the end, the 2 upload set will be completed, and the pictures prepared, and dispatched to some collection
    s = waitForUploadSetStateReady(client, upload_set_1_id)
    assert len(s["associated_collections"]) == 1
    s = waitForUploadSetStateReady(client, upload_set_2_id)
    assert len(s["associated_collections"]) == 1


@SEQ_IMGS
def test_add_item_no_auth_but_mandatory(datafiles, app_client_with_auth):
    """If the auth is configured as mandatory for upload, we cannot upload without a valid token"""
    response = app_client_with_auth.post("/api/upload_sets", json={"title": "some title"})
    assert response.status_code == 401, response.text
    assert response.json == {"message": "Authentication is mandatory"}

    # same with a invalid token
    response = app_client_with_auth.post("/api/upload_sets", json={"title": "some title"}, headers={"Authorization": "Bearer pouet"})
    assert response.status_code == 401, response.text
    assert response.json == {"details": {"error": "Impossible to decode token"}, "message": "Token not valid", "status_code": 401}


@SEQ_IMGS
def test_add_item_to_non_owned_upload_set(datafiles, app_client_with_auth, bobAccountToken, defaultAccountToken):
    """It's forbidden to add files to an upload set belonging to another user"""
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    response = add_files_to_upload_set(client, upload_set_id, datafiles / "1.jpg", jwtToken=defaultAccountToken(), raw_response=True)

    assert response.status_code == 403
    assert response.json == {"message": "You're not authorized to add picture to this upload set", "status_code": 403}


@SEQ_IMGS
def test_main_upload_set_workflow(datafiles, app_client_with_auth, bobAccountToken, bobAccountID, defaultAccountToken):
    """
    Test main upload set workflow.
    We create an UploadSet with an estimated of 2 files.
    We push the 2 files on it, and after a while a collection is created with the 2 items
    """
    upload_set_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=2)

    r = add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    pic_1_id = UUID(r["picture_id"])

    # if we query the upload set is it still not completed
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is False

    r = add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / "2.jpg", jwtToken=bobAccountToken())
    pic_2_id = UUID(r["picture_id"])

    # if we query the upload set, it is now marked as completed
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r[
        "associated_collections"
    ]  # since it's asynchronous, the associated collection can either be empty or filled
    dispatched = upload_set_r["dispatched"]
    items_status = upload_set_r[
        "items_status"
    ]  # same here, since it's asynchronous, we cannot assert the number of 'preparing'/'prepared' pictures
    upload_set_r.pop("ready")
    assert items_status["broken"] == 0
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "associated_collections": associated_cols,
        "completed": True,
        "dispatched": dispatched,
        "estimated_nb_files": 2,
        "id": upload_set_id,
        "nb_items": 2,
        "semantics": [],
        "sort_method": "time-asc",
        "items_status": items_status,
        "title": "some title",
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # we can query the files of the upload set
    upload_set_files_r = app_client_with_auth.get(
        f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"}
    )
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    assert len(upload_set_files_r.json["files"]) == 2
    first_file = upload_set_files_r.json["files"][0]
    inserted_at = first_file.pop("inserted_at")
    UUID(first_file.pop("picture_id"))
    is_valid_datetime(inserted_at)

    assert first_file == {
        "file_name": "1.jpg",
        "content_md5": "d969aec7bc8f564173c767313150e499",
        "size": 3296115,
        "file_type": "picture",
        "links": [
            {
                "href": f"http://localhost:5000/api/upload_sets/{upload_set_id}",
                "rel": "parent",
                "type": "application/json",
            }
        ],
        # Note: no `rejected` field
    }

    # we can query the files of the upload set as anonymous
    r = app_client_with_auth.get(f"/api/upload_sets/{upload_set_id}/files")
    assert r.status_code == 200, r.text
    assert len(r.json["files"]) == 2
    for f in r.json["files"]:
        # if we are not logged in, we cannot see the picture_id
        assert f.get("picture_id") is None

    # we can also query the files of the upload set logged in another user
    r = app_client_with_auth.get(f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert r.status_code == 200, r.text
    assert len(r.json["files"]) == 2
    for f in r.json["files"]:
        # if we are not bob,, we cannot see the picture_id
        assert f.get("picture_id") is None

    r = app_client_with_auth.get(f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 200, r.text
    assert len(r.json["files"]) == 2
    for f in r.json["files"]:
        # if we are logged in, we can see the picture_id
        assert "picture_id" in f

    waitForUploadSetStateReady(app_client_with_auth, upload_set_id, timeout=10)

    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r["associated_collections"]
    assert len(associated_cols) == 1
    col_id = UUID(associated_cols[0]["id"])

    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "associated_collections": [
            {
                "id": str(col_id),
                "nb_items": 2,
                "ready": True,
                "title": "some title",
                "extent": {
                    "temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:16:56Z"]]},
                },
                "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0},
                "links": [{"rel": "self", "href": f"http://localhost:5000/api/collections/{str(col_id)}", "type": "application/json"}],
            }
        ],
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 2,
        "id": upload_set_id,
        "nb_items": 2,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query this collection, and find all the pictures

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
    assert col_r.status_code == 200, col_r.text
    assert col_r.json["stats:items"] == {"count": 2}

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
    assert col_r.status_code == 200, col_r.text
    assert len(col_r.json["features"]) == 2

    # check all the background job history
    jobs = db.fetchall(
        current_app,
        "SELECT job_task, picture_id, sequence_id, upload_set_id, error FROM job_history ORDER BY started_at",
        row_factory=dict_row,
    )
    jobs = [{k: v for k, v in j.items() if v is not None} for j in jobs]
    assert jobs == [
        {"job_task": "prepare", "picture_id": pic_1_id},
        {"job_task": "prepare", "picture_id": pic_2_id},
        {"job_task": "dispatch", "upload_set_id": UUID(upload_set_id)},
        {"job_task": "finalize", "sequence_id": col_id},
    ]


@pytest.fixture
def app_client_with_split_workers(dburl, fsesUrl):
    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "SECRET_KEY": "a very secret key",
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_FORCE_AUTH_ON_UPLOAD": "true",
                "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
            }
        ) as app,
        app.test_client() as client,
    ):
        yield client


@SEQ_IMGS
def test_split_workers(app_client_with_split_workers, datafiles, dburl, tmp_path, bobAccountID, bobAccountToken):
    """
    Test posting new picture with some split workers to do the job
    """
    client = app_client_with_split_workers
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=2)

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    pic_1_id = UUID(r["picture_id"])

    # if we query the upload set is it still not completed
    upload_set_r = client.get(
        f"/api/upload_sets/{upload_set_id}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert upload_set_r.status_code == 200, upload_set_r.text
    assert upload_set_r.json["completed"] is False

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "2.jpg", jwtToken=bobAccountToken())
    pic_2_id = UUID(r["picture_id"])

    # if we query the upload set, it is now marked as completed, but since there are no background workers, no dispatch has been done
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["associated_collections"] == []
    assert upload_set_r["dispatched"] is False
    assert upload_set_r["ready"] is False
    assert upload_set_r["items_status"] == {"broken": 0, "not_processed": 2, "preparing": 0, "prepared": 0, "rejected": 0}

    # we start a background worker, it should start processing all pictures, and dispatch them to a collection
    background_worker(dburl, tmp_path)

    waitForUploadSetStateReady(client, upload_set_id)

    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r["associated_collections"]
    assert len(associated_cols) == 1
    col_id = UUID(associated_cols[0]["id"])
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "associated_collections": [
            {
                "id": str(col_id),
                "nb_items": 2,
                "title": "some title",
                "ready": True,
                "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0},
                "extent": {
                    "temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:16:56Z"]]},
                },
                "links": [{"rel": "self", "href": f"http://localhost:5000/api/collections/{str(col_id)}", "type": "application/json"}],
            }
        ],
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 2,
        "id": upload_set_id,
        "nb_items": 2,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query this collection, and find all the pictures
    col_r = client.get(f"/api/collections/{str(col_id)}")
    assert col_r.status_code == 200, col_r.text
    assert "geovisio:status" not in col_r.json
    assert col_r.json["stats:items"] == {"count": 2}

    col_r = client.get(f"/api/collections/{str(col_id)}/items")
    assert col_r.status_code == 200, col_r.text
    assert len(col_r.json["features"]) == 2

    # check all the background job history
    jobs = db.fetchall(
        current_app,
        "SELECT job_task, picture_id, sequence_id, upload_set_id, error FROM job_history ORDER BY started_at",
        row_factory=dict_row,
    )
    jobs = [{k: v for k, v in j.items() if v is not None} for j in jobs]
    assert jobs == [
        {"job_task": "prepare", "picture_id": pic_1_id},
        {"job_task": "prepare", "picture_id": pic_2_id},
        {"job_task": "dispatch", "upload_set_id": UUID(upload_set_id)},
        {"job_task": "finalize", "sequence_id": col_id},
    ]


def background_worker(dburl, tmp_path, wait=True):
    return start_background_worker(
        dburl,
        tmp_path,
        config={
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
        },
        wait=wait,
    )


def test_complete_unknown_upload_set(client):
    response = client.post(
        "/api/upload_sets/00000000-0000-0000-0000-000000000000/complete",
    )
    assert response.status_code == 404
    assert response.json == {"message": "UploadSet 00000000-0000-0000-0000-000000000000 does not exist", "status_code": 404}


def test_complete_un_owned_upload_set(app_client_with_auth, bobAccountToken, defaultAccountToken):
    response = app_client_with_auth.post(
        "/api/upload_sets",
        json={"title": "some title"},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    id = response.json["id"]
    response = app_client_with_auth.post(
        f"/api/upload_sets/{id}/complete",
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert response.status_code == 403
    assert response.json == {"message": "You're not authorized to complete this upload set", "status_code": 403}

    # without auth should result in error too
    response = app_client_with_auth.post(
        f"/api/upload_sets/{id}/complete",
    )
    assert response.status_code == 401
    assert response.json == {"message": "Authentication is mandatory"}


@SEQ_IMGS
def test_upload_set_with_manual_completion(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """
    Test upload workflow with manual completion.
    We do not set an estimated number of files, and we manually complete the upload set
    After a while a collection is created with the 2 items
    """
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken())

    # if we query the upload set is it still not completed
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is False

    add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / "2.jpg", jwtToken=bobAccountToken())

    # if we query the upload set is it still not completed
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is False

    # we manually complete the upload set
    upload_set_r = _complete_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True

    # and after a while, the collection is created
    waitForUploadSetStateReady(app_client_with_auth, upload_set_id)

    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r["associated_collections"]
    assert len(associated_cols) == 1
    col_id = UUID(associated_cols[0]["id"])
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "associated_collections": [
            {
                "id": str(col_id),
                "nb_items": 2,
                "ready": True,
                "title": "some title",
                "extent": {
                    "temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:16:56Z"]]},
                },
                "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0},
                "links": [{"rel": "self", "href": f"http://localhost:5000/api/collections/{str(col_id)}", "type": "application/json"}],
            }
        ],
        "completed": True,
        "dispatched": True,
        "id": upload_set_id,
        "nb_items": 2,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query this collection, and find all the pictures

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
    assert col_r.status_code == 200, col_r.text
    assert "geovisio:status" not in col_r.json
    assert col_r.json["stats:items"] == {"count": 2}

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
    assert col_r.status_code == 200, col_r.text
    assert len(col_r.json["features"]) == 2

    # adding more picture is possible
    response = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/files",
        data={"file": (datafiles / "3.jpg").open("rb")},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 202, response.text

    # since more pictures were added, the upload set should be now marked as uncompleted
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is False
    assert upload_set_r["dispatched"] is True  # but still dispatched

    # we should complete it for the last picture to be dispatched
    response = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        data={"file": (datafiles / "3.jpg").open("rb")},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    waitForAllJobsDone(current_app, timeout=3)
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "associated_collections": [
            {
                "id": str(col_id),  # <- it should be the same id as before
                "nb_items": 3,
                "ready": True,
                "title": "some title",
                "extent": {
                    "temporal": {
                        "interval": [
                            [
                                "2021-07-29T09:16:54Z",
                                "2021-07-29T09:16:58Z",  # <- the interval has been updated to include the last picture (was 16:56 before)
                            ]
                        ]
                    },
                },
                "items_status": {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0},
                "links": [{"rel": "self", "href": f"http://localhost:5000/api/collections/{str(col_id)}", "type": "application/json"}],
            }
        ],
        "completed": True,
        "dispatched": True,
        "id": upload_set_id,
        "nb_items": 3,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query this collection, and find all the pictures

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
    assert col_r.status_code == 200, col_r.text
    assert "geovisio:status" not in col_r.json
    assert col_r.json["stats:items"] == {"count": 3}

    col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
    assert col_r.status_code == 200, col_r.text
    assert len(col_r.json["features"]) == 3


@SEQ_IMGS
def test_split_workers_manual_completion(app_client_with_split_workers, datafiles, dburl, tmp_path, bobAccountID, bobAccountToken):
    """
    Test posting new picture with some split workers to do the job

    We simulate that the estimated number of pictures cannot be reached, and we manually complete the upload set, after all pictures have been prepared.
    The collection is created with the 2 items.
    """
    client = app_client_with_split_workers
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=3)

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    pic_1_id = UUID(r["picture_id"])

    # if we query the upload set is it still not completed
    upload_set_r = client.get(
        f"/api/upload_sets/{upload_set_id}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert upload_set_r.status_code == 200, upload_set_r.text
    assert upload_set_r.json["completed"] is False

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "2.jpg", jwtToken=bobAccountToken())
    pic_2_id = UUID(r["picture_id"])

    # we start a background worker, it should start processing all pictures, but since the estimated number of files is not reached, the upload set is not completed, and no collection is created
    background_worker(dburl, tmp_path)

    s = waitForUploadSetState(client, upload_set_id, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)
    assert s["completed"] is False
    assert s["dispatched"] is False
    assert s["ready"] is False

    # we manually complete the upload set
    response = client.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    assert response.json["completed"] is True

    # the dispatch is asynchronous, so at first, the upload set is not dispatched
    response = client.get(
        f"/api/upload_sets/{upload_set_id}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    assert response.json["completed"] is True
    assert response.json["dispatched"] is False
    assert response.json["ready"] is False
    assert response.json["associated_collections"] == []

    # we start a background worker, it should handle the dispatching of the upload set (and the collection finalization)
    background_worker(dburl, tmp_path)

    s = waitForUploadSetStateReady(client, upload_set_id)

    # and since all pictures were prepared, the collection is created
    assert len(s["associated_collections"]) > 0
    assert s["completed"] is True
    assert s["dispatched"] is True
    assert s["ready"] is True

    # check all the background job history
    jobs = db.fetchall(
        current_app,
        "SELECT job_task, picture_id, sequence_id, upload_set_id, error FROM job_history ORDER BY started_at",
        row_factory=dict_row,
    )
    jobs = [{k: v for k, v in j.items() if v is not None} for j in jobs]
    assert jobs == [
        {"job_task": "prepare", "picture_id": pic_1_id},
        {"job_task": "prepare", "picture_id": pic_2_id},
        {"job_task": "dispatch", "upload_set_id": UUID(upload_set_id)},
        {"job_task": "finalize", "sequence_id": UUID(s["associated_collections"][0]["id"])},
    ]


def _complete_upload_set(client, id, token):
    response = client.post(
        f"/api/upload_sets/{id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    return response.json


def _delete_upload_set(client, id, token):
    response = client.delete(
        f"/api/upload_sets/{id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204, response.text


def _get_upload_set_files(client, upload_set_id, token, raw_response=False):
    upload_set_files_r = client.get(f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {token}"})
    if raw_response:
        return upload_set_files_r
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    return upload_set_files_r.json


@pytest.mark.parametrize(
    ("limit", "error"),
    (
        (
            "10000",
            {
                "details": [{"error": "Input should be less than or equal to 1000", "fields": ["limit"], "input": "10000"}],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        (
            "-1",
            {
                "details": [{"error": "Input should be greater than or equal to 0", "fields": ["limit"], "input": "-1"}],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        (
            "pouet",
            {
                "details": [
                    {
                        "error": "Input should be a valid integer, unable to parse string as an integer",
                        "fields": ["limit"],
                        "input": "pouet",
                    }
                ],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
    ),
)
def test_list_upload_sets_limits(app_client_with_auth, bobAccountToken, limit, error):
    """limit cannot exceed 1000"""
    response = app_client_with_auth.get(
        f"/api/users/me/upload_sets?limit={limit}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 400, response.text
    assert response.json == error


@SEQ_IMGS
def test_list_upload_sets(datafiles, app_client_with_auth, bobAccountToken):
    """
    list the upload sets

    We have 3 upload sets:
    u1: 2 files, completed and dispatched
    u2: 0 files, completed and dispatched
    u3: 1 files, not completed, not dispatched
    """
    u1 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken())
    u2 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken())
    u3 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken())

    add_files_to_upload_set(app_client_with_auth, u1, datafiles / "1.jpg", jwtToken=bobAccountToken())
    add_files_to_upload_set(app_client_with_auth, u1, datafiles / "2.jpg", jwtToken=bobAccountToken())

    add_files_to_upload_set(app_client_with_auth, u3, datafiles / "3.jpg", jwtToken=bobAccountToken())

    _complete_upload_set(app_client_with_auth, u1, token=bobAccountToken())
    _complete_upload_set(app_client_with_auth, u2, token=bobAccountToken())

    u1_state = waitForUploadSetState(app_client_with_auth, u1, wanted_state=lambda x: x.json["dispatched"] is True)
    u2_state = waitForUploadSetState(app_client_with_auth, u2, wanted_state=lambda x: x.json["dispatched"] is True)
    u3_state = waitForUploadSetState(app_client_with_auth, u3, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)

    assert u1_state["completed"] is True
    assert u1_state["dispatched"] is True

    assert u2_state["completed"] is True
    assert u2_state["dispatched"] is True

    assert u3_state["completed"] is False
    assert u3_state["dispatched"] is False

    def _get_upload_sets_id(r):
        return [x["id"] for x in r.json["upload_sets"]]

    response = app_client_with_auth.get(
        "/api/users/me/upload_sets",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    # by default, we should have only the non dispatched upload sets
    assert _get_upload_sets_id(response) == [u3]

    # if we want everything, we are forced to either give an empty filter, or a filter that matches everything
    response = app_client_with_auth.get(
        "/api/users/me/upload_sets?filter=",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    assert _get_upload_sets_id(response) == [u1, u2, u3]

    response = app_client_with_auth.get(
        "/api/users/me/upload_sets?limit=2&filter=",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    assert _get_upload_sets_id(response) == [u1, u2]

    response = app_client_with_auth.get(
        "/api/users/me/upload_sets?filter=completed=TRUE",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    assert _get_upload_sets_id(response) == [u1, u2]

    response = app_client_with_auth.get(
        "/api/users/me/upload_sets?filter=completed=false AND dispatched = FALSE",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    assert _get_upload_sets_id(response) == [u3]


ALL_IMGS = pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "1.jpg"),
    os.path.join(FIXTURE_DIR, "2.jpg"),
    os.path.join(FIXTURE_DIR, "3.jpg"),
    os.path.join(FIXTURE_DIR, "4.jpg"),
    os.path.join(FIXTURE_DIR, "5.jpg"),
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "e4.jpg"),
    os.path.join(FIXTURE_DIR, "e5.jpg"),
    os.path.join(FIXTURE_DIR, "b1.jpg"),
    os.path.join(FIXTURE_DIR, "b2.jpg"),
)


@ALL_IMGS
def test_upload_set_deletion(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """We create and uploadset with 2 collections.
    When we delete the first collection, the 2nd colllection should be kept.
    When we delete the 2nd collection, the uploadset is deleted
    """
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=8)

    for p in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "e1.jpg", "e2.jpg", "e3.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    # 8 files should have been received
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 8

    waitForUploadSetStateReady(client, upload_set_id)
    # if we query the upload set, it is now marked as completed
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True

    associated_cols = upload_set_r["associated_collections"]
    # 2 collections should have been created
    assert len(associated_cols) == 2

    cols = {c["nb_items"]: c["id"] for c in associated_cols}
    # the first collection should have 5 pictures, the second collection 3
    col1_id = cols[5]
    col2_id = cols[3]

    r = client.delete(f"/api/collections/{col1_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 204, r.text

    waitForAllJobsDone(current_app, timeout=3)
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True  # <- still completed

    associated_cols = upload_set_r["associated_collections"]
    # only 1 collection now
    assert len(associated_cols) == 1
    # still 8 files received, the files are not deleted when the pictures are
    # Note: not sure about this one, but it feels the right way to do it, it can be changed though
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 8

    # one collection in the global pool
    r = client.get("/api/collections")
    assert r.status_code == 200, r.text
    assert len(r.json["collections"]) == 1

    assert db.fetchone(current_app, "SELECT COUNT(*) FROM pictures")[0] == 3  # <- only 3 pictures remain

    r = client.delete(f"/api/collections/{col2_id}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 204, r.text

    waitForAllJobsDone(current_app, timeout=3)
    # for the moment the upload set is not deleted, but that could change in the future
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    assert db.fetchone(current_app, "SELECT COUNT(*) FROM pictures")[0] == 0  # <- no pictures
    assert db.fetchone(current_app, "SELECT COUNT(*) FROM upload_sets")[0] == 0
    # the sequences are kept, but marked as deleted
    assert db.fetchall(current_app, "SELECT status FROM sequences") == [("deleted",), ("deleted",)]


@SEQ_IMGS
def test_patch_upload_set(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """Patch an existing uploadset"""
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

    for p in ["1.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    waitForUploadSetStateReady(client, upload_set_id)
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    upload_set_r.pop("associated_collections")
    upload_set_r.pop("created_at")
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 1,
        "id": upload_set_id,
        "nb_items": 1,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    r = client.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"split_distance": 1, "split_time": 57.5},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    us = r.json
    us.pop("associated_collections")
    us.pop("created_at")
    assert us == {
        "account_id": str(bobAccountID),
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 1,
        "id": upload_set_id,
        "nb_items": 1,
        "semantics": [],
        "sort_method": "time-asc",
        "split_distance": 1,
        "split_time": 57.5,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }


@SEQ_IMGS
def test_patch_upload_set_forbidden(datafiles, app_client_with_auth, bobAccountToken, bobAccountID, defaultAccountToken):

    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

    # it should be forbidden to patch without credentials
    response = client.patch(f"/api/upload_sets/{upload_set_id}", json={"split_distance": 2})
    assert response.status_code == 401
    assert response.json == {
        "message": "Authentication is mandatory",
    }

    # it should be forbidden to patch an unowned uploadset
    response = client.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"split_distance": 2},
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert response.status_code == 403
    assert response.json == {
        "message": "You are not allowed to update this upload set",
        "status_code": 403,
    }

    # empty updates are ok
    r = client.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200
    us = r.json
    us.pop("associated_collections")
    us.pop("created_at")
    assert us == {
        "account_id": str(bobAccountID),
        "completed": False,
        "dispatched": False,
        "ready": False,
        "estimated_nb_files": 1,
        "id": upload_set_id,
        "nb_items": 0,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 0, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # for the moment we cannot update the titles
    r = client.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"title": "new title"},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 400
    assert r.json == {
        "details": [
            {
                "error": "Extra inputs are not permitted",
                "fields": [
                    "title",
                ],
                "input": "new title",
            },
        ],
        "message": "Impossible to update the UploadSet",
        "status_code": 400,
    }


@SEQ_IMGS
def test_patch_upload_set_unknown(datafiles, app_client_with_auth, bobAccountToken, bobAccountID, defaultAccountToken):
    # or an unknown upload_set
    response = app_client_with_auth.patch(
        f"/api/upload_sets/00000000-0000-0000-0000-000000000000",
        json={"split_distance": 2},
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert response.status_code == 404, response.text
    assert response.json == {
        "message": "UploadSet doesn't exist",
        "status_code": 404,
    }


@ALL_IMGS
def test_main_upload_set_dispatch_to_several_collections(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """
    Test dispatching to several collections, and the itempotence of the dispatch

    At first we add 9 files to the upload set, and 2 collections should be created

    Then we add another 3 files, and a third collection should be created (and one item should be added to a previous collection).

    The ids of the collections might change after the dispatch
    """
    # Note: configure a split time at 2mn since b1 and b2 are 90s apart
    upload_set_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=9, split_time=120)

    for p in datafiles.iterdir():
        if p.suffix == ".jpg" and p.name not in ["b1.jpg", "b2.jpg", "e3.jpg"]:
            add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / p.name, jwtToken=bobAccountToken())

    # if we query the upload set, it is now marked as completed
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True

    # we can query the files of the upload set
    upload_set_files_r = app_client_with_auth.get(
        f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"}
    )
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    assert len(upload_set_files_r.json["files"]) == 9
    for p in upload_set_files_r.json["files"]:
        # no files should be rejected
        assert p.get("rejected", False) is False

    waitForUploadSetStateReady(app_client_with_auth, upload_set_id, timeout=10)

    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r.pop("associated_collections")
    # 2 collections should have been created
    assert len(associated_cols) == 2
    col_ids = {c["id"]: c["nb_items"] for c in associated_cols}

    associated_cols = _get_short_cols(associated_cols)
    expected_cols = [
        {
            "nb_items": 5,
            "extent": {"temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:17:02Z"]]}},
            "title": "some title-1",
            "items_status": {"prepared": 5, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
        {
            "nb_items": 4,
            "extent": {"temporal": {"interval": [["2022-10-19T07:56:34Z", "2022-10-19T07:56:42Z"]]}},
            "title": "some title-2",
            "items_status": {"prepared": 4, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
    ]
    assert associated_cols == expected_cols

    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 9,
        "id": upload_set_id,
        "nb_items": 9,
        "semantics": [],
        "sort_method": "time-asc",
        "split_time": 120.0,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 9, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query those collections, and find all the pictures
    for col_id, expected in col_ids.items():
        col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
        assert col_r.status_code == 200, col_r.text
        assert col_r.json["stats:items"] == {"count": expected}

        col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
        assert col_r.status_code == 200, col_r.text
        assert len(col_r.json["features"]) == expected

    # check all the background job history
    def get_jobs():
        return db.fetchall(
            current_app,
            "SELECT job_task, count(*) as nb FROM job_history GROUP BY job_task ORDER BY job_task",
            row_factory=dict_row,
        )

    assert get_jobs() == [
        {"job_task": "prepare", "nb": 9},
        {"job_task": "dispatch", "nb": 1},
        {"job_task": "finalize", "nb": 2},
    ]

    # we can complete again, and nothing should change
    response = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    waitForAllJobsDone(current_app, timeout=3)

    assert get_jobs() == [
        {"job_task": "prepare", "nb": 9},
        {"job_task": "dispatch", "nb": 2},
        {"job_task": "finalize", "nb": 4},  # <- the sequences were finalized again, since we do not check if there was a real change yet
    ]

    u = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    associated_cols = _get_short_cols(u["associated_collections"])
    assert associated_cols == expected_cols

    # we add the 3 other files, and a new collection should be created
    for p in {"b1.jpg", "b2.jpg", "e3.jpg"}:
        add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    waitForAllJobsDone(current_app, timeout=3)
    # since we did not explicitly complete the upload set, the new pictures have been added but not dispatched
    assert get_jobs() == [
        {"job_task": "prepare", "nb": 12},  # <- the new pictures have been processed
        {"job_task": "dispatch", "nb": 2},  # <- but no new dispatch nor collections
        {"job_task": "finalize", "nb": 4},
    ]
    u = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert u["nb_items"] == 12
    assert len(u["associated_collections"]) == 2

    # we complete the upload set, and the collections should be created
    response = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text

    waitForAllJobsDone(current_app, timeout=3)

    assert get_jobs() == [
        {"job_task": "prepare", "nb": 12},
        {"job_task": "dispatch", "nb": 3},
        {"job_task": "finalize", "nb": 7},  # <- the 4 last finalizations + the 3 new ones
    ]

    u = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    associated_cols = _get_short_cols(u["associated_collections"])
    expected_cols = [
        {
            "nb_items": 2,
            "extent": {"temporal": {"interval": [["2015-04-25T13:36:17Z", "2015-04-25T13:37:48Z"]]}},
            "title": "some title",
            "items_status": {"prepared": 2, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
        {
            "nb_items": 5,
            "extent": {"temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:17:02Z"]]}},
            "title": "some title",
            "items_status": {"prepared": 5, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
        {
            "nb_items": 5,
            "extent": {"temporal": {"interval": [["2022-10-19T07:56:34Z", "2022-10-19T07:56:42Z"]]}},
            "title": "some title",
            "items_status": {"prepared": 5, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
    ]
    cols = {}
    for col in u["associated_collections"]:
        r = app_client_with_auth.get(f"/api/collections/{str(col['id'])}/items")
        assert r.status_code == 200, r.text
        cols[col["id"]] = [r["properties"]["original_file:name"] for r in r.json["features"]]
    cols = sorted(cols.items(), key=lambda x: x[1][0])
    cols_values = [v for _, v in cols]
    assert cols_values == [
        ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"],
        ["b2.jpg", "b1.jpg"],  # <- all collection are sorted by capture time and b2 has been taken before b1
        ["e1.jpg", "e2.jpg", "e3.jpg", "e4.jpg", "e5.jpg"],
    ]

    # all collection should be readily usable
    r = db.fetchall(current_app, "SELECT id, ST_NPoints(geom) as nb_points FROM sequences")
    cols_geom = {str(r[0]): r[1] for r in r}

    assert cols_geom == {
        cols[0][0]: 5,
        # v- b1 and b2 are 80m apart, so no geometry is computed (since we split each geometry in 50m segments,and each segment would only have one point)
        cols[1][0]: None,
        cols[2][0]: 5,
    }


def _get_short_cols(cols):
    return sorted(
        [{k: v for k, v in c.items() if k in {"nb_items", "ready", "title", "extent", "items_status"}} for c in cols],
        key=lambda x: x["extent"]["temporal"]["interval"][0],
    )


@ALL_IMGS
def test_main_upload_set_dispatch_to_several_collections_deletion(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """
    Test dispatching to several collections by changing the dispatch parameter. Some collections should now be useless, and be deleted.

    At first we add 9 files to the upload set, and 2 collections should be created. Then we change the dispatch parameter to only keep the first collection.

    The first collection should have kept its id (we don't want to change it since the users might have changed some stuff on it (like the title, some annotations, ...))
    """
    # Note: configure a split time at 2mn since b1 and b2 are 90s apart
    upload_set_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=9, split_time=120)

    for p in datafiles.iterdir():
        if p.suffix == ".jpg" and p.name not in ["b1.jpg", "b2.jpg", "e3.jpg"]:
            add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / p.name, jwtToken=bobAccountToken())

    # if we query the upload set, it is now marked as completed
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True

    # we can query the files of the upload set
    upload_set_files_r = app_client_with_auth.get(
        f"/api/upload_sets/{upload_set_id}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"}
    )
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    assert len(upload_set_files_r.json["files"]) == 9
    for p in upload_set_files_r.json["files"]:
        # no files should be rejected
        assert p.get("rejected", False) is False

    waitForUploadSetStateReady(app_client_with_auth, upload_set_id, timeout=10)

    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r.pop("associated_collections")
    # 2 collections should have been created
    assert len(associated_cols) == 2
    col_ids = {c["id"]: c["nb_items"] for c in associated_cols}

    associated_cols = _get_short_cols(associated_cols)
    expected_cols = [
        {
            "nb_items": 5,
            "extent": {"temporal": {"interval": [["2021-07-29T09:16:54Z", "2021-07-29T09:17:02Z"]]}},
            "title": "some title-1",
            "items_status": {"prepared": 5, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
        {
            "nb_items": 4,
            "extent": {"temporal": {"interval": [["2022-10-19T07:56:34Z", "2022-10-19T07:56:42Z"]]}},
            "title": "some title-2",
            "items_status": {"prepared": 4, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
    ]
    assert associated_cols == expected_cols

    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 9,
        "id": upload_set_id,
        "nb_items": 9,
        "semantics": [],
        "sort_method": "time-asc",
        "split_time": 120.0,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 9, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    # we can query those collections, and find all the pictures
    for col_id, expected in col_ids.items():
        col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}")
        assert col_r.status_code == 200, col_r.text
        assert col_r.json["stats:items"] == {"count": expected}

        col_r = app_client_with_auth.get(f"/api/collections/{str(col_id)}/items")
        assert col_r.status_code == 200, col_r.text
        assert len(col_r.json["features"]) == expected

    # check all the background job history
    def get_jobs():
        return db.fetchall(
            current_app,
            "SELECT job_task, count(*) as nb FROM job_history GROUP BY job_task ORDER BY job_task",
            row_factory=dict_row,
        )

    assert get_jobs() == [
        {"job_task": "prepare", "nb": 9},
        {"job_task": "dispatch", "nb": 1},
        {"job_task": "finalize", "nb": 2},  # <- 2 sequences created and finalized
    ]

    # we change the split parameters of the upload_set
    r = app_client_with_auth.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"split_time": 999999999, "split_distance": 99999999},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200

    u = r.json
    associated_cols = u.pop("associated_collections")
    # the collectoins should not have been updated yet
    new_col_ids = {c["id"]: c["nb_items"] for c in associated_cols}
    assert col_ids == new_col_ids
    assert _get_short_cols(associated_cols) == expected_cols
    assert u == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 9,
        "id": upload_set_id,
        "nb_items": 9,
        "semantics": [],
        "sort_method": "time-asc",
        "split_distance": 99999999,
        "split_time": 999999999.00,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 9, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # we ask for the dispatch to be done again
    response = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    waitForAllJobsDone(current_app, timeout=3)

    assert get_jobs() == [
        {"job_task": "prepare", "nb": 9},
        {"job_task": "dispatch", "nb": 2},
        {"job_task": "finalize", "nb": 3},  # <- 2 sequences created and finalized at first + only 1 finalized at the second dispatch
    ]

    r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    associated_cols = _get_short_cols(r["associated_collections"])
    expected_cols = [
        {
            "nb_items": 9,
            "extent": {"temporal": {"interval": [["2015-04-25T13:36:17Z", "2022-10-19T07:56:42Z"]]}},
            "title": "some title",
            "items_status": {"prepared": 2, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
    ]

    # the second collection should have been deleted
    nb_cols = db.fetchall(current_app, "SELECT status FROM sequences")

    assert set((s[0] for s in nb_cols)) == {"deleted", "ready"}


@ALL_IMGS
def test_upload_set_no_split(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """Same test as test_main_upload_set_dispatch_to_several_collections but specificly asking not to dispatch to several collections."""
    # Note: configure a split time at 2mn since b1 and b2 are 90s apart
    upload_set_id = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=9, no_split=True)

    for p in datafiles.iterdir():
        if p.suffix == ".jpg" and p.name not in ["b1.jpg", "b2.jpg", "e3.jpg"]:
            add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / p.name, jwtToken=bobAccountToken())

    # if we query the upload set, it is now marked as completed
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True

    waitForUploadSetStateReady(app_client_with_auth, upload_set_id, timeout=10)

    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    created_at = upload_set_r["created_at"]
    assert dateutil.parser.parse(created_at)
    associated_cols = upload_set_r.pop("associated_collections")
    # only 1 collection should have been created
    assert len(associated_cols) == 1

    associated_cols = _get_short_cols(associated_cols)
    expected_cols = [
        {
            "nb_items": 9,
            "extent": {"temporal": {"interval": [["2021-07-29T09:16:54Z", "2022-10-19T07:56:42Z"]]}},
            "title": "some title",
            "items_status": {"prepared": 9, "preparing": 0, "broken": 0, "not_processed": 0},
            "ready": True,
        },
    ]
    assert associated_cols == expected_cols

    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "completed": True,
        "dispatched": True,
        "ready": True,
        "estimated_nb_files": 9,
        "id": upload_set_id,
        "nb_items": 9,
        "semantics": [],
        "sort_method": "time-asc",
        "no_split": True,
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 9, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # if I patch and dispatch again, we got 2 collections
    r = app_client_with_auth.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"no_split": False, "split_distance": 100, "split_time": 60},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    # just patching does nothing, we should complete it
    waitForAllJobsDone(current_app, timeout=1)
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert len(upload_set_r["associated_collections"]) == 1

    # but after a complete, we got our 2 collections
    r = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    waitForAllJobsDone(current_app, timeout=4)
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert len(upload_set_r["associated_collections"]) == 2


@SEQ_IMGS
def test_upload_set_no_dedup(datafiles, app_client_with_auth, bobAccountToken, fsesUrl):
    """A bit like `test_capture_duplicates` but explicitly telling not to remove capture duplicates"""
    client = app_client_with_auth

    # we change the coordinate of 2.jpg to be too close to 1.jpg

    with open(datafiles / "1.jpg", "rb") as f:
        pic1_metadata = reader.readPictureMetadata(f.read())
    with open(datafiles / "4.jpg", "rb") as f:
        pic4_metadata = reader.readPictureMetadata(f.read())

    _update_picture_metadata(
        datafiles,
        "2.jpg",
        PictureMetadata(
            longitude=pic1_metadata.lon,
            latitude=pic1_metadata.lat + 0.000001,  # <- roughtly 1m
            direction=Direction(pic1_metadata.heading or 0),
        ),
    )
    # pic 3 is too close to pic 1, but with a different heading, so the picture should be kept as it will likely contains useful information
    _update_picture_metadata(
        datafiles,
        "3.jpg",
        PictureMetadata(
            longitude=pic1_metadata.lon, latitude=pic1_metadata.lat + 0.000001, direction=Direction((pic1_metadata.heading or 0) + 90)
        ),
    )
    _update_picture_metadata(datafiles, "5.jpg", PictureMetadata(longitude=pic4_metadata.lon, latitude=pic4_metadata.lat + 0.000001))

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=5, no_deduplication=True)

    for p in ["1.jpg", "updated_2.jpg", "updated_3.jpg", "4.jpg", "updated_5.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    waitForAllJobsDone(current_app, timeout=5)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())

    assert u["nb_items"] == 5
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 5
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0, "rejected": 0}

    col_r = client.get(f"/api/collections/{str(u['associated_collections'][0]['id'])}")
    assert col_r.status_code == 200, col_r.text
    assert col_r.json["stats:items"] == {"count": 5}

    # and if we change this to ask for a deduplication, we pictures will be deleted
    r = app_client_with_auth.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"no_deduplication": False, "duplicate_distance": 1, "duplicate_rotation": 30},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    # just patching does nothing, we should complete it
    waitForAllJobsDone(current_app, timeout=1)
    upload_set_r = get_upload_set(app_client_with_auth, upload_set_id, token=bobAccountToken())
    assert len(upload_set_r["associated_collections"]) == 1
    assert upload_set_r["associated_collections"][0]["nb_items"] == 5

    # but after a complete, the capture duplicates are deleted
    r = app_client_with_auth.post(
        f"/api/upload_sets/{upload_set_id}/complete",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    waitForAllJobsDone(current_app, timeout=4)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())

    assert u["nb_items"] == 3
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 3
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0, "rejected": 2}

    col_r = client.get(f"/api/collections/{str(u['associated_collections'][0]['id'])}/items")
    assert col_r.status_code == 200, col_r.text
    assert [p["properties"]["original_file:name"] for p in col_r.json["features"]] == ["1.jpg", "updated_3.jpg", "4.jpg"]

    files = _get_upload_set_files(client, upload_set_id, bobAccountToken())
    pictures_id = [f.get("picture_id") for f in files["files"]]
    remaining_pictures_id = {pictures_id[0], pictures_id[2], pictures_id[3]}

    # check that the pictures have been completly removed from the database and the file system
    assert {str(r[0]) for r in db.fetchall(current_app, "SELECT id FROM pictures")} == remaining_pictures_id

    with open_fs(fsesUrl.permanent) as fs:
        f = {f.info.name for f in fs.glob("**/*jpg")}
        assert f == {f"{id[9:]}.jpg" for id in remaining_pictures_id}

    with open_fs(fsesUrl.tmp) as fs:
        f = {f.info.name for f in fs.glob("**/*jpg")}
        assert f == set()


@pytest.fixture()
def override_default_dedup(dburl):
    with psycopg.connect(dburl, autocommit=True) as c:
        c.execute(
            """UPDATE configurations SET default_duplicate_distance = NULL,
            default_duplicate_rotation = NULL,
            default_split_distance = NULL,
            default_split_time = NULL"""
        )
        yield
        # put back old values
        c.execute(
            """UPDATE configurations SET default_duplicate_distance = 1,
            default_duplicate_rotation = 60,
            default_split_distance = 100,
            default_split_time = interval '5 minute'"""
        )


@SEQ_IMGS
def test_upload_set_no_dedup_by_default(datafiles, app_client_with_auth, bobAccountToken, fsesUrl, override_default_dedup):
    """If the instance administrator set the duplicate values to null, by default there will be no deduplication on the upload_sets"""
    client = app_client_with_auth

    # we change the coordinate of 2.jpg to be too close to 1.jpg

    with open(datafiles / "1.jpg", "rb") as f:
        pic1_metadata = reader.readPictureMetadata(f.read())

    _update_picture_metadata(
        datafiles,
        "2.jpg",
        PictureMetadata(
            longitude=pic1_metadata.lon,
            latitude=pic1_metadata.lat + 0.000001,  # <- roughtly 1m
            direction=Direction(pic1_metadata.heading or 0),
        ),
    )
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    for p in ["1.jpg", "updated_2.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    waitForAllJobsDone(current_app, timeout=5)
    _complete_upload_set(client, upload_set_id, token=bobAccountToken())
    waitForAllJobsDone(current_app, timeout=5)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())

    assert u["nb_items"] == 2
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 2
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0, "rejected": 0}

    col_r = client.get(f"/api/collections/{str(u['associated_collections'][0]['id'])}")
    assert col_r.status_code == 200, col_r.text
    assert col_r.json["stats:items"] == {"count": 2}

    # and if we change this to ask for a deduplication, we pictures will be deleted
    r = app_client_with_auth.patch(
        f"/api/upload_sets/{upload_set_id}",
        json={"no_deduplication": False, "duplicate_distance": 1, "duplicate_rotation": 30},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text

    _complete_upload_set(client, upload_set_id, token=bobAccountToken())
    assert r.status_code == 200, r.text
    waitForAllJobsDone(current_app, timeout=4)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())

    assert u["nb_items"] == 1
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 1
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 1}


def _update_picture_metadata(datafiles, pic_name, metadata):
    with open(datafiles / pic_name, "rb") as f:
        d = f.read()
        d = writePictureMetadata(d, metadata)
        with open(datafiles / f"updated_{pic_name}", "wb") as out:
            out.write(d)


@SEQ_IMGS
def test_capture_duplicates(datafiles, app_client_with_auth, bobAccountToken, fsesUrl):
    """
    Picture too near in space and time should be marked as soft duplicate
    """
    client = app_client_with_auth

    # we change the coordinate of 2.jpg to be too close to 1.jpg

    with open(datafiles / "1.jpg", "rb") as f:
        pic1_metadata = reader.readPictureMetadata(f.read())
    with open(datafiles / "4.jpg", "rb") as f:
        pic4_metadata = reader.readPictureMetadata(f.read())

    _update_picture_metadata(
        datafiles,
        "2.jpg",
        PictureMetadata(
            longitude=pic1_metadata.lon,
            latitude=pic1_metadata.lat + 0.000001,  # <- roughtly 1m
            direction=Direction(pic1_metadata.heading or 0),
        ),
    )
    # pic 3 is too close to pic 1, but with a different heading, so the picture should be kept as it will likely contains useful information
    _update_picture_metadata(
        datafiles,
        "3.jpg",
        PictureMetadata(
            longitude=pic1_metadata.lon, latitude=pic1_metadata.lat + 0.000001, direction=Direction((pic1_metadata.heading or 0) + 90)
        ),
    )
    _update_picture_metadata(datafiles, "5.jpg", PictureMetadata(longitude=pic4_metadata.lon, latitude=pic4_metadata.lat + 0.000001))

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    for p in ["1.jpg", "updated_2.jpg", "updated_3.jpg", "4.jpg", "updated_5.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())
        # Note: no early errors yet, but that could change in the future

    waitForAllJobsDone(current_app, timeout=5)

    # since we'll also have async deletions jobs, we need to wait for them to be done
    _complete_upload_set(client, upload_set_id, token=bobAccountToken())
    waitForAllJobsDone(current_app, timeout=5)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())

    assert u["nb_items"] == 3
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 3  # only 3 files were kept at the end
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0, "rejected": 2}

    col_r = client.get(f"/api/collections/{str(u['associated_collections'][0]['id'])}")
    assert col_r.status_code == 200, col_r.text
    assert col_r.json["stats:items"] == {"count": 3}

    col_r = client.get(f"/api/collections/{str(u['associated_collections'][0]['id'])}/items")
    assert col_r.status_code == 200, col_r.text
    assert [p["properties"]["original_file:name"] for p in col_r.json["features"]] == ["1.jpg", "updated_3.jpg", "4.jpg"]

    files = _get_upload_set_files(client, upload_set_id, bobAccountToken())
    simplified_files = [{k: v for k, v in f.items() if k in {"file_name", "file_type", "size", "rejected"}} for f in files["files"]]

    assert simplified_files == [
        {"file_name": "1.jpg", "file_type": "picture", "size": 3296115},
        {
            "file_name": "updated_2.jpg",
            "file_type": "picture",
            "size": 3252501,
            "rejected": {
                "reason": "capture_duplicate",
                "severity": "info",
                "message": "The picture is too similar to another one (nearby and taken almost at the same time)",
                "details": {
                    "angle": 0,
                    "distance": 0.11,
                    "duplicate_of": files["files"][0]["picture_id"],
                },
            },
        },
        {"file_name": "updated_3.jpg", "file_type": "picture", "size": 3260595},
        {"file_name": "4.jpg", "file_type": "picture", "size": 3269447},
        {
            "file_name": "updated_5.jpg",
            "file_type": "picture",
            "size": 3339147,
            "rejected": {
                "reason": "capture_duplicate",
                "severity": "info",
                "message": "The picture is too similar to another one (nearby and taken almost at the same time)",
                "details": {
                    "angle": 6,
                    "distance": 0.11,
                    "duplicate_of": files["files"][3]["picture_id"],
                },
            },
        },
    ]
    pictures_id = [f.get("picture_id") for f in files["files"]]
    remaining_pictures_id = {pictures_id[0], pictures_id[2], pictures_id[3]}

    # check that the pictures have been completly removed from the database and the file system
    assert {str(r[0]) for r in db.fetchall(current_app, "SELECT id FROM pictures")} == remaining_pictures_id

    with open_fs(fsesUrl.permanent) as fs:
        f = {f.info.name for f in fs.glob("**/*jpg")}
        assert f == {f"{id[9:]}.jpg" for id in remaining_pictures_id}

    with open_fs(fsesUrl.tmp) as fs:
        f = {f.info.name for f in fs.glob("**/*jpg")}
        assert f == set()

    # We check the jobs logs, there should have been at least 3 prepare jobs (or more, since the dupplicates can also be prepared before being deleted, depending on the order of the jobs)
    # 1 dispatch for the upload set, 1 finalization for the sequence, and 2 deletions for the duplicates
    history = get_job_history()
    nb_jobs = {h["job_task"]: len([h2 for h2 in history if h2["job_task"] == h["job_task"]]) for h in history}
    assert 3 <= nb_jobs["prepare"] <= 5
    del nb_jobs["prepare"]
    assert nb_jobs == {"dispatch": 1, "finalize": 1, "delete": 2}


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "invalid_exif.jpg"),
    os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
)
def test_invalid_files(datafiles, app_client_with_auth, bobAccountToken, fsesUrl):
    """
    Send several invalid files to an upload set, and check that they are rejected but correclty tracked
    The valid files should be dispatched to a collection
    """
    client = app_client_with_auth

    with open(datafiles / "not_a_jpg.txt", "w") as f:
        f.write("not a jpg")

    with open(datafiles / "invalid.jpg", "w") as f:
        f.write("I'm no jpg")

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=6)

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "invalid_exif.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 400
    assert r.json == {
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
        "details": {
            "error": "No GPS coordinates or broken coordinates in picture EXIF tags",
            "missing_fields": [
                "location",
            ],
        },
    }

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "e1_without_exif.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 400
    assert r.json == {
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
        "details": {
            "error": """The picture is missing mandatory metadata:
\t- No GPS coordinates or broken coordinates in picture EXIF tags
\t- No valid date in picture EXIF tags""",
            "missing_fields": ["datetime", "location"],
        },
    }

    add_files_to_upload_set(client, upload_set_id, datafiles / "e2.jpg", jwtToken=bobAccountToken())

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "not_a_jpg.txt", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 400
    assert r.json == {
        "message": "Picture file is either missing or in an unsupported format (should be jpg)",
        "status_code": 400,
    }
    r = add_files_to_upload_set(client, upload_set_id, datafiles / "invalid.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 400
    assert r.json == {
        "message": "Impossible to open file as image. The only supported image format is jpg.",
        "status_code": 400,
    }

    add_files_to_upload_set(client, upload_set_id, datafiles / "e3.jpg", jwtToken=bobAccountToken())

    # upload set should be complete as we said we would upload 6 files
    waitForAllJobsDone(current_app, timeout=5)

    u = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert u["completed"] is True
    assert u["ready"] is True

    assert u["nb_items"] == 2
    assert len(u["associated_collections"]) == 1
    assert u["associated_collections"][0]["nb_items"] == 2
    assert u["associated_collections"][0]["ready"] is True
    assert u["associated_collections"][0]["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0}
    assert u["items_status"] == {"broken": 0, "not_processed": 0, "prepared": 2, "preparing": 0, "rejected": 4}

    files = _get_upload_set_files(client, upload_set_id, bobAccountToken())
    simplified_files = [{k: v for k, v in f.items() if k in {"file_name", "file_type", "size", "rejected"}} for f in files["files"]]

    assert simplified_files == [
        {
            "file_name": "invalid_exif.jpg",
            "file_type": "picture",
            "size": 1708671,
            "rejected": {
                "reason": "invalid_metadata",
                "severity": "error",
                "message": "No GPS coordinates or broken coordinates in picture EXIF tags",
                "details": {
                    "missing_fields": ["location"],
                },
            },
        },
        {
            "file_name": "e1_without_exif.jpg",
            "file_type": "picture",
            "size": 12769,
            "rejected": {
                "reason": "invalid_metadata",
                "severity": "error",
                "message": """The picture is missing mandatory metadata:
\t- No GPS coordinates or broken coordinates in picture EXIF tags
\t- No valid date in picture EXIF tags""",
                "details": {
                    "missing_fields": ["datetime", "location"],
                },
            },
        },
        {"file_name": "e2.jpg", "file_type": "picture", "size": 483454},
        {
            "file_name": "not_a_jpg.txt",
            "file_type": "picture",
            "rejected": {
                "reason": "invalid_file",
                "severity": "error",
                "message": "Picture file is either missing or in an unsupported format (should be jpg)",
            },
        },
        {
            "file_name": "invalid.jpg",
            "file_type": "picture",
            "size": 10,
            "rejected": {
                "reason": "invalid_file",
                "severity": "error",
                "message": "Impossible to open file as image. The only supported image format is jpg.",
            },
        },
        {"file_name": "e3.jpg", "file_type": "picture", "size": 529344},
    ]


@SEQ_IMGS
def test_invalid_api_calls_not_counted(datafiles, app_client_with_auth, bobAccountToken):
    """
    Invalid API calls should not count as received files
    """
    client = app_client_with_auth
    u_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=2)

    response = client.post(
        f"/api/upload_sets/{u_id}/files",
        data={"pouet": (datafiles / "1.jpg").open("rb")},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 400
    assert len(_get_upload_set_files(client, u_id, bobAccountToken())["files"]) == 0
    u = get_upload_set(client, u_id, bobAccountToken())
    assert u["nb_items"] == 0

    response = client.post(
        f"/api/upload_sets/{u_id}/files",
        data={"pouet": (datafiles / "1.jpg").open("rb")},
    )
    assert response.status_code == 401
    assert len(_get_upload_set_files(client, u_id, bobAccountToken())["files"]) == 0

    # add good file
    add_files_to_upload_set(client, u_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    pic_id = db.fetchone(current_app, "SELECT id FROM pictures")[0]

    # duplicate should count
    r = add_files_to_upload_set(client, u_id, datafiles / "1.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 409
    assert r.json == {
        "message": "The item has already been added to this upload set",
        "status_code": 409,
        "existing_item": {"id": str(pic_id)},
    }

    assert len(_get_upload_set_files(client, u_id, bobAccountToken())["files"]) == 1
    u = get_upload_set(client, u_id, bobAccountToken())
    assert u["nb_items"] == 1
    assert u["completed"] is False  # since it was waiting for 2 files


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"),
)
def test_correction_of_invalid_metadata(datafiles, app_client_with_auth, bobAccountToken):
    """
    Send first a file with bad metadata, then post the same file with corrected metadata
    """
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

    r = add_files_to_upload_set(client, upload_set_id, datafiles / "e1_without_exif.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 400
    assert r.json == {
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
        "details": {
            "error": "The picture is missing mandatory metadata:\n\t- No GPS coordinates or broken coordinates in picture EXIF tags\n\t- No valid date in picture EXIF tags",
            "missing_fields": [
                "datetime",
                "location",
            ],
        },
    }

    assert len(_get_upload_set_files(client, upload_set_id, bobAccountToken())["files"]) == 1
    u = get_upload_set(client, upload_set_id, bobAccountToken())
    assert u["nb_items"] == 0
    assert u["completed"] is True  # since we received the expecter number of files

    # it should be valid to send back the same file with external metadata
    r = add_files_to_upload_set(
        client,
        upload_set_id,
        datafiles / "e1_without_exif.jpg",
        jwtToken=bobAccountToken(),
        additional_data={
            "override_longitude": 42.42,
            "override_latitude": 4.1,
            "override_capture_time": "2023-07-03T10:12:01.001Z",
        },
    )
    waitForAllJobsDone(current_app, timeout=5)
    u = get_upload_set(client, upload_set_id, bobAccountToken())
    assert u["nb_items"] == 1
    assert u["completed"] is False  # <- it is now not completed since we received files since the completion

    # we need to complete it again
    _complete_upload_set(client, upload_set_id, token=bobAccountToken())
    waitForAllJobsDone(current_app, timeout=5)
    u = get_upload_set(client, upload_set_id, bobAccountToken())
    assert u["nb_items"] == 1
    assert u["completed"] is True


@ALL_IMGS
def test_upload_set_dispatched_deletion(datafiles, app_client_with_auth, bobAccountToken):
    """
    Test that an upload set can be deleted after it's dispatched.
    All the pictures, files and collections should be deleted.
    """
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=8)

    for p in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "e1.jpg", "e2.jpg", "e3.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    # 8 files should have been received
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 8

    waitForUploadSetStateReady(client, upload_set_id)
    # if we query the upload set, it is now marked as completed/dispatched
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["dispatched"] is True

    associated_cols = upload_set_r["associated_collections"]
    # 2 collections should have been created
    assert len(associated_cols) == 2

    # we delete the upload set
    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # we should not find any collection too
    for c in associated_cols:
        r = client.get(f"/api/collections/{str(c['id'])}")
        assert r.status_code == 404

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # but in database the collections should be marked as deleted
    db_cols = db.fetchall(current_app, "SELECT status FROM sequences")
    assert db_cols == [("deleted",), ("deleted",)]

    # there should not be any pictures associated to this uploadset
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_pics) == 0

    # nor any files
    db_files = db.fetchall(current_app, "SELECT * FROM files WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_files) == 0


def test_unknown_upload_set_deletion(app_client_with_auth, bobAccountToken):
    # we delete the upload set
    response = app_client_with_auth.delete(
        "/api/upload_sets/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 404, response.text
    assert response.json == {
        "message": "UploadSet 00000000-0000-0000-0000-000000000000 does not exist",
        "status_code": 404,
    }


@ALL_IMGS
def test_upload_set_not_dispatched_deletion(datafiles, app_client_with_auth, bobAccountToken):
    """Test that an upload set can be deleted even if it is not dispatched"""
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    for p in ["1.jpg", "2.jpg", "3.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    # 3 files should have been received and the upload set is not completed/dispatched
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 3

    # wait for pictures to be prepared
    s = waitForUploadSetState(app_client_with_auth, upload_set_id, wanted_state=lambda x: x.json["items_status"]["not_processed"] == 0)
    assert s["dispatched"] is False
    assert s["completed"] is False
    assert s["ready"] is False

    upload_set = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert len(upload_set["associated_collections"]) == 0

    # we delete the upload set
    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # there should not be any pictures associated to this uploadset
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_pics) == 0

    # nor any files
    db_files = db.fetchall(current_app, "SELECT * FROM files WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_files) == 0


@ALL_IMGS
def test_upload_set_forbidden_deletion(datafiles, app_client_with_auth, bobAccountToken, defaultAccountToken):
    """Only the owner of an upload set can delete it"""
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=defaultAccountToken())
    r = client.delete(
        f"/api/upload_sets/{upload_set_id}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )

    assert r.status_code == 403
    assert r.json == {"message": "You're not authorized to delete this upload set", "status_code": 403}

    r = client.delete(f"/api/upload_sets/{upload_set_id}")
    assert r.status_code == 401
    assert r.json == {"message": "Authentication is mandatory"}


def test_upload_set_empty_deletion(datafiles, app_client_with_auth, bobAccountToken):
    """Test that an empty upload set can be deleted"""
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken())

    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404


@ALL_IMGS
def test_upload_set_deleted_after_all_its_collection_deletion(datafiles, app_client_with_auth, bobAccountToken, bobAccountID):
    """
    Test that an upload set is deleted if all of its collections are deleted.
    """
    client = app_client_with_auth

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=8)

    for p in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "e1.jpg", "e2.jpg", "e3.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    # 8 files should have been received
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 8

    waitForUploadSetStateReady(client, upload_set_id)
    # if we query the upload set, it is now marked as completed/dispatched
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["dispatched"] is True

    created_at = upload_set_r["created_at"]
    initial_associated_cols = upload_set_r.pop("associated_collections")
    # sort the associated collections by their extent to ease comparison
    initial_associated_cols.sort(key=lambda x: x["extent"]["temporal"]["interval"][0])
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "completed": True,
        "dispatched": True,
        "estimated_nb_files": 8,
        "id": upload_set_id,
        "nb_items": 8,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 8, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    assert initial_associated_cols == [
        {
            "id": str(initial_associated_cols[0]["id"]),
            "extent": {
                "temporal": {
                    "interval": [
                        [
                            "2021-07-29T09:16:54Z",
                            "2021-07-29T09:17:02Z",
                        ],
                    ],
                },
            },
            "nb_items": 5,
            "ready": True,
            "title": "some title-1",
            "items_status": {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0},
            "links": [
                {
                    "rel": "self",
                    "href": f"http://localhost:5000/api/collections/{str(initial_associated_cols[0]['id'])}",
                    "type": "application/json",
                }
            ],
        },
        {
            "extent": {
                "temporal": {
                    "interval": [
                        [
                            "2022-10-19T07:56:34Z",
                            "2022-10-19T07:56:38Z",
                        ],
                    ],
                },
            },
            "id": str(initial_associated_cols[1]["id"]),
            "items_status": {
                "broken": 0,
                "not_processed": 0,
                "prepared": 3,
                "preparing": 0,
            },
            "links": [
                {
                    "href": f"http://localhost:5000/api/collections/{str(initial_associated_cols[1]['id'])}",
                    "rel": "self",
                    "type": "application/json",
                },
            ],
            "nb_items": 3,
            "ready": True,
            "title": "some title-2",
        },
    ]

    # we delete one collection
    r = client.delete(f"/api/collections/{str(initial_associated_cols[0]['id'])}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 204, r.text

    # The upload set should be fine, with only the second collection remaining
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "associated_collections": [
            {
                "extent": {
                    "temporal": {
                        "interval": [
                            [
                                "2022-10-19T07:56:34Z",
                                "2022-10-19T07:56:38Z",
                            ],
                        ],
                    },
                },
                "id": str(initial_associated_cols[1]["id"]),
                "items_status": {
                    "broken": 0,
                    "not_processed": 0,
                    "prepared": 3,
                    "preparing": 0,
                },
                "links": [
                    {
                        "href": f"http://localhost:5000/api/collections/{str(initial_associated_cols[1]['id'])}",
                        "rel": "self",
                        "type": "application/json",
                    },
                ],
                "nb_items": 3,
                "ready": True,
                "title": "some title-2",
            },
        ],
        "completed": True,
        "dispatched": True,
        "estimated_nb_files": 8,
        "id": upload_set_id,
        "nb_items": 3,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 3, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # now if the other collection is deleted, the upload set should be deleted too
    r = client.delete(f"/api/collections/{str(initial_associated_cols[1]['id'])}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 204, r.text

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # we should not find any collection too
    for c in initial_associated_cols:
        r = client.get(f"/api/collections/{str(c['id'])}")
        assert r.status_code == 404


@ALL_IMGS
def test_upload_set_deleted_after_all_its_pictures_deletion(
    dburl, tmp_path, datafiles, app_client_with_split_workers, bobAccountToken, bobAccountID
):
    """
    Test that an upload set is deleted if all of its pictures are deleted.
    """
    client = app_client_with_split_workers

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=5)

    pics_id = {}
    for p in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"]:
        r = add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())
        pics_id[p] = r["picture_id"]

    # 8 files should have been received
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 5

    background_worker(dburl, tmp_path)
    waitForUploadSetStateReady(client, upload_set_id)
    # if we query the upload set, it is now marked as completed/dispatched
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["dispatched"] is True

    created_at = upload_set_r["created_at"]
    initial_associated_cols = upload_set_r.pop("associated_collections")
    # sort the associated collections by their extent to ease comparison
    initial_associated_cols.sort(key=lambda x: x["extent"]["temporal"]["interval"][0])
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "completed": True,
        "dispatched": True,
        "estimated_nb_files": 5,
        "id": upload_set_id,
        "nb_items": 5,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }
    assert initial_associated_cols == [
        {
            "id": str(initial_associated_cols[0]["id"]),
            "extent": {
                "temporal": {
                    "interval": [
                        [
                            "2021-07-29T09:16:54Z",
                            "2021-07-29T09:17:02Z",
                        ],
                    ],
                },
            },
            "nb_items": 5,
            "ready": True,
            "title": "some title",
            "items_status": {"broken": 0, "not_processed": 0, "prepared": 5, "preparing": 0},
            "links": [
                {
                    "rel": "self",
                    "href": f"http://localhost:5000/api/collections/{str(initial_associated_cols[0]['id'])}",
                    "type": "application/json",
                }
            ],
        },
    ]

    # we delete 4 pictures and keep 1
    for p in {"1.jpg", "2.jpg", "3.jpg", "4.jpg"}:
        pic_id = pics_id[p]
        r = client.delete(
            f"/api/collections/{str(initial_associated_cols[0]['id'])}/items/{pic_id}",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert r.status_code == 204, r.text

    background_worker(dburl, tmp_path)
    # The upload set should be fine
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r == {
        "account_id": str(bobAccountID),
        "created_at": created_at,
        "ready": True,
        "associated_collections": [
            {
                "extent": {
                    "temporal": {
                        "interval": [
                            [
                                "2021-07-29T09:17:02Z",
                                "2021-07-29T09:17:02Z",
                            ],
                        ],
                    },
                },
                "id": str(initial_associated_cols[0]["id"]),
                "items_status": {
                    "broken": 0,
                    "not_processed": 0,
                    "prepared": 1,
                    "preparing": 0,
                },
                "links": [
                    {
                        "href": f"http://localhost:5000/api/collections/{str(initial_associated_cols[0]['id'])}",
                        "rel": "self",
                        "type": "application/json",
                    },
                ],
                "nb_items": 1,
                "ready": True,
                "title": "some title",
            },
        ],
        "completed": True,
        "dispatched": True,
        "estimated_nb_files": 5,
        "id": upload_set_id,
        "nb_items": 1,
        "semantics": [],
        "sort_method": "time-asc",
        "title": "some title",
        "items_status": {"broken": 0, "not_processed": 0, "prepared": 1, "preparing": 0, "rejected": 0},
        "links": [{"href": f"http://localhost:5000/api/upload_sets/{upload_set_id}", "rel": "self", "type": "application/json"}],
    }

    # now if the other picture is deleted, the upload set should be deleted too
    r = client.delete(
        f"/api/collections/{str(initial_associated_cols[0]['id'])}/items/{pics_id['5.jpg']}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 204, r.text

    background_worker(dburl, tmp_path)

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # we should find the collection though, for the moment deleting all pictures of a collection does not delete the collection.
    # it can change in the future
    for c in initial_associated_cols:
        r = client.get(f"/api/collections/{str(c['id'])}")
        assert r.status_code == 200

    # # and after a while we can check that nothing is left in the database
    waitForAllJobsDone(current_app, timeout=3)

    assert db.fetchone(current_app, "SELECT * FROM upload_sets WHERE id = %s", [upload_set_id]) is None


@ALL_IMGS
def test_upload_set_being_dispatched_deletion(datafiles, app_client_with_split_workers, bobAccountToken, dburl, tmp_path):
    """
    Test that an upload set can be deleted even if it's currently being dispatched.
    """
    client = app_client_with_split_workers

    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=8)

    for p in ["1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg", "e1.jpg", "e2.jpg", "e3.jpg"]:
        add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())

    # 8 files should have been received
    f = _get_upload_set_files(client, upload_set_id, token=bobAccountToken())
    assert len(f["files"]) == 8

    # Nothing should be dispatched since we did not start the background worker
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["associated_collections"] == []
    assert upload_set_r["dispatched"] is False
    assert upload_set_r["ready"] is False
    assert upload_set_r["items_status"] == {"broken": 0, "not_processed": 8, "preparing": 0, "prepared": 0, "rejected": 0}

    # starts background workers, and right away delete the uploadset
    background_worker(dburl, tmp_path)

    # we delete the upload set
    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # starts background workers again in case the previous one were stopped
    background_worker(dburl, tmp_path)

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # there should not be any pictures associated to this uploadset
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_pics) == 0

    # nor any files
    db_files = db.fetchall(current_app, "SELECT * FROM files WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_files) == 0

    assert db.fetchone(current_app, "SELECT * FROM upload_sets WHERE id = %s", [upload_set_id]) is None


@SEQ_IMGS
def test_upload_set_being_deletion_while_pictures_are_deleted(
    app_client_with_split_workers, datafiles, dburl, tmp_path, monkeypatch, bobAccountToken
):
    """
    Test that the upload set deletion is postponed if its pictures are being deleted.
    """
    from geovisio.workers import runner_pictures

    def new_delete_picture(dbPic):
        """Mock function that takes more time to delete the 2nd picture, so it should still be deleting the picture when the upload set is being deleted"""
        import time

        if dbPic.id == UUID(pic_ids["2.jpg"]):
            time.sleep(2)

    monkeypatch.setattr(runner_pictures, "_delete_picture", new_delete_picture)

    client = app_client_with_split_workers
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=2)

    pic_ids = {}
    for p in ["1.jpg", "2.jpg"]:
        r = add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())
        pic_ids[p] = r["picture_id"]

    # starts background workers o process all pictures
    background_worker(dburl, tmp_path)

    waitForAllJobsDone(current_app, timeout=3)
    # all is ready
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert len(upload_set_r["associated_collections"]) > 0
    upload_set_r["associated_collections"][0]["id"]
    assert upload_set_r["dispatched"] is True
    assert upload_set_r["ready"] is True
    assert upload_set_r["items_status"] == {"broken": 0, "not_processed": 0, "preparing": 0, "prepared": 2, "rejected": 0}

    # we delete the upload set
    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # starts background workers again in case the previous one were stopped
    t1 = background_worker(dburl, tmp_path, wait=False)
    t2 = background_worker(dburl, tmp_path, wait=False)
    t1.join()
    t2.join()

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # there should not be any pictures associated to this uploadset
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_pics) == 0

    # nor any files
    db_files = db.fetchall(current_app, "SELECT * FROM files WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_files) == 0

    assert db.fetchone(current_app, "SELECT * FROM upload_sets WHERE id = %s", [upload_set_id]) is None


@SEQ_IMGS
def test_upload_set_being_deletion_while_pictures_are_not_prepared(
    app_client_with_split_workers, datafiles, dburl, tmp_path, monkeypatch, bobAccountToken
):
    """
    Test that the upload set deletion is correclty done, even if the pictures are preparing
    """
    from geovisio.workers import runner_pictures

    def new_delete_picture(dbPic):
        """Mock function that takes more time to delete the 2nd picture, so it should still be deleting the picture when the upload set is being deleted"""
        import time

        if dbPic.id == UUID(pic_ids["2.jpg"]):
            time.sleep(2)

    monkeypatch.setattr(runner_pictures, "_delete_picture", new_delete_picture)

    client = app_client_with_split_workers
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=2)

    pic_ids = {}
    for p in ["1.jpg", "2.jpg"]:
        r = add_files_to_upload_set(client, upload_set_id, datafiles / p, jwtToken=bobAccountToken())
        pic_ids[p] = r["picture_id"]

    # the pictures should be waiting for preparation
    upload_set_r = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert upload_set_r["completed"] is True
    assert upload_set_r["associated_collections"] == []
    assert upload_set_r["dispatched"] is False
    assert upload_set_r["ready"] is False
    assert upload_set_r["items_status"] == {"broken": 0, "not_processed": 2, "preparing": 0, "prepared": 0, "rejected": 0}

    # we delete the upload set
    _delete_upload_set(client, upload_set_id, token=bobAccountToken())

    # it should be impossible to find again the uploadset
    r = get_upload_set(client, upload_set_id, token=bobAccountToken(), raw_response=True)
    assert r.status_code == 404

    # starts background workers again in case the previous one were stopped
    t1 = background_worker(dburl, tmp_path, wait=False)
    t2 = background_worker(dburl, tmp_path, wait=False)
    t1.join()
    t2.join()

    # and after a while, all associated pictures/files should be deleted
    waitForAllJobsDone(current_app, timeout=3)

    # there should not be any pictures associated to this uploadset
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_pics) == 0

    # nor any files
    db_files = db.fetchall(current_app, "SELECT * FROM files WHERE upload_set_id = %s", [upload_set_id])
    assert len(db_files) == 0

    assert db.fetchone(current_app, "SELECT * FROM upload_sets WHERE id = %s", [upload_set_id]) is None


@SEQ_IMGS
def test_add_several_files_with_same_names(datafiles, app_client_with_auth, bobAccountToken):
    """
    Adding files with the same name (but in different directories) should not be possible
    """
    sub_dir = datafiles / "pouet"
    sub_dir.mkdir()
    os.rename(datafiles / "1.jpg", sub_dir / "1.jpg")
    os.rename(datafiles / "2.jpg", datafiles / "1.jpg")
    u1 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=2)

    f = add_files_to_upload_set(app_client_with_auth, u1, datafiles / "1.jpg", jwtToken=bobAccountToken())
    r = add_files_to_upload_set(app_client_with_auth, u1, sub_dir / "1.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 409
    assert r.json == {
        "existing_item": {
            "id": f["picture_id"],
        },
        "message": "A different picture with the same name has already been added to this uploadset",
        "status_code": 409,
    }

    # the uploadset should not be completed as we expected 2 files
    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is False

    # we after a manual completion, all should be ok
    _complete_upload_set(app_client_with_auth, u1, token=bobAccountToken())

    waitForAllJobsDone(current_app)
    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is True
    assert us["dispatched"] is True


@SEQ_IMGS
def test_add_several_files_with_same_names_same_md5(datafiles, app_client_with_auth, bobAccountToken):
    """
    Adding files with the same name and same md5 should not be possible
    """
    import shutil

    sub_dir = datafiles / "pouet"
    sub_dir.mkdir()
    shutil.copy(datafiles / "1.jpg", sub_dir / "1.jpg")
    u1 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=2)

    f = add_files_to_upload_set(app_client_with_auth, u1, datafiles / "1.jpg", jwtToken=bobAccountToken())
    r = add_files_to_upload_set(app_client_with_auth, u1, sub_dir / "1.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert r.status_code == 409
    assert r.json == {
        "existing_item": {
            "id": f["picture_id"],
        },
        "message": "The item has already been added to this upload set",
        "status_code": 409,
    }
    _complete_upload_set(app_client_with_auth, u1, token=bobAccountToken())

    waitForAllJobsDone(current_app)

    upload_set_files_r = app_client_with_auth.get(f"/api/upload_sets/{u1}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    assert len(upload_set_files_r.json["files"]) == 1  # the duplicate is not tracked
    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [u1])
    assert len(db_pics) == 1

    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is True
    assert us["dispatched"] is True


@pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "e1_without_exif.jpg"))
def test_add_same_file_twice_failure_first(datafiles, app_client_with_auth, bobAccountToken):
    """If we try adding an incorrect picture, we should have a rejection
    But it's possible to send again the file, and if it's not correct, we should accept it
    """
    u1 = create_upload_set(app_client_with_auth, jwtToken=bobAccountToken(), estimated_nb_files=1)

    f = add_files_to_upload_set(app_client_with_auth, u1, datafiles / "e1_without_exif.jpg", jwtToken=bobAccountToken(), raw_response=True)
    assert f.status_code == 400, f.text
    assert f.json == {
        "details": {
            "error": """The picture is missing mandatory metadata:
\t- No GPS coordinates or broken coordinates in picture EXIF tags
\t- No valid date in picture EXIF tags""",
            "missing_fields": [
                "datetime",
                "location",
            ],
        },
        "message": "Impossible to parse picture metadata",
        "status_code": 400,
    }

    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is True  # completed, as we expected 1 file and received one (even if it was invalid)

    # should be valid to send the same file with external metadata, making it a valid picture
    r = add_files_to_upload_set(
        app_client_with_auth,
        u1,
        datafiles / "e1_without_exif.jpg",
        jwtToken=bobAccountToken(),
        raw_response=True,
        additional_data={
            "override_longitude": 42.42,
            "override_latitude": 4.21,
            "override_capture_time": "2023-07-03T10:12:01.001Z",
        },
    )

    # uploadset is incomplete as we added more file to a complete uploadset, manual completion is now mandatory
    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is False

    waitForAllJobsDone(current_app)
    _complete_upload_set(app_client_with_auth, u1, token=bobAccountToken())
    waitForAllJobsDone(current_app)
    us = get_upload_set(app_client_with_auth, u1)
    assert us["completed"] is True
    assert us["dispatched"] is True

    upload_set_files_r = app_client_with_auth.get(f"/api/upload_sets/{u1}/files", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert upload_set_files_r.status_code == 200, upload_set_files_r.text
    assert len(upload_set_files_r.json["files"]) == 1

    db_pics = db.fetchall(current_app, "SELECT id FROM pictures WHERE upload_set_id = %s", [u1])
    assert len(db_pics) == 1


@pytest.mark.parametrize(
    ("params"),
    [
        ({"no_deduplication": True, "duplicate_distance": 1}),
        ({"no_deduplication": True, "duplicate_rotation": 10}),
        ({"no_split": True, "split_distance": 1}),
        ({"no_split": True, "split_time": 10}),
    ],
)
def test_incompatible_upload_set_parameters(app_client_with_auth, bobAccountToken, params):
    response = app_client_with_auth.post(
        "/api/upload_sets", json={"title": "pouet"} | params, headers={"Authorization": f"Bearer {bobAccountToken()}"}
    )
    assert response.status_code == 400


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "1.jpg"),
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
)
def test_post_upload_set_with_semantics(app_client_with_auth, datafiles, bobAccountToken, bobAccountID):
    us_base_semantic = [{"key": "some_key", "value": "some_value"}, {"key": "transport_mode", "value": "bike"}]
    client = app_client_with_auth
    response = client.post(
        "/api/upload_sets",
        json={"title": "some title", "semantics": us_base_semantic},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    us_id = response.json["id"]

    # we should be able to get the semantic on the upload set
    u = get_upload_set(app_client_with_auth, us_id, token=bobAccountToken())
    assert u["semantics"] == us_base_semantic

    # we add 2 pictures to get 2 associated collections, and the upload_set tags should be added to all associated collections
    r = add_files_to_upload_set(client, us_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    r = add_files_to_upload_set(client, us_id, datafiles / "e1.jpg", jwtToken=bobAccountToken())

    _complete_upload_set(client, us_id, token=bobAccountToken())

    # we add a separate upload_set to verify that the second one is not found in the search by tags
    us2 = create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)
    r = add_files_to_upload_set(client, us2, datafiles / "e2.jpg", jwtToken=bobAccountToken())

    # at the end, the 2 upload set will be completed, and the pictures prepared, and dispatched to some collection
    s = waitForUploadSetStateReady(client, us_id)
    assert len(s["associated_collections"]) == 2

    for c in s["associated_collections"]:
        col = client.get(f"/api/collections/{c['id']}")
        assert col.status_code == 200, col.text

        assert col.json["semantics"] == us_base_semantic

    # if we add semantic on a collection, we'll get all the semantic tags
    us2 = s["associated_collections"][0]["id"]
    r = client.patch(
        f"/api/collections/{us2}",
        json={
            "semantics": [
                {"key": "some_collection_key", "value": "some_collection_value", "action": "add"},
                {"key": "some_key", "value": "some_value", "action": "delete"},  # we can also remove tags added on the upload_set
            ]
        },
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200

    assert r.json["semantics"] == [
        {"key": "some_collection_key", "value": "some_collection_value"},
        {"key": "transport_mode", "value": "bike"},
    ]

    # we can patch those semantic tags on the upload set, even after dispatch
    r = client.patch(
        f"/api/upload_sets/{us_id}",
        json={
            "semantics": [
                {"key": "transport_mode", "value": "bike", "action": "delete"},
                {"key": "camera_support", "value": "backpack", "action": "add"},
            ]
        },
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    # the upload_set semantics should be updated
    assert r.json["semantics"] == [
        {"key": "camera_support", "value": "backpack"},
        {"key": "some_key", "value": "some_value"},
    ]

    # and it should be propagated to all the associated collections
    r = client.get(f"/api/collections/{us2}")
    assert r.status_code == 200
    assert r.json["semantics"] == [
        {"key": "camera_support", "value": "backpack"},
        {"key": "some_collection_key", "value": "some_collection_value"},
    ]

    # the second collection still has the `some_key=some_value` (it has been removed only on the other collection)
    r = client.get(f"/api/collections/{s['associated_collections'][1]['id']}")
    assert r.status_code == 200
    assert r.json["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "some_key", "value": "some_value"}]

    # we'll also see those tags when querying the list of collections
    r = client.get("/api/collections")
    assert r.status_code == 200, r.text
    assert len(r.json["collections"]) == 3
    col_1 = next(c for c in r.json["collections"] if c["id"] == us2)
    assert col_1["semantics"] == [
        {"key": "camera_support", "value": "backpack"},
        {"key": "some_collection_key", "value": "some_collection_value"},
    ]
    col_2 = next(c for c in r.json["collections"] if c["id"] == s["associated_collections"][1]["id"])
    assert col_2["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "some_key", "value": "some_value"}]

    # and we can search for those tags
    r = client.get("/api/search?filter=\"semantics.camera_support\"='backpack'")
    assert r.status_code == 200, r.text
    assert len(r.json["features"]) == 2
    assert {f["properties"]["original_file:name"] for f in r.json["features"]} == {"1.jpg", "e1.jpg"}


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "1.jpg"),
)
def test_patch_upload_set_with_semantics_other_user(
    app_client_with_auth, datafiles, bobAccountToken, bobAccountID, defaultAccountToken, defaultAccountID
):
    """it's possible for another user to add semantic tags to the upload set, but it's not tracked in an history table, only in the semantic table
    Note: its not yet possible change the semantic of an upload set after it has been dispatched
    """
    client = app_client_with_auth
    response = client.post(
        "/api/upload_sets",
        json={"title": "some title"},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    us_id = response.json["id"]

    r = add_files_to_upload_set(client, us_id, datafiles / "1.jpg", jwtToken=bobAccountToken())

    r = client.patch(
        f"/api/upload_sets/{us_id}",
        json={"semantics": [{"key": "transport_mode", "value": "boat"}, {"key": "camera_support", "value": "backpack"}]},
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert r.status_code == 200
    assert r.json["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "transport_mode", "value": "boat"}]

    # and bob could also add some
    r = client.patch(
        f"/api/upload_sets/{us_id}",
        json={
            "semantics": [
                {"key": "camera_support", "value": "backpack", "action": "delete"},
                {"key": "camera_support", "value": "pole"},
                {"key": "hashtag", "value": "GreatTimeToTakePictures"},
            ]
        },
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert r.status_code == 200, r.text
    assert r.json["semantics"] == [
        {"key": "camera_support", "value": "pole"},
        {"key": "hashtag", "value": "GreatTimeToTakePictures"},
        {"key": "transport_mode", "value": "boat"},
    ]

    db_tags = db.fetchall(
        current_app, "SELECT key, value, account_id FROM upload_sets_semantics WHERE upload_set_id = %s ORDER BY key, value", [us_id]
    )
    assert db_tags == [
        ("camera_support", "pole", bobAccountID),
        ("hashtag", "GreatTimeToTakePictures", bobAccountID),
        ("transport_mode", "boat", defaultAccountID),
    ]


@pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "1.jpg"),
    os.path.join(FIXTURE_DIR, "e1.jpg"),
)
def test_patch_upload_set_already_dispatched(app_client_with_auth, datafiles, bobAccountToken, bobAccountID, defaultAccountToken):
    """If we add semantic on an already dispatched upload set, we propagate the update to all the associated collections"""
    client = app_client_with_auth
    response = client.post(
        "/api/upload_sets",
        json={"title": "some title", "estimated_nb_files": 2},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200, response.text
    us_id = response.json["id"]

    r = add_files_to_upload_set(client, us_id, datafiles / "1.jpg", jwtToken=bobAccountToken())
    r = add_files_to_upload_set(client, us_id, datafiles / "e1.jpg", jwtToken=bobAccountToken())
    s = waitForUploadSetStateReady(client, us_id)

    r = client.patch(
        f"/api/upload_sets/{us_id}",
        json={"semantics": [{"key": "transport_mode", "value": "boat"}, {"key": "camera_support", "value": "backpack"}]},
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert r.status_code == 200
    assert r.json["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "transport_mode", "value": "boat"}]

    assert len(r.json["associated_collections"]) == 2
    for c in r.json["associated_collections"]:
        col = client.get(f"/api/collections/{c['id']}")
        assert col.status_code == 200, col.text
        assert col.json["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "transport_mode", "value": "boat"}]

    tag_history = get_tags_history()
    assert len(tag_history["sequences"]) == 2
    for h in tag_history["sequences"]:
        assert h[1] == "Default account"  # we have tracked that it's the default account that added the tags
        assert h[2] == [
            {"action": "add", "key": "transport_mode", "value": "boat"},
            {"action": "add", "key": "camera_support", "value": "backpack"},
        ]

    # if we dispatch again the upload_set it should not change anything
    assert db.fetchone(current_app, "SELECT COUNT(*) FROM job_history WHERE upload_set_id = %s", [us_id])[0] == 1
    _complete_upload_set(client, us_id, token=bobAccountToken())
    waitForAllJobsDone(current_app)

    assert db.fetchone(current_app, "SELECT COUNT(*) FROM job_history WHERE upload_set_id = %s", [us_id])[0] == 2

    assert len(r.json["associated_collections"]) == 2
    for c in r.json["associated_collections"]:
        col = client.get(f"/api/collections/{c['id']}")
        assert col.status_code == 200, col.text
        assert col.json["semantics"] == [{"key": "camera_support", "value": "backpack"}, {"key": "transport_mode", "value": "boat"}]

    tag_history = get_tags_history()
    assert len(tag_history["sequences"]) == 2
    for h in tag_history["sequences"]:
        assert h[1] == "Default account"  # we have tracked that it's the default account that added the tags
        assert h[2] == [
            {"action": "add", "key": "transport_mode", "value": "boat"},
            {"action": "add", "key": "camera_support", "value": "backpack"},
        ]


@ALL_IMGS
def test_upload_set_relative_heading(app_client_with_auth, dburl, tmp_path, datafiles, bobAccountToken, bobAccountID, defaultAccountToken):
    """We can set a relative heading for the upload set, and it will be applied to all the associated collections"""
    client = app_client_with_auth
    upload_set_id = create_upload_set(client, jwtToken=bobAccountToken(), relative_heading=90)

    for p in datafiles.iterdir():
        if p.suffix == ".jpg":
            add_files_to_upload_set(app_client_with_auth, upload_set_id, datafiles / p.name, jwtToken=bobAccountToken())

    _complete_upload_set(client, upload_set_id, bobAccountToken())
    waitForUploadSetStateReady(client, upload_set_id)

    us = get_upload_set(client, upload_set_id, token=bobAccountToken())
    assert us["relative_heading"] == 90

    col1_headings = [114, 103, 96, 72, 72]
    col2_headings = [7, 2, 2, 0, 0]
    col3_headings = [28, 28]

    def relative_headings(headings, relative):
        return [(h + relative) % 360 for h in headings]

    col_1_id = None
    # 3 associated collections, and in each, all pictures should have a relative heading of 90°
    assert len(us["associated_collections"]) == 3
    for c in us["associated_collections"]:
        items = client.get(f"/api/collections/{c['id']}/items")
        assert items.status_code == 200, items.text
        file_names = set([f["properties"]["original_file:name"] for f in items.json["features"]])
        headings = [f["properties"]["view:azimuth"] for f in items.json["features"]]
        if file_names == {"1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"}:
            col_1_id = c["id"]
            assert headings == col1_headings
        elif file_names == {"e1.jpg", "e2.jpg", "e3.jpg", "e4.jpg", "e5.jpg"}:
            assert headings == col2_headings
        elif file_names == {"b1.jpg", "b2.jpg"}:
            assert headings == col3_headings
        else:
            assert False, f"The collection should not be split like this, file_names = {file_names}"

    # afterward, I can update the relative heading of the uploadset, but I'll need to complete it again for the new relative heading to be applied
    r = client.patch(
        f"/api/upload_sets/{upload_set_id}", json={"relative_heading": -90}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
    )
    assert r.status_code == 200, r.text
    assert r.json["relative_heading"] == -90, r.json

    _complete_upload_set(client, upload_set_id, bobAccountToken())
    background_worker(dburl, tmp_path)
    waitForUploadSetStateReady(client, upload_set_id)
    assert len(us["associated_collections"]) == 3
    for c in us["associated_collections"]:
        items = client.get(f"/api/collections/{c['id']}/items")
        assert items.status_code == 200, items.text
        file_names = set([f["properties"]["original_file:name"] for f in items.json["features"]])
        headings = [f["properties"]["view:azimuth"] for f in items.json["features"]]
        if file_names == {"1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"}:
            assert headings == relative_headings(col1_headings, -180)  # -180 because we go from -90 to 90
        elif file_names == {"e1.jpg", "e2.jpg", "e3.jpg", "e4.jpg", "e5.jpg"}:
            assert headings == relative_headings(col2_headings, -180)
        elif file_names == {"b1.jpg", "b2.jpg"}:
            assert headings == relative_headings(col3_headings, -180)
        else:
            assert False, f"The collection should not be split like this, file_names = {file_names}"

    # and if we update one sequence's relative heading, this sequence should be updated (but not the others)
    r = client.patch(f"/api/collections/{col_1_id}", json={"relative_heading": 0}, headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 200

    for c in us["associated_collections"]:
        items = client.get(f"/api/collections/{c['id']}/items")
        assert items.status_code == 200, items.text
        file_names = set([f["properties"]["original_file:name"] for f in items.json["features"]])
        headings = [f["properties"]["view:azimuth"] for f in items.json["features"]]
        if file_names == {"1.jpg", "2.jpg", "3.jpg", "4.jpg", "5.jpg"}:
            assert headings == relative_headings(col1_headings, -90)
        elif file_names == {"e1.jpg", "e2.jpg", "e3.jpg", "e4.jpg", "e5.jpg"}:
            assert headings == relative_headings(col2_headings, -180)
        elif file_names == {"b1.jpg", "b2.jpg"}:
            assert headings == relative_headings(col3_headings, -180)
        else:
            assert False, f"The collection should not be split like this, file_names = {file_names}"
