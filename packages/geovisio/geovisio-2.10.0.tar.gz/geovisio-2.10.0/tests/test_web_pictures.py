import pytest
import psycopg
import io
from PIL import Image
from . import conftest


@conftest.SEQ_IMGS
def test_getPictureHD(datafiles, initSequenceApp, dburl):
    # Retrieve loaded sequence metadata
    with initSequenceApp(datafiles) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            picId = cursor.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0]

            assert len(str(picId)) > 0

            # Call on WebP
            response = client.get("/api/pictures/" + str(picId) + "/hd.webp")
            assert response.status_code == 404  # no webp generated, no webp served

            # Call on JPEG
            response = client.get("/api/pictures/" + str(picId) + "/hd.jpg")
            assert response.status_code == 200
            assert response.content_type == "image/jpeg"

            # Call on invalid format
            response = client.get("/api/pictures/" + str(picId) + "/hd.gif")
            assert response.status_code == 404

            # Call on unexisting picture
            response = client.get("/api/pictures/ffffffff-ffff-ffff-ffff-ffffffffffff/hd.webp")
            assert response.status_code == 404

            # Call on hidden picture
            cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])
            conn.commit()
            response = client.get("/api/pictures/" + str(picId) + "/hd.jpg")
            assert response.status_code == 403


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_getPictureHD_blurred(requests_mock, datafiles, initSequenceApp, dburl):
    conftest.mockBlurringAPIPost(datafiles, requests_mock)
    with initSequenceApp(datafiles, blur=True) as client:
        # Retrieve loaded sequence metadata
        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                picId = cursor.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0]

                assert len(str(picId)) > 0

                # Call on WebP
                response = client.get("/api/pictures/" + str(picId) + "/hd.webp")
                assert response.status_code == 404

                # Call on JPEG
                response = client.get("/api/pictures/" + str(picId) + "/hd.jpg")
                assert response.status_code == 200
                assert response.content_type == "image/jpeg"


@conftest.SEQ_IMGS
def test_getPictureSD(datafiles, initSequenceApp, dburl):
    # Retrieve loaded sequence metadata
    with initSequenceApp(datafiles) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            picId = cursor.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0]

            assert len(str(picId)) > 0

            # Call on WebP
            response = client.get("/api/pictures/" + str(picId) + "/sd.webp")
            assert response.status_code == 404

            # Call on JPEG
            response = client.get("/api/pictures/" + str(picId) + "/sd.jpg")
            assert response.status_code == 200
            assert response.content_type == "image/jpeg"

            img = Image.open(io.BytesIO(response.get_data()))
            w, h = img.size
            assert w == 2048

            # Call API on unexisting picture
            response = client.get("/api/pictures/ffffffff-ffff-ffff-ffff-ffffffffffff/sd.jpg")
            assert response.status_code == 404

            # Call API on hidden picture
            cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])
            conn.commit()
            response = client.get("/api/pictures/" + str(picId) + "/sd.jpg")
            assert response.status_code == 403


@conftest.SEQ_IMGS
def test_getPictureThumb(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            picId = cursor.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0]

            assert len(str(picId)) > 0

            # Call on WebP not supported
            response = client.get("/api/pictures/" + str(picId) + "/thumb.webp")
            assert response.status_code == 404

            # Call on JPEG
            response = client.get("/api/pictures/" + str(picId) + "/thumb.jpg")
            assert response.status_code == 200
            assert response.content_type == "image/jpeg"

            img = Image.open(io.BytesIO(response.get_data()))
            w, h = img.size
            assert w == 500
            assert h == 300

            # Call API on unexisting picture
            response = client.get("/api/pictures/ffffffff-ffff-ffff-ffff-ffffffffffff/thumb.jpg")
            assert response.status_code == 404

            # Call API on hidden picture
            cursor.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])
            conn.commit()
            response = client.get("/api/pictures/" + str(picId) + "/thumb.jpg")
            assert response.status_code == 403


def test_getPictureTiledEmpty(tmp_path, client):
    # Call API on unexisting picture
    response = client.get("/api/pictures/00000000-0000-0000-0000-000000000000/tiled/0_0.jpg")
    assert response.status_code == 404


@pytest.mark.parametrize(
    ("col", "row", "httpCode", "picStatus", "format"),
    (
        (0, 0, 404, "ready", "webp"),
        (0, 0, 200, "ready", "jpeg"),
        (7, 3, 200, "ready", "jpeg"),
        (8, 4, 404, "ready", "jpeg"),
        (-1, -1, 404, "ready", "jpeg"),
        (0, 0, 403, "hidden", "jpeg"),
    ),
)
@conftest.SEQ_IMGS
def test_getPictureTiled(datafiles, initSequenceApp, dburl, col, row, httpCode, picStatus, format):
    with initSequenceApp(datafiles) as client, psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            picId = str(cursor.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0])

            assert len(str(picId)) > 0

            seqId = cursor.execute("SELECT id FROM sequences LIMIT 1").fetchone()[0]

            assert len(str(seqId)) > 0

            if picStatus != "ready":
                cursor.execute("UPDATE pictures SET status = %s WHERE id = %s", (picStatus, picId))
                conn.commit()

            response = client.get(f"/api/pictures/{picId}/tiled/{col}_{row}.{'jpg' if format == 'jpeg' else format}")

            assert response.status_code == httpCode

            if httpCode == 200:
                assert response.content_type == f"image/{format}"
                diskImg = Image.open(
                    f"{datafiles}/derivates/{picId[0:2]}/{picId[2:4]}/{picId[4:6]}/{picId[6:8]}/{picId[9:]}/tiles/{col}_{row}.jpg"
                )
                apiImg = Image.open(io.BytesIO(response.get_data()))

                assert conftest.arePicturesSimilar(diskImg, apiImg, limit=2)


@conftest.SEQ_IMGS_FLAT
def test_getPictureTiled_flat(datafiles, initSequenceApp, tmp_path, dburl):
    with initSequenceApp(datafiles) as client, psycopg.connect(dburl) as conn:
        # Get picture ID
        picId = conn.execute("SELECT id FROM pictures LIMIT 1").fetchone()[0]
        assert len(str(picId)) > 0

        # Check tiles API call
        response = client.get("/api/pictures/" + str(picId) + "/tiled/0_0.jpg")
        assert response.status_code == 404
