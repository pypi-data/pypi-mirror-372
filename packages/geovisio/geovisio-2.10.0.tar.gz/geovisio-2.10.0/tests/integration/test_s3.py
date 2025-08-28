from urllib.parse import quote
from flask import current_app
import requests
import pytest
from geovisio.utils import filesystems
from ..conftest import SEQ_IMGS, dburl, waitForAllJobsDone, waitForSequence, createSequence, uploadPicture, getPictureIds, create_test_app
import boto3

# mark all tests in the module with the docker marker
pytestmark = [pytest.mark.docker, pytest.mark.skipci]


def _get_minio_bucket_url(minio, bucket, subdir):
    url = quote(minio, safe="")
    return f"s3://geovisio:SOME_VERY_SECRET_KEY@{bucket}/{subdir}?endpoint_url={url}"


@pytest.fixture
def split_storage_fs_url(minio):
    return filesystems.FilesystemsURL(
        tmp=_get_minio_bucket_url(minio, bucket="panoramax-private", subdir="tmp"),
        permanent=_get_minio_bucket_url(minio, bucket="panoramax-public", subdir="main-pictures"),
        derivates=_get_minio_bucket_url(minio, bucket="panoramax-public", subdir="derivates"),
    )


@pytest.fixture
def split_storage_app(dburl, split_storage_fs_url):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": split_storage_fs_url.tmp,
            "FS_PERMANENT_URL": split_storage_fs_url.permanent,
            "FS_DERIVATES_URL": split_storage_fs_url.derivates,
            "SERVER_NAME": "localhost:5000",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
        }
    ) as app:
        yield app


@SEQ_IMGS
def test_minio_split_storage_upload(split_storage_app, datafiles):
    """Everything should be ok while uploading pictures is the storage are split across several buckets"""
    with split_storage_app.test_client() as client:
        _check_upload(client, datafiles)


def _check_upload(client, datafiles, jwtToken=None):
    sequence = createSequence(client, "séquence", jwtToken=jwtToken)

    pic_id = uploadPicture(
        client,
        sequence,
        pic=(datafiles / "1.jpg").open("rb"),
        filename="a_pic.jpg",
        position=1,
        jwtToken=jwtToken,
    )

    waitForSequence(client, sequence)

    seq_response = client.get(f"{sequence}/items")
    assert seq_response.status_code < 400
    assert len(seq_response.json["features"]) == 1
    pic = seq_response.json["features"][0]
    assert pic["id"] == pic_id

    # by default the pictures are served by the API
    assert pic["assets"]["hd"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/hd.jpg"
    assert pic["assets"]["sd"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/sd.jpg"
    assert pic["assets"]["thumb"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/thumb.jpg"

    assert pic["asset_templates"]["tiles"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/tiled/{{TileCol}}_{{TileRow}}.jpg"


@pytest.fixture
def same_storage_app(dburl, minio):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir=""),
            "FS_TMP_URL": "",
            "FS_PERMANENT_URL": "",
            "FS_DERIVATES_URL": "",
            "SERVER_NAME": "localhost:5000",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
        }
    ) as app:
        yield app


@SEQ_IMGS
def test_minio_same_storage_upload(same_storage_app, datafiles):
    """Everything should be ok while uploading pictures is the FS_URL is defined"""
    with same_storage_app.test_client() as client:
        _check_upload(client, datafiles)


def test_openFilesystemsFromS3(minio):
    """Test that the uniq FS_URL parameter works for s3 based storage too"""
    from geovisio.utils import filesystems
    import fs.base

    res = filesystems.openFilesystemsFromConfig({"FS_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir="")})

    assert isinstance(res.tmp, fs.base.FS)
    assert isinstance(res.permanent, fs.base.FS)
    assert isinstance(res.derivates, fs.base.FS)

    res.tmp.writetext("test.txt", "test")
    res.permanent.writetext("test.txt", "test")
    res.derivates.writetext("test.txt", "test")


@pytest.fixture
def split_storage_app_with_external_url(dburl, minio):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": _get_minio_bucket_url(minio, bucket="panoramax-private", subdir="tmp"),
            "FS_PERMANENT_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir="main-pictures"),
            "FS_DERIVATES_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir="derivates"),
            "SERVER_NAME": "localhost:5000",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",  # exposing derivates pictures only works if derivates are always generated for the moment
            "API_PERMANENT_PICTURES_PUBLIC_URL": f"{minio}/panoramax-public/main-pictures",
            "API_DERIVATES_PICTURES_PUBLIC_URL": f"{minio}/panoramax-public/derivates",
            "SECRET_KEY": "a very secret key",
        }
    ) as app:
        yield app


def _pic_storage_path(picId):
    return f"/{str(picId)[0:2]}/{str(picId)[2:4]}/{str(picId)[4:6]}/{str(picId)[6:8]}/{str(picId)[9:]}"


@SEQ_IMGS
def test_external_url_for_pictures(split_storage_app_with_external_url, datafiles, minio):
    """
    The API should return url to the s3 pictures directly if asked, and those pictures should be available
    """
    with split_storage_app_with_external_url.test_client() as client:
        sequence = createSequence(client, "séquence")

        pic_id = uploadPicture(
            client,
            sequence,
            pic=(datafiles / "1.jpg").open("rb"),
            filename="a_pic.jpg",
            position=1,
        )

        waitForSequence(client, sequence)

        seq_response = client.get(f"{sequence}/items")
        assert seq_response.status_code < 400
        assert len(seq_response.json["features"]) == 1
        pic = seq_response.json["features"][0]
        assert pic["id"] == pic_id

        assert pic["assets"]["hd"]["href"] == f"{minio}/panoramax-public/main-pictures{_pic_storage_path(pic_id)}.jpg"
        f = requests.get(pic["assets"]["hd"]["href"])
        f.raise_for_status()
        assert len(f.content) > 0
        assert pic["assets"]["sd"]["href"] == f"{minio}/panoramax-public/derivates{_pic_storage_path(pic_id)}/sd.jpg"
        f = requests.get(pic["assets"]["sd"]["href"])
        f.raise_for_status()
        assert len(f.content) > 0
        assert pic["assets"]["thumb"]["href"] == f"{minio}/panoramax-public/derivates{_pic_storage_path(pic_id)}/thumb.jpg"
        f = requests.get(pic["assets"]["thumb"]["href"])
        f.raise_for_status()
        assert len(f.content) > 0

        assert (
            pic["asset_templates"]["tiles"]["href"]
            == f"{minio}/panoramax-public/derivates{_pic_storage_path(pic_id)}/tiles/{{TileCol}}_{{TileRow}}.jpg"
        )
        # we try to access the first tile
        f = requests.get(pic["asset_templates"]["tiles"]["href"].replace("{TileCol}", "0").replace("{TileRow}", "0"))
        f.raise_for_status()
        assert len(f.content) > 0

        r = client.get(f"/api/pictures/{pic_id}/hd.jpg", follow_redirects=False)
        assert r.status_code == 302
        assert r.location == f"{minio}/panoramax-public/main-pictures{_pic_storage_path(pic_id)}.jpg"

        r = client.get(f"/api/pictures/{pic_id}/sd.jpg", follow_redirects=False)
        assert r.status_code == 302
        assert r.location == f"{minio}/panoramax-public/derivates{_pic_storage_path(pic_id)}/sd.jpg"
        r = client.get(f"/api/pictures/{pic_id}/thumb.jpg", follow_redirects=False)
        assert r.status_code == 302
        assert r.location == f"{minio}/panoramax-public/derivates{_pic_storage_path(pic_id)}/thumb.jpg"


@SEQ_IMGS
def test_external_url_for_hidden_pictures(split_storage_app_with_external_url, datafiles, minio, dburl, bobAccountToken):
    """
    The API should not expose hidden picture though the s3 directly, to be able to check permissions
    """
    with split_storage_app_with_external_url.test_client() as client:
        token = bobAccountToken()
        sequence_location = createSequence(client, "séquence", jwtToken=token)

        pic_id = uploadPicture(
            client,
            sequence_location,
            pic=(datafiles / "1.jpg").open("rb"),
            filename="a_pic.jpg",
            position=1,
            jwtToken=token,
        )

        waitForSequence(client, sequence_location)

        # we set the picture as hidden
        response = client.patch(
            f"{sequence_location}/items/{pic_id}",
            data={"visible": "false"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # public calls should see no pictures
        seq_response = client.get(f"{sequence_location}/items")
        assert seq_response.status_code == 200
        assert len(seq_response.json["features"]) == 0

        # and authenticated call by the owner should see the pictures's internal urls
        seq_response = client.get(f"{sequence_location}/items", headers={"Authorization": f"Bearer {token}"})
        assert seq_response.status_code == 200
        assert len(seq_response.json["features"]) == 1

        pic = seq_response.json["features"][0]
        assert pic["id"] == pic_id

        assert pic["assets"]["hd"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/hd.jpg"
        f = client.get(f"/api/pictures/{pic_id}/hd.jpg", headers={"Authorization": f"Bearer {token}"})
        assert f.status_code == 200 and len(f.get_data()) > 0

        assert pic["assets"]["sd"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/sd.jpg"
        f = client.get(f"/api/pictures/{pic_id}/sd.jpg", headers={"Authorization": f"Bearer {token}"})
        assert f.status_code == 200 and len(f.get_data()) > 0

        assert pic["assets"]["thumb"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/thumb.jpg"
        f = client.get(f"/api/pictures/{pic_id}/thumb.jpg", headers={"Authorization": f"Bearer {token}"})
        assert f.status_code == 200 and len(f.get_data()) > 0

        assert pic["asset_templates"]["tiles"]["href"] == f"http://localhost:5000/api/pictures/{pic_id}/tiled/{{TileCol}}_{{TileRow}}.jpg"
        # we try to access the first tile
        f = client.get(f"api/pictures/{pic_id}/tiled/0_0.jpg", headers={"Authorization": f"Bearer {token}"})
        assert f.status_code == 200 and len(f.get_data()) > 0


@SEQ_IMGS
def test_external_derivates_without_preprocess(minio):
    with pytest.raises(Exception):
        with create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": _get_minio_bucket_url(minio, bucket="panoramax-private", subdir="tmp"),
                "FS_PERMANENT_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir="main-pictures"),
                "FS_DERIVATES_URL": _get_minio_bucket_url(minio, bucket="panoramax-public", subdir="derivates"),
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
                "API_PERMANENT_PICTURES_PUBLIC_URL": f"{minio}/panoramax-public/main-pictures",
                "API_DERIVATES_PICTURES_PUBLIC_URL": f"{minio}/panoramax-public/derivates",
            }
        ):
            pass


@SEQ_IMGS
def test_delete_picture(datafiles, split_storage_fs_url, dburl, bobAccountToken, minio):
    """
    Test that deleting a picture also work on s3
    """

    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": split_storage_fs_url.tmp,
                "FS_PERMANENT_URL": split_storage_fs_url.permanent,
                "FS_DERIVATES_URL": split_storage_fs_url.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "SECRET_KEY": "a very secret key",
            }
        ) as app,
        app.test_client() as client,
    ):
        _check_upload(client, datafiles, bobAccountToken())

        sequence = getPictureIds(dburl)[0]
        first_pic_id = sequence.pictures[0].id

        # before the delte, we can query the first picture
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 200

        response = client.get(f"/api/collections/{sequence.id}/items")
        assert response.status_code == 200 and response.json
        assert len(response.json["features"]) == 1

        s3 = boto3.resource(
            "s3",
            aws_access_key_id="geovisio",
            aws_secret_access_key="SOME_VERY_SECRET_KEY",
            endpoint_url=minio,
        )
        my_bucket = s3.Bucket("panoramax-public")

        # bucket should include base picture and all its derivates
        all_files = {o.key for o in my_bucket.objects.all()}
        expected_files = {
            f"main-pictures/{first_pic_id[0:2]}/{first_pic_id[2:4]}/{first_pic_id[4:6]}/{first_pic_id[6:8]}/{first_pic_id[9:]}.jpg",
            f"derivates/{first_pic_id[0:2]}/{first_pic_id[2:4]}/{first_pic_id[4:6]}/{first_pic_id[6:8]}/{first_pic_id[9:]}/thumb.jpg",
            f"derivates/{first_pic_id[0:2]}/{first_pic_id[2:4]}/{first_pic_id[4:6]}/{first_pic_id[6:8]}/{first_pic_id[9:]}/sd.jpg",
        } | {
            f"derivates/{first_pic_id[0:2]}/{first_pic_id[2:4]}/{first_pic_id[4:6]}/{first_pic_id[6:8]}/{first_pic_id[9:]}/tiles/{c}_{r}.jpg"
            for c in range(8)
            for r in range(4)
        }
        assert all_files == expected_files

        response = client.delete(
            f"/api/collections/{sequence.id}/items/{first_pic_id}",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 204

        # The first picture should not be returned in any response
        response = client.get(f"/api/collections/{sequence.id}/items/{first_pic_id}")
        assert response.status_code == 404

        # and after a while since it's asynchrone, the files will be deleted
        waitForAllJobsDone(current_app)

        # bucket should be empty
        all_files = {o.key for o in my_bucket.objects.all()}
        assert all_files == set()
