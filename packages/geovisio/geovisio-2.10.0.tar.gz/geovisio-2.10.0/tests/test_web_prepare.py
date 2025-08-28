import os
from uuid import UUID
from flask import current_app
import psycopg
from pytest import fixture
import geovisio
from geovisio.utils import db
from tests import conftest
from psycopg.rows import dict_row
from PIL import Image


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


def mock_blurring_api_twice(requests_mock, datafiles):
    requests_mock.post(
        conftest.MOCK_BLUR_API + "/blur/",
        [
            {"body": open(datafiles / "1_blurred.jpg", "rb")},
            # the second time the blur is returned, it will give a different response (to mock an update of the blurring model)
            {"body": open(datafiles / "2.jpg", "rb")},
        ],
    )


def _get_jobs():
    jobs = db.fetchall(
        current_app,
        "SELECT job_task, picture_id, sequence_id, upload_set_id, error, args FROM job_history ORDER BY started_at",
        row_factory=dict_row,
    )
    return [{k: v for k, v in j.items() if v is not None} for j in jobs]


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_prepare_item(requests_mock, datafiles, create_test_app, dburl):
    app = create_test_app
    mock_blurring_api_twice(requests_mock, datafiles)

    with create_test_app.test_client() as client:
        ids = conftest.upload_files(
            client,
            [datafiles / "1.jpg"],
            wait=True,
        )
        us = conftest.get_upload_set(client, ids.id)
        seq_id = UUID(us["associated_collections"][0]["id"])

        # Check that picture has been correctly processed
        laterResponse = client.get(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}")
        assert laterResponse.status_code == 200

        # Check if picture sent to blur API is same as one from FS
        reqSize = int(requests_mock.request_history[0].headers["Content-Length"])
        picSize = os.path.getsize(datafiles / "1.jpg")
        assert picSize * 0.99 <= reqSize <= picSize * 1.01

        # Check file is available on filesystem
        hd_file = f"{datafiles}/permanent{geovisio.utils.pictures.getHDPicturePath(ids.pics['1.jpg'])}"
        assert os.path.isfile(hd_file)
        first_permanent_file_update_time = os.path.getmtime(hd_file)
        # derivates should also be available
        sd_file = f"{datafiles}/derivates{geovisio.utils.pictures.getPictureFolderPath(ids.pics['1.jpg'])}/sd.jpg"
        assert os.path.isfile(sd_file)

        initial_image = Image.open(hd_file)
        conftest.arePicturesSimilar(initial_image, Image.open(datafiles / "1_blurred.jpg"))

        first_sd_file_update_time = os.path.getmtime(sd_file)

        assert requests_mock.call_count == 1
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
        ]

        response = client.post(
            f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare",
        )
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(app)

        assert requests_mock.call_count == 2

        assert os.path.getmtime(hd_file) > first_permanent_file_update_time
        assert os.path.getmtime(sd_file) > first_sd_file_update_time
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
        ]
        conftest.arePicturesSimilar(Image.open(hd_file), Image.open(f"{datafiles}/2.jpg"))

        # we can also prepare without blurring
        response = client.post(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare", json={"skip_blurring": "true"})
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(app)

        assert requests_mock.call_count == 2  # no additional blurring
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"], "args": {"skip_blurring": True}},
        ]

        # calling with an invalid parameter should fail
        response = client.post(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare", json={"skip_blurring": "pouet"})
        assert response.status_code == 400
        assert response.json == {
            "details": [
                {
                    "error": "Input should be a valid boolean, unable to interpret input",
                    "fields": [
                        "skip_blurring",
                    ],
                    "input": "pouet",
                },
            ],
            "message": "Impossible to parse parameters",
            "status_code": 400,
        }


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_prepare_hidden_item(requests_mock, datafiles, create_test_app, bobAccountToken):
    app = create_test_app
    mock_blurring_api_twice(requests_mock, datafiles)

    headers = {"Authorization": f"Bearer {bobAccountToken()}"}
    with create_test_app.test_client() as client:

        ids = conftest.upload_files(
            client,
            [datafiles / "1.jpg"],
            jwtToken=bobAccountToken(),
            wait=True,
        )
        us = conftest.get_upload_set(client, ids.id, token=bobAccountToken())
        seq_id = UUID(us["associated_collections"][0]["id"])

        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
        ]

        # we make the picture private
        response = client.patch(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}", data={"visible": "false"}, headers=headers)
        assert response.status_code == 200
        pic_detail = client.get(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}", headers=headers)
        assert pic_detail.status_code == 200
        assert pic_detail.json["properties"]["geovisio:status"] == "hidden"

        # should be impossible to prepare the picture without auth
        response = client.post(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare")
        assert response.status_code == 404
        response = client.post(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare", headers=headers)
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(app)

        assert requests_mock.call_count == 2
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
        ]
        hd_file = f"{datafiles}/permanent{geovisio.utils.pictures.getHDPicturePath(ids.pics['1.jpg'])}"
        conftest.arePicturesSimilar(Image.open(hd_file), Image.open(f"{datafiles}/2.jpg"))
        # the picture should still be hidden
        pic_detail = client.get(f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}", headers=headers)
        assert pic_detail.status_code == 200
        assert pic_detail.json["properties"]["geovisio:status"] == "hidden"


def test_prepare_not_found_item(create_test_app):
    with create_test_app.test_client() as client:
        seq_location = conftest.createSequence(client, "a_sequence")
        seq_id = UUID(seq_location.split("/")[-1])
        unknow_uuid = "00000000-0000-0000-0000-000000000000"
        response = client.post(f"/api/collections/{seq_id}/items/{unknow_uuid}/prepare")
        assert response.status_code == 404
        assert response.json == {
            "message": "Picture 00000000-0000-0000-0000-000000000000 wasn't found in database",
            "status_code": 404,
        }


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_prepare_already_blurred_picture(requests_mock, datafiles, create_test_app, bobAccountToken):
    app = create_test_app
    mock_blurring_api_twice(requests_mock, datafiles)

    with create_test_app.test_client() as client:

        ids = conftest.upload_files(
            client,
            [conftest.PicToUpload(path=datafiles / "1.jpg", additional_data={"isBlurred": True})],
            jwtToken=bobAccountToken(),
            wait=True,
        )
        us = conftest.get_upload_set(client, ids.id, token=bobAccountToken())
        seq_id = UUID(us["associated_collections"][0]["id"])

        # Check file is available on filesystem
        hd_file = f"{datafiles}/permanent{geovisio.utils.pictures.getHDPicturePath(ids.pics['1.jpg'])}"
        assert os.path.isfile(hd_file)
        first_permanent_file_update_time = os.path.getmtime(hd_file)
        # derivates should also be available
        sd_file = f"{datafiles}/derivates{geovisio.utils.pictures.getPictureFolderPath(ids.pics['1.jpg'])}/sd.jpg"
        assert os.path.isfile(sd_file)

        initial_image = Image.open(hd_file)
        conftest.arePicturesSimilar(initial_image, Image.open(f"{datafiles}/1.jpg"))  # picture should not have been blurred

        first_sd_file_update_time = os.path.getmtime(sd_file)

        assert requests_mock.call_count == 0  # the picture should not have been blurred
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"], "args": {"skip_blurring": True}},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
        ]

        response = client.post(
            f"/api/collections/{seq_id}/items/{ids.pics['1.jpg']}/prepare",
        )
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(app)

        assert requests_mock.call_count == 1  # now blurring should have been done

        assert os.path.getmtime(hd_file) > first_permanent_file_update_time
        assert os.path.getmtime(sd_file) > first_sd_file_update_time
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"], "args": {"skip_blurring": True}},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},  # second call should not skip blurring
        ]
        conftest.arePicturesSimilar(Image.open(hd_file), Image.open(datafiles / "1_blurred.jpg"))


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_prepare_collections(requests_mock, datafiles, create_test_app, bobAccountToken):
    requests_mock.post(
        conftest.MOCK_BLUR_API + "/blur/",
        [
            {"body": open(datafiles / "1_blurred.jpg", "rb")},
            {"body": open(datafiles / "2.jpg", "rb")},
            {"body": open(datafiles / "3.jpg", "rb")},
            {"body": open(datafiles / "4.jpg", "rb")},
        ],
    )

    with create_test_app.test_client() as client:
        ids = conftest.upload_files(
            client,
            [datafiles / "1.jpg", conftest.PicToUpload(path=datafiles / "2.jpg", additional_data={"isBlurred": True})],
            jwtToken=bobAccountToken(),
            wait=True,
        )
        us = conftest.get_upload_set(client, ids.id, token=bobAccountToken())
        seq_id = UUID(us["associated_collections"][0]["id"])
        assert requests_mock.call_count == 1  # only 1 picture is blurred in the initial process
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"], "args": {"skip_blurring": True}},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
        ]

        response = client.post(f"/api/collections/{seq_id}/prepare")
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(create_test_app)

        assert requests_mock.call_count == 3  # both pictures are blurred in the second process
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"], "args": {"skip_blurring": True}},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"]},
        ]

        # we can also prepare without blurring
        response = client.post(f"/api/collections/{seq_id}/prepare", json={"skip_blurring": "true"})
        assert response.status_code == 202
        assert response.json == {}
        conftest.waitForAllJobsDone(create_test_app)

        assert requests_mock.call_count == 3  # no additional blurring
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"], "args": {"skip_blurring": True}},
            {"job_task": "dispatch", "upload_set_id": ids.id},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"]},
            {"job_task": "prepare", "picture_id": ids.pics["1.jpg"], "args": {"skip_blurring": True}},  # but more preparation
            {"job_task": "prepare", "picture_id": ids.pics["2.jpg"], "args": {"skip_blurring": True}},
        ]


def test_prepare_not_found_collection(create_test_app):
    with create_test_app.test_client() as client:
        response = client.post(f"/api/collections/00000000-0000-0000-0000-000000000000/prepare")
        assert response.status_code == 404
        assert response.json == {
            "message": "Collection 00000000-0000-0000-0000-000000000000 wasn't found in database",
            "status_code": 404,
        }


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_prepare_hidden_collections(requests_mock, datafiles, create_test_app, bobAccountToken):
    app = create_test_app
    mock_blurring_api_twice(requests_mock, datafiles)

    headers = {"Authorization": f"Bearer {bobAccountToken()}"}
    with create_test_app.test_client() as client:
        seq_location = conftest.createSequence(client, "a_sequence", jwtToken=bobAccountToken())
        seq_id = UUID(seq_location.split("/")[-1])

        pic1Id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, jwtToken=bobAccountToken())

        conftest.waitForSequence(client, seq_location)

        # we hide the collection
        response = client.patch(seq_location, data={"visible": "false"}, headers=headers)
        # should be impossible to prepare the collection without auth
        response = client.post(f"{seq_location}/prepare")
        assert response.status_code == 404
        response = client.post(f"{seq_location}/prepare", headers=headers)
        assert response.status_code == 202
        assert response.json == {}

        conftest.waitForAllJobsDone(create_test_app)
        assert _get_jobs() == [
            {"job_task": "prepare", "picture_id": UUID(pic1Id)},
            {"job_task": "finalize", "sequence_id": seq_id},
            {"job_task": "prepare", "picture_id": UUID(pic1Id)},
            {"job_task": "finalize", "sequence_id": seq_id},
        ]
        # collection is still hidden after the blurring
        response = client.get(f"{seq_location}")
        assert response.status_code == 404
        response = client.get(f"{seq_location}", headers=headers)
        assert response.status_code == 200
