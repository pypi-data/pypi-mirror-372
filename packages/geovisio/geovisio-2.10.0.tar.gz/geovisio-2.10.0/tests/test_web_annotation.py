from email import header
from math import exp
from uuid import UUID
from wsgiref import headers
from flask import current_app
import psycopg
from pytest import fixture
import pytest
import geovisio
from geovisio.utils import db
from tests import conftest


@fixture
def create_test_app(dburl, tmp_path):
    with conftest.create_test_app(
        {
            "TESTING": True,
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "DB_URL": dburl,
            "FS_URL": str(tmp_path),
            "FS_TMP_URL": None,
            "FS_PERMANENT_URL": None,
            "FS_DERIVATES_URL": None,
            "SECRET_KEY": "a very secret key",
        }
    ) as app:
        yield app


@conftest.SEQ_IMGS
def test_create_annotation(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken):

    with create_test_app.test_client() as client:
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
        seq, pic = conftest.getFirstPictureIds(dburl)

        initial_updated_at = client.get(f"/api/collections/{seq}/items/{pic}").json["properties"]["updated"]

        # Create an annotation on the picture
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 200
        # updated_at should be updated
        updated_at_after_creation = client.get(f"/api/collections/{seq}/items/{pic}").json["properties"]["updated"]
        assert updated_at_after_creation > initial_updated_at
        a = response.json
        annotation_id = a.pop("id")
        assert response.headers["Location"] == f"http://localhost/api/annotations/{annotation_id}"
        UUID(annotation_id)
        assert a == {
            "picture_id": str(pic),
            "semantics": [{"key": "some_other_tag", "value": "some_other_value"}, {"key": "some_tag", "value": "some_value"}],
            "shape": {  # the shape is always returned as a geojson polygon, even if it was provided as a boundingbox.
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }

        # the annotation tags should also have been added in the history
        assert conftest.get_tags_history() == {
            "pictures": [
                (
                    pic,
                    "bob",
                    [
                        {
                            "action": "add",
                            "key": "some_tag",
                            "value": "some_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                        {
                            "action": "add",
                            "key": "some_other_tag",
                            "value": "some_other_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                    ],
                ),
            ],
        }
        # and we should find this annotation in the picture's reponse
        r = client.get(f"/api/collections/{seq}/items/{pic}")
        assert r.status_code == 200
        assert r.json["properties"]["annotations"] == [
            {
                "id": annotation_id,
                "shape": {
                    "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                    "type": "Polygon",
                },
                "semantics": [{"key": "some_other_tag", "value": "some_other_value"}, {"key": "some_tag", "value": "some_value"}],
            }
        ]
        # we can also get our annotation
        a = client.get(f"/api/collections/{seq}/items/{pic}/annotations/{annotation_id}")
        assert a.status_code == 200
        assert a.json == {
            "id": annotation_id,
            "picture_id": str(pic),
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "some_value"},
            ],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }
        # and we can get it via the shortcut
        sa = client.get(f"/api/annotations/{annotation_id}")
        assert sa.status_code == 200
        assert a.json == sa.json

        # we can patch the annotation (with another user for the fun)
        a = client.patch(
            f"/api/collections/{seq}/items/{pic}/annotations/{annotation_id}",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value", "action": "delete"},
                    {"key": "some_tag", "value": "some_new_value"},
                    {"key": "traffic_sign", "value": "stop"},
                ],
            },
        )
        assert a.status_code == 200, a.text
        assert a.json == {
            "id": annotation_id,
            "picture_id": str(pic),
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "some_new_value"},
                {"key": "traffic_sign", "value": "stop"},
            ],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }
        updated_at_after_patch = client.get(f"/api/collections/{seq}/items/{pic}").json["properties"]["updated"]
        assert updated_at_after_patch > updated_at_after_creation
        # and we have this edit in the history
        assert conftest.get_tags_history() == {
            "pictures": [
                (
                    pic,
                    "bob",
                    [
                        {
                            "action": "add",
                            "key": "some_tag",
                            "value": "some_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                        {
                            "action": "add",
                            "key": "some_other_tag",
                            "value": "some_other_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                    ],
                ),
                (
                    pic,
                    "Default account",
                    [
                        {
                            "action": "delete",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_tag",
                            "value": "some_value",
                        },
                        {
                            "action": "add",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_tag",
                            "value": "some_new_value",
                        },
                        {
                            "action": "add",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "traffic_sign",
                            "value": "stop",
                        },
                    ],
                ),
            ],
        }

        # and if we remove all semantic tags, the annotation is deleted
        a = client.patch(
            f"/api/collections/{seq}/items/{pic}/annotations/{annotation_id}",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "semantics": [
                    {"key": "some_other_tag", "value": "some_other_value", "action": "delete"},
                    {"key": "some_tag", "value": "some_new_value", "action": "delete"},
                    {"key": "traffic_sign", "value": "stop", "action": "delete"},
                ],
            },
        )
        assert a.status_code == 204, a.text
        assert client.get(f"/api/collections/{seq}/items/{pic}").json["properties"]["updated"] > updated_at_after_patch

        # the annotation is not anymore in the database
        assert db.fetchone(current_app, "SELECT * FROM annotations WHERE id = %(id)s", {"id": annotation_id}) is None
        # and it's tracked in the database history
        assert conftest.get_tags_history() == {
            "pictures": [
                (
                    pic,
                    "bob",
                    [
                        {
                            "action": "add",
                            "key": "some_tag",
                            "value": "some_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                        {
                            "action": "add",
                            "key": "some_other_tag",
                            "value": "some_other_value",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                        },
                    ],
                ),
                (
                    pic,
                    "Default account",
                    [
                        {
                            "action": "delete",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_tag",
                            "value": "some_value",
                        },
                        {
                            "action": "add",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_tag",
                            "value": "some_new_value",
                        },
                        {
                            "action": "add",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "traffic_sign",
                            "value": "stop",
                        },
                    ],
                ),
                (
                    pic,
                    "Default account",
                    [
                        {
                            "action": "delete",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_other_tag",
                            "value": "some_other_value",
                        },
                        {
                            "action": "delete",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "some_tag",
                            "value": "some_new_value",
                        },
                        {
                            "action": "delete",
                            "annotation_shape": {
                                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                                "type": "Polygon",
                            },
                            "key": "traffic_sign",
                            "value": "stop",
                        },
                    ],
                ),
            ],
        }
        # and it's ok to add back some annotation on this shape
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_new_tag", "value": "some_new_value"}],
            },
        )
        assert response.status_code == 200
        a = response.json
        annotation_id = a.pop("id")
        UUID(annotation_id)
        assert a == {
            "picture_id": str(pic),
            "semantics": [{"key": "some_new_tag", "value": "some_new_value"}],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }

        # we can also add a now annotation, with the same shape, and the existing one will be used
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "another tag", "value": "nice value"}],
            },
        )
        assert response.status_code == 200
        assert response.json == {
            "picture_id": str(pic),
            "id": annotation_id,
            "semantics": [{"key": "another tag", "value": "nice value"}, {"key": "some_new_tag", "value": "some_new_value"}],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }

        # we can also add a now annotation, with the same shape and removing all previous tags, the same annotation will be used anyway
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [
                    {"key": "some_new_tag", "value": "some_new_value", "action": "delete"},
                    {"key": "another tag", "value": "nice value", "action": "delete"},
                    {"key": "some_tag", "value": "some_new_value"},
                ],
            },
        )
        assert response.status_code == 200
        assert response.json == {
            "picture_id": str(pic),
            "id": annotation_id,
            "semantics": [{"key": "some_tag", "value": "some_new_value"}],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }


@conftest.SEQ_IMGS
def test_create_annotation_with_shortcut(
    dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken
):
    # most annotation APIs should also be aliases to ease some integrations (most to be able to not know the collection ID)
    with create_test_app.test_client() as client:
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
        _seq, pic = conftest.getFirstPictureIds(dburl)
        # Create an annotation on the picture
        response = client.post(
            f"/api/pictures/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 200, response.text
        a = response.json
        annotation_id = a.pop("id")
        UUID(annotation_id)
        # Location is directly the non stac alias
        assert response.headers["Location"] == f"http://localhost/api/annotations/{annotation_id}"
        assert a == {
            "picture_id": str(pic),
            "semantics": [{"key": "some_other_tag", "value": "some_other_value"}, {"key": "some_tag", "value": "some_value"}],
            "shape": {  # the shape is always returned as a geojson polygon, even if it was provided as a boundingbox.
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }

        # and we should find this annotation in the picture's reponse
        r = client.get(f"/api/pictures/{pic}")
        assert r.status_code == 200
        assert r.json["properties"]["annotations"] == [
            {
                "id": annotation_id,
                "shape": {
                    "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                    "type": "Polygon",
                },
                "semantics": [{"key": "some_other_tag", "value": "some_other_value"}, {"key": "some_tag", "value": "some_value"}],
            }
        ]
        # we can also get our annotation
        a = client.get(f"/api/annotations/{annotation_id}")
        assert a.status_code == 200
        assert a.json == {
            "id": annotation_id,
            "picture_id": str(pic),
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "some_value"},
            ],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }

        # we can patch the annotation (with another user for the fun)
        a = client.patch(
            f"/api/annotations/{annotation_id}",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value", "action": "delete"},
                    {"key": "some_tag", "value": "some_new_value"},
                    {"key": "traffic_sign", "value": "stop"},
                ],
            },
        )
        assert a.status_code == 200, a.text
        assert a.json == {
            "id": annotation_id,
            "picture_id": str(pic),
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "some_new_value"},
                {"key": "traffic_sign", "value": "stop"},
            ],
            "shape": {
                "coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]],
                "type": "Polygon",
            },
        }


@conftest.SEQ_IMGS
def test_create_annotation_no_auth(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID):
    """To create an annotation, we need to be authenticated"""
    with create_test_app.test_client() as client:
        response = client.post(
            f"/api/collections/00000000-0000-0000-0000-000000000000/items/00000000-0000-0000-0000-000000000000/annotations",
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 401
        assert response.json == {
            "message": "Authentication is mandatory",
        }


@conftest.SEQ_IMGS
def test_create_annotation_unkown_pic(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID):
    with create_test_app.test_client() as client:
        response = client.post(
            f"/api/collections/00000000-0000-0000-0000-000000000000/items/00000000-0000-0000-0000-000000000000/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 404
        assert response.json == {
            "status_code": 404,
            "message": "Picture 00000000-0000-0000-0000-000000000000 wasn't found in database",
        }


@conftest.SEQ_IMGS
def test_create_annotation_other_account(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountToken):
    """anyone can create an annotation on a picture"""
    with create_test_app.test_client() as client:
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
        seq, pic = conftest.getFirstPictureIds(dburl)

        # Create an annotation on the picture
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}],
            },
        )
        assert response.status_code == 200

        # and we have the account that have created the annotation in the history
        assert conftest.get_tags_history() == {
            "pictures": [
                (
                    pic,
                    "Default account",
                    [
                        {
                            "action": "add",
                            "key": "some_tag",
                            "value": "some_value",
                            "annotation_shape": {"coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]], "type": "Polygon"},
                        },
                    ],
                ),
            ],
        }


@conftest.SEQ_IMGS
def test_create_many_annotations(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken):
    """Test with several semantics on a sequence and picture and several annotations"""

    with create_test_app.test_client() as client:
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
        seq, pic = conftest.getFirstPictureIds(dburl)

        a = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [1, 1, 10, 10],
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert a.status_code == 200
        first_annotation_id = a.json["id"]

        assert (
            client.post(
                f"/api/collections/{seq}/items/{pic}/annotations",
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
                json={
                    "shape": [5, 5, 100, 20],
                    "semantics": [{"key": "traffic_sign", "value": "stop"}, {"key": "traffic_sign:source", "value": "skynet"}],
                },
            ).status_code
            == 200
        )

        assert (
            client.patch(
                f"/api/collections/{seq}/items/{pic}",
                json={
                    "semantics": [
                        {"key": "wikidata", "value": "Q1245"},
                        {"key": "osm:amenity", "value": "pub"},
                        {"key": "osm:amenity", "value": "hotel"},
                        {"key": "people:count", "value": "15"},
                    ]
                },
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            ).status_code
            == 200
        )

        assert (
            client.patch(
                f"/api/collections/{seq}",
                json={
                    "semantics": [
                        {"key": "osm:node_id", "value": "12"},
                        {"key": "panoramax:camera_support", "value": "backpack"},
                        {"key": "exif:lightsource", "value": "daylight"},
                    ]
                },
                headers={"Authorization": f"Bearer {bobAccountToken()}"},
            ).status_code
            == 200
        )

        # we should be able to find the picture/annotation semantic tags on the items, and on the /search endpoint
        # Note: we don't get the sequence tags for the moment, they need to be queried on /collections/:id for the moment
        expected_pic_semantics = [
            {"key": "osm:amenity", "value": "hotel"},
            {"key": "osm:amenity", "value": "pub"},
            {"key": "people:count", "value": "15"},
            {"key": "wikidata", "value": "Q1245"},
        ]
        expected_annotations = [
            {
                "semantics": [
                    {"key": "some_other_tag", "value": "some_other_value"},
                    {"key": "some_tag", "value": "some_value"},
                ],
                "shape": {"coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]], "type": "Polygon"},
            },
            {
                "semantics": [
                    {"key": "traffic_sign", "value": "stop"},
                    {"key": "traffic_sign:source", "value": "skynet"},
                ],
                "shape": {"coordinates": [[[5, 5], [100, 5], [100, 20], [5, 20], [5, 5]]], "type": "Polygon"},
            },
        ]

        get_resp = client.get(f"/api/collections/{seq}/items")
        assert get_resp.status_code == 200

        first_pic = next(p for p in get_resp.json["features"] if p["id"] == str(pic))
        assert first_pic["properties"]["semantics"] == expected_pic_semantics

        assert conftest.cleanup_annotations(first_pic["properties"]["annotations"]) == expected_annotations
        # same when we query only the picture
        get_resp = client.get(f"/api/collections/{seq}/items/{pic}")
        assert get_resp.status_code == 200
        assert get_resp.json["properties"]["semantics"] == expected_pic_semantics
        assert conftest.cleanup_annotations(get_resp.json["properties"]["annotations"]) == expected_annotations

        # or when searching for a picture
        r = client.get(f'/api/search?ids=["{pic}"]')
        assert r.status_code == 200
        assert len(r.json["features"]) == 1
        assert r.json["features"][0]["properties"]["semantics"] == expected_pic_semantics
        assert conftest.cleanup_annotations(r.json["features"][0]["properties"]["annotations"]) == expected_annotations

        # we can then add some more tag to an annotation (and replace one some for the fun)
        a = client.patch(
            f"/api/collections/{seq}/items/{pic}/annotations/{first_annotation_id}",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "semantics": [
                    {"key": "some_tag", "value": "some_value", "action": "delete"},
                    {"key": "some_tag", "value": "some_new_value"},
                    {"key": "traffic_sign", "value": "stop"},
                ],
            },
        )
        assert a.status_code == 200, a.text
        assert a.json == {
            "id": first_annotation_id,
            "picture_id": str(pic),
            "semantics": [
                {"key": "some_other_tag", "value": "some_other_value"},
                {"key": "some_tag", "value": "some_new_value"},
                {"key": "traffic_sign", "value": "stop"},
            ],
            "shape": {"coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]], "type": "Polygon"},
        }
        # same as before, we can find it in the picture
        get_resp = client.get(f"/api/collections/{seq}/items/{pic}")
        assert get_resp.status_code == 200
        assert conftest.cleanup_annotations(get_resp.json["properties"]["annotations"]) == [
            {
                "semantics": [
                    {"key": "some_other_tag", "value": "some_other_value"},
                    {"key": "some_tag", "value": "some_new_value"},
                    {"key": "traffic_sign", "value": "stop"},
                ],
                "shape": {"coordinates": [[[1, 1], [10, 1], [10, 10], [1, 10], [1, 1]]], "type": "Polygon"},
            },
            {
                "semantics": [
                    {"key": "traffic_sign", "value": "stop"},
                    {"key": "traffic_sign:source", "value": "skynet"},
                ],
                "shape": {"coordinates": [[[5, 5], [100, 5], [100, 20], [5, 20], [5, 5]]], "type": "Polygon"},
            },
        ]


@conftest.SEQ_IMGS
def test_update_annotation_no_auth(create_test_app):
    """To update an annotation, we need to be authenticated"""
    with create_test_app.test_client() as client:
        response = client.patch(
            f"/api/collections/00000000-0000-0000-0000-000000000000/items/00000000-0000-0000-0000-000000000000/annotations/00000000-0000-0000-0000-000000000000",
            json={
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 401
        assert response.json == {
            "message": "Authentication is mandatory",
        }


@conftest.SEQ_IMGS
def test_update_unknown_annotation(create_test_app, bobAccountToken):
    """Updating an unknown annotation should return 404"""
    with create_test_app.test_client() as client:
        response = client.patch(
            f"/api/collections/00000000-0000-0000-0000-000000000000/items/00000000-0000-0000-0000-000000000000/annotations/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "semantics": [{"key": "some_tag", "value": "some_value"}, {"key": "some_other_tag", "value": "some_other_value"}],
            },
        )
        assert response.status_code == 404, response.text
        assert response.json == {
            "message": "Annotation 00000000-0000-0000-0000-000000000000 not found",
            "status_code": 404,
        }


@pytest.mark.parametrize(
    ("shape", "error"),
    (
        ([1, 1, 10, 10], None),
        (
            [-1, 1, 10, 10],
            {
                "message": "Annotation shape is outside the range of the picture",
                "details": "Annotation shape's coordinates should be in pixel, between [0, 0] and [5760, 4320]",
                "status_code": 400,
                "value": {
                    "x": -1,
                    "y": 1,
                },
            },
        ),
        (
            [1, 100000, 10, 10],
            {
                "message": "Annotation shape is outside the range of the picture",
                "details": "Annotation shape's coordinates should be in pixel, between [0, 0] and [5760, 4320]",
                "status_code": 400,
                "value": {
                    "x": 1,
                    "y": 100000,
                },
            },
        ),
        (
            "pouet",
            {
                "details": [
                    {
                        "error": "Input should be a valid dictionary or instance of Polygon",
                        "fields": ["shape", "geometry"],
                        "input": "pouet",
                    }
                ],
                "message": "Impossible to create an annotation",
                "status_code": 400,
            },
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [1, 10],
                        [10, 100],
                        [5, 300],
                        [240, 632],
                        [1000, 1000],
                        [1, 10],
                    ]
                ],
            },
            None,
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [
                        [1, 10],
                        [10, 100],
                        [5, 300],
                        [240, 632],
                        [1000, 100000],
                        [1, 10],
                    ]
                ],
            },
            {
                "message": "Annotation shape is outside the range of the picture",
                "details": "Annotation shape's coordinates should be in pixel, between [0, 0] and [5760, 4320]",
                "status_code": 400,
                "value": {
                    "x": 1000,
                    "y": 100000,
                },
            },
        ),
        (
            {"type": "Point", "coordinates": [1, 10]},  # points are not supported yet
            {
                "details": [
                    {"error": "Input should be 'Polygon'", "fields": ["shape", "geometry", "type"], "input": "Point"},
                    {"error": "Input should be a valid list", "fields": ["shape", "geometry", "coordinates", 0], "input": 1},
                    {"error": "Input should be a valid list", "fields": ["shape", "geometry", "coordinates", 1], "input": 10},
                ],
                "message": "Impossible to create an annotation",
                "status_code": 400,
            },
        ),
    ),
)
@conftest.SEQ_IMGS
def test_create_annotation_custom_geom(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, shape, error):
    with create_test_app.test_client() as client:
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
        seq, pic = conftest.getFirstPictureIds(dburl)

        # Create an annotation on the picture
        response = client.post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": shape,
                "semantics": [{"key": "some_tag", "value": "some_value"}],
            },
        )
        if error is None:
            assert response.status_code == 200, response.text
        else:
            assert response.json == error


@conftest.SEQ_IMGS
def test_empty_annotations(dburl, datafiles, create_test_app, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken):
    """If a picture has no annotation the semantics should be empty"""
    with create_test_app.test_client() as client:
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
        seq, pic = conftest.getFirstPictureIds(dburl)

        get_resp = client.get(f"/api/collections/{seq}/items/{pic}")
        assert get_resp.status_code == 200
        print(get_resp.json["properties"])
        assert get_resp.json["properties"]["semantics"] == []
        assert get_resp.json["properties"]["annotations"] == []
