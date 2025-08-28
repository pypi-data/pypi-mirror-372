from importlib import metadata
import json
import os
import io
from pathlib import Path
import psycopg
import re
from psycopg.rows import dict_row
from datetime import date, datetime, timezone, timedelta, time
from PIL import Image
from geopic_tag_reader import reader, writer
from uuid import UUID
import pytest

from geovisio.utils import db
import geovisio.utils.sequences
from geovisio.workers import runner_pictures
from . import conftest
from tests.conftest import create_test_app, start_background_worker
from geovisio import utils

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


@conftest.SEQ_IMGS
def test_processSequence(datafiles, initSequenceApp, tmp_path, dburl, defaultAccountID):
    # Check results
    with initSequenceApp(datafiles), psycopg.connect(dburl, row_factory=dict_row) as db2:
        # Sequence definition
        res0 = db2.execute(
            """
            SELECT
                id, status, metadata,
                account_id, ST_AsText(geom) AS geom,
                computed_type, computed_model, computed_capture_date
            FROM sequences
        """
        ).fetchall()[0]

        seqId = str(res0["id"])
        assert len(seqId) > 0

        # use regex because float precision may differ between systems
        expectedGeom = re.compile(
            r"^MULTILINESTRING\(\(1\.919185441799\d+ 49\.00688961988\d+,1\.919189623000\d+ 49\.0068986458\d+,1\.919196360602\d+ 49\.00692625960\d+,1\.919199780601\d+ 49\.00695484980\d+,1\.919194019996\d+ 49\.00697341759\d+\)\)$"
        )
        assert expectedGeom.match(res0["geom"]) is not None
        assert res0["status"] == "ready"
        assert res0["account_id"] == defaultAccountID
        assert res0["metadata"]["title"] == "seq1"
        assert res0["computed_type"] == "equirectangular"
        assert res0["computed_model"] == "GoPro Max"
        assert res0["computed_capture_date"].isoformat() == "2021-07-29"

        # Pictures
        res1 = db2.execute("SELECT id, ts, status, metadata, account_id FROM pictures ORDER BY ts").fetchall()

        assert len(res1) == 5
        assert len(str(res1[0]["id"])) > 0
        assert res1[0]["ts"].timestamp() == 1627550214.0
        assert res1[0]["status"] == "ready"
        assert res1[0]["metadata"]["field_of_view"] == 360
        assert res1[0]["metadata"]["pitch"] == 0
        assert res1[0]["metadata"]["roll"] == 0
        assert res1[0]["account_id"] == defaultAccountID

        picIds = []
        for rec in res1:
            picIds.append(str(rec["id"]))

        # Sequences + pictures
        with db2.cursor() as cursor:
            res2 = cursor.execute("SELECT pic_id FROM sequences_pictures WHERE seq_id = %s ORDER BY rank", [seqId]).fetchall()
            resPicIds = [str(f["pic_id"]) for f in res2]

            assert resPicIds == picIds

        # Check destination folder structure
        for picId in picIds:
            permaPath = str(tmp_path / "permanent" / picId[0:2] / picId[2:4] / picId[4:6] / picId[6:8] / picId[9:]) + ".jpg"
            derivPath = tmp_path / "derivates" / picId[0:2] / picId[2:4] / picId[4:6] / picId[6:8] / picId[9:]
            assert os.path.isfile(permaPath)
            assert os.path.isdir(derivPath)
            assert os.path.isdir(derivPath / "tiles")
            assert os.path.isfile(derivPath / "sd.jpg")
            assert os.path.isfile(derivPath / "thumb.jpg")

        # Check upload folder has been removed
        assert len(os.listdir(tmp_path / "tmp")) == 0

        newSequencePicturesEntries = db2.execute(
            "select rank from sequences_pictures inner join pictures on (pic_id = id) order by ts asc"
        ).fetchall()
        assert newSequencePicturesEntries == [{"rank": rank} for rank in range(1, len(newSequencePicturesEntries) + 1)]


@conftest.SEQ_IMGS_FLAT
def test_processSequence_flat(datafiles, initSequenceApp, tmp_path, dburl, defaultAccountID):
    with psycopg.connect(dburl, row_factory=dict_row, autocommit=True) as db2:
        # Run processing
        with initSequenceApp(datafiles):

            # Sequence definition
            res0 = db2.execute(
                """
                SELECT
                    id, status, metadata,
                    account_id, ST_AsText(geom) AS geom,
                    computed_type, computed_model, computed_capture_date
                FROM sequences
            """
            ).fetchall()[0]

            seqId = str(res0["id"])
            assert len(seqId) > 0

            assert res0["geom"] is None  # the points are too far apart to have a geometry
            assert res0["status"] == "ready"
            assert res0["account_id"] == defaultAccountID
            assert res0["metadata"]["title"] == "seq1"
            assert res0["computed_type"] == "flat"
            assert res0["computed_model"] == "OLYMPUS IMAGING CORP. SP-720UZ"
            assert res0["computed_capture_date"].isoformat() == "2015-04-25"

            # Pictures
            res1 = db2.execute("SELECT id, ts, status, metadata, account_id FROM pictures ORDER BY ts").fetchall()

            assert len(res1) == 2
            assert len(str(res1[0]["id"])) > 0
            assert res1[0]["ts"] == datetime.fromisoformat("2015-04-25T15:36:17+02:00")
            assert res1[0]["metadata"]["tz"] == "CEST"
            assert res1[0]["status"] == "ready"
            assert res1[0]["metadata"]["field_of_view"] == 67
            assert res1[0]["metadata"]["pitch"] is None
            assert res1[0]["metadata"]["roll"] is None
            assert res1[0]["account_id"] == defaultAccountID

            picIds = []
            for rec in res1:
                picIds.append(str(rec["id"]))

            # Check destination folder structure
            for picId in picIds:
                permaPath = str(tmp_path / "permanent" / picId[0:2] / picId[2:4] / picId[4:6] / picId[6:8] / picId[9:]) + ".jpg"
                derivPath = tmp_path / "derivates" / picId[0:2] / picId[2:4] / picId[4:6] / picId[6:8] / picId[9:]
                assert os.path.isfile(permaPath)
                assert os.path.isdir(derivPath)
                assert not os.path.isdir(derivPath / "tiles")
                assert os.path.isfile(derivPath / "sd.jpg")
                assert os.path.isfile(derivPath / "thumb.jpg")

            # Check upload folder has been removed
            assert len(os.listdir(tmp_path / "tmp")) == 0


@conftest.SEQ_IMGS_NOHEADING
def test_processSequence_noheading(datafiles, initAppWithData, dburl):
    with psycopg.connect(dburl, row_factory=dict_row) as db2, initAppWithData(datafiles, preprocess=False):

        # Sequence definition
        seqId = db2.execute("SELECT id FROM sequences").fetchall()
        assert len(seqId) == 1

        # Pictures
        pics = db2.execute("SELECT * FROM pictures").fetchall()

        for r in pics:
            assert r["status"] == "ready"
            assert r["metadata"].get("heading") is None

        headings = {r["metadata"].get("originalFileName"): r["heading"] for r in pics}
        assert headings == {"e1.jpg": 277, "e2.jpg": 272, "e3.jpg": 272, "e4.jpg": 270, "e5.jpg": 270}


@conftest.SEQ_IMGS
def test_updateSequenceHeadings_unchanged(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId = db.execute("SELECT id FROM sequences").fetchone()
        assert seqId
        seqId = seqId[0]
        picHeadings = {}
        for key, value in db.execute("SELECT id, heading FROM pictures").fetchall():
            picHeadings[key] = value

        geovisio.utils.sequences.update_headings(db, seqId, relativeHeading=10, updateOnlyMissing=True)

        for id, heading, headingMetadata in db.execute("SELECT id, heading, metadata->>'heading' AS mh FROM pictures").fetchall():
            assert picHeadings[id] == heading
            assert headingMetadata is None


@conftest.SEQ_IMGS
def test_updateSequenceHeadings_updateAllExisting(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId = db.execute("SELECT id FROM sequences").fetchone()
        assert seqId is not None
        seqId = seqId[0]
        geovisio.utils.sequences.update_headings(db, seqId, relativeHeading=10, updateOnlyMissing=False)
        res = db.execute("select metadata->>'originalFileName', heading, metadata->>'heading' AS mh from pictures").fetchall()
        for r in res:
            assert r[2] is None
        headings = {r[0].split("/")[-1]: r[1] for r in res}
        assert headings == {"1.jpg": 34, "2.jpg": 23, "3.jpg": 16, "4.jpg": 352, "5.jpg": 352}


@conftest.SEQ_IMG
def test_processPictureFiles_noblur_preprocess(datafiles, tmp_path, fsesUrl, dburl, defaultAccountID):
    with open(datafiles / "1.jpg", "rb") as f:
        picAsBytes = f.read()
    picture = Image.open(io.BytesIO(picAsBytes))
    pictureOrig = picture.copy()

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
        }
    ) as app:
        with psycopg.connect(dburl) as db:
            seqId = utils.sequences.createSequence({}, defaultAccountID)
            picId = utils.pictures.insertNewPictureInDatabase(db, seqId, 0, picAsBytes, defaultAccountID, {})

            # persist file
            utils.pictures.saveRawPicture(picId, picAsBytes, isBlurred=False)

            runner_pictures.process_next_job(app)

            pics = conftest.getPictureIds(dburl)[0].pictures
            derivate_dir = pics[0].get_derivate_dir(datafiles)

            # No Blur + preprocess derivates = generates thumbnail and all derivates+ original file
            assert sorted(os.listdir(derivate_dir)) == [
                "sd.jpg",
                "thumb.jpg",
                "tiles",
            ]
            assert conftest.arePicturesSimilar(pictureOrig, Image.open(str(pics[0].get_permanent_file(datafiles))))

            # Check content is same as generatePictureDerivates
            os.makedirs(datafiles / "derivates" / "gvs_picder")
            resPicDer = utils.pictures.generatePictureDerivates(
                app.config["FILESYSTEMS"].derivates, picture, {"cols": 8, "rows": 4, "width": 5760, "height": 2880}, "/gvs_picder"
            )
            assert resPicDer is True
            assert sorted(os.listdir(derivate_dir)) == sorted(app.config["FILESYSTEMS"].derivates.listdir("/gvs_picder/"))
            assert sorted(os.listdir(f"{derivate_dir}/tiles/")) == sorted(app.config["FILESYSTEMS"].derivates.listdir("/gvs_picder/tiles/"))


@conftest.SEQ_IMG
def test_processPictureFiles_noblur_ondemand(datafiles, tmp_path, fsesUrl, dburl, defaultAccountID):
    with open(datafiles / "1.jpg", "rb") as f:
        picAsBytes = f.read()
    pictureOrig = Image.open(io.BytesIO(picAsBytes))

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
        }
    ) as app:
        with psycopg.connect(dburl) as db:
            seqId = utils.sequences.createSequence({}, defaultAccountID)
            picId = utils.pictures.insertNewPictureInDatabase(db, seqId, 0, picAsBytes, defaultAccountID, {})

            # persist file
            utils.pictures.saveRawPicture(picId, picAsBytes, isBlurred=False)

            runner_pictures.process_next_job(app)

            pics = conftest.getPictureIds(dburl)[0].pictures
            derivate_dir = pics[0].get_derivate_dir(datafiles)

            # No blur + on-demand derivates = generates thumbnail + original file
            assert sorted(os.listdir(derivate_dir)) == ["thumb.jpg"]
            assert conftest.arePicturesSimilar(pictureOrig, Image.open(str(pics[0].get_permanent_file(datafiles))))


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_blur_preprocess(monkeypatch, datafiles, tmp_path, fsesUrl, dburl, defaultAccountID):
    monkeypatch.setattr(utils.pictures, "createBlurredHDPicture", conftest.mockCreateBlurredHDPictureFactory(datafiles))
    with open(datafiles / "1.jpg", "rb") as f:
        picAsBytes = f.read()
    pictureOrig = Image.open(io.BytesIO(picAsBytes))

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "API_BLUR_URL": "https://geovisio-blurring.net",
        }
    ) as app:
        with psycopg.connect(dburl) as db:
            seqId = utils.sequences.createSequence({}, defaultAccountID)
            picId = utils.pictures.insertNewPictureInDatabase(db, seqId, 0, picAsBytes, defaultAccountID, {})

            # persist file
            utils.pictures.saveRawPicture(picId, picAsBytes, isBlurred=False)

            runner_pictures.process_next_job(app)

            pics = conftest.getPictureIds(dburl)[0].pictures
            derivate_dir = pics[0].get_derivate_dir(datafiles)

            # Blur + preprocess derivates = generates thumbnail, all derivates + blurred original file
            assert sorted(os.listdir(derivate_dir)) == [
                "sd.jpg",
                "thumb.jpg",
                "tiles",
            ]
            # picture should be blurred, so different from original
            assert not conftest.arePicturesSimilar(pictureOrig, Image.open(str(pics[0].get_permanent_file(datafiles))))

            # Check tmp folder has been removed
            assert len(app.config["FILESYSTEMS"].tmp.listdir("/")) == 0


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_blur_ondemand(monkeypatch, datafiles, tmp_path, fsesUrl, dburl, defaultAccountID):
    monkeypatch.setattr(utils.pictures, "createBlurredHDPicture", conftest.mockCreateBlurredHDPictureFactory(datafiles))
    with open(datafiles / "1.jpg", "rb") as f:
        picAsBytes = f.read()
    pictureOrig = Image.open(io.BytesIO(picAsBytes))

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "API_BLUR_URL": "https://geovisio-blurring.net",
        }
    ) as app:
        with psycopg.connect(dburl) as db:
            seqId = utils.sequences.createSequence({}, defaultAccountID)
            picId = utils.pictures.insertNewPictureInDatabase(db, seqId, 0, picAsBytes, defaultAccountID, {})

            # persist file
            utils.pictures.saveRawPicture(picId, picAsBytes, isBlurred=False)

            runner_pictures.process_next_job(app)

            pics = conftest.getPictureIds(dburl)[0].pictures
            derivate_dir = pics[0].get_derivate_dir(datafiles)

            # Blur + on-demand derivates = generates thumbnail + blurred original file
            assert sorted(os.listdir(derivate_dir)) == ["thumb.jpg"]
            # picture should be blurred, so different from original
            assert not conftest.arePicturesSimilar(pictureOrig, Image.open(str(pics[0].get_permanent_file(datafiles))))

            # Check tmp folder has been removed
            assert len(app.config["FILESYSTEMS"].tmp.listdir("/")) == 0


@conftest.SEQ_IMGS
def test_get_next_job(datafiles, app, tmp_path, dburl, defaultAccountID):
    """
    Test runner_pictures._get_next_picture_to_process
    Insert 3 images, they should be taken in order 1 -> 3 -> 2 -> None (since 2 has 1 error, we consider that we should retry it last)
    """
    picBytes = open(str(datafiles / "1.jpg"), "rb").read()

    seqId = utils.sequences.createSequence({}, defaultAccountID)
    with psycopg.connect(dburl) as db:
        db.commit()
        pic1_id = utils.pictures.insertNewPictureInDatabase(db, seqId, 1, picBytes, defaultAccountID, {})
        db.commit()  # we commit each insert to get different insert_at timestamp
        pic2_id = utils.pictures.insertNewPictureInDatabase(db, seqId, 2, picBytes, defaultAccountID, {})
        db.commit()
        pic3_id = utils.pictures.insertNewPictureInDatabase(db, seqId, 3, picBytes, defaultAccountID, {})
        db.commit()
        # being 'preparing-derivates' should only makes pic 2 to be taken last
        db.execute("UPDATE job_queue SET nb_errors = 1 WHERE picture_id = %s", [pic2_id])
        db.commit()

    with runner_pictures._get_next_job(app) as db_job:
        assert db_job is not None and db_job.pic is not None
        assert db_job.pic.id == pic1_id

        with runner_pictures._get_next_job(app) as db_job2:
            assert db_job2 is not None and db_job2.pic is not None
            assert db_job2.pic.id == pic3_id

            try:
                with runner_pictures._get_next_job(app) as db_job3:
                    assert db_job3 is not None and db_job3.pic is not None
                    assert db_job3.pic.id == pic2_id

                    # There should no more be pictures to process (but there might be a sequence finalization job)
                    with runner_pictures._get_next_job(app) as db_job4:
                        assert db_job4 is None or (db_job4.seq is not None and db_job4.task == "finalize")

                    # An exception is raised, a rollback should occurs, pic2 should be marked on error and lock should be released
                    raise Exception("some exception")
            except:
                pass

            with runner_pictures._get_next_job(app) as db_job5:
                assert db_job5 is None or (db_job5.seq is not None and db_job5.task == "finalize")


@conftest.SEQ_IMGS
def test_split_workers(datafiles, dburl, tmp_path):
    """Test posting new pictures on upload set with some split workers to do the job"""

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
        with app.test_client() as client, psycopg.connect(dburl, row_factory=dict_row) as conn:
            seq_location = conftest.createSequence(client, os.path.basename(datafiles))
            seq_id = UUID(seq_location.split("/")[-1])
            pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1)

            # no worker start yet, pictures should be waiting for process
            r = conn.execute("SELECT count(*) as nb FROM job_queue").fetchone()
            assert r and r["nb"] == 1
            r = conn.execute("SELECT id, status FROM pictures").fetchall()
            assert r and list(r) == [{"id": UUID(pic_id), "status": "waiting-for-process"}]
            # no jobs should have been started
            r = conn.execute("SELECT count(*) as nb FROM job_history").fetchone()
            assert r and r["nb"] == 0

            # start a background job that stop when all pictures have been processed
            start_background_worker(
                dburl,
                tmp_path,
                config={
                    "TESTING": True,
                    "DB_URL": dburl,
                    "FS_URL": str(tmp_path),
                    "FS_TMP_URL": None,
                    "FS_PERMANENT_URL": None,
                    "FS_DERIVATES_URL": None,
                },
            )

            # all should be ready
            r = conn.execute("SELECT count(*) AS nb FROM job_queue").fetchone()
            assert r and r["nb"] == 0

            r = conn.execute("SELECT id, status FROM pictures").fetchall()
            assert r and list(r) == [{"id": UUID(pic_id), "status": "ready"}]

            # all jobs should have been correctly traced in the database, 1 job for the picture, one for the sequence completion
            r = conn.execute(
                "SELECT id, picture_id, sequence_id, job_task, started_at, finished_at, error FROM job_history ORDER BY finished_at"
            ).fetchall()
            assert r and len(r) == 2
            assert r[0]["picture_id"] == UUID(pic_id)
            assert r[0]["sequence_id"] is None
            assert r[0]["job_task"] == "prepare"
            assert r[0]["started_at"].date() == date.today()
            assert r[0]["finished_at"].date() == date.today()
            assert r[0]["started_at"] < r[0]["finished_at"]
            assert r[0]["error"] is None

            assert r[1]["picture_id"] is None
            assert r[1]["sequence_id"] == seq_id
            assert r[1]["job_task"] == "finalize"
            assert r[1]["started_at"].date() == date.today()
            assert r[1]["finished_at"].date() == date.today()
            assert r[1]["started_at"] < r[1]["finished_at"]
            assert r[1]["error"] is None


@conftest.SEQ_IMGS
def test_split_workers_reprocess_pic(datafiles, dburl, tmp_path):
    """
    Test posting new picture with some split workers to do the job
    After the picture has been processed, we try to reprocess the picture, and this should work
    """

    def start_worker():
        start_background_worker(
            dburl,
            tmp_path,
            config={
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
            },
        )

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
            seq_location = conftest.createSequence(client, os.path.basename(datafiles))
            pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1)

            # no worker start yet, pictures should be waiting for process
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 1
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "waiting-for-process", None, 0)]

            # start a background job that stop when all pictures have been processed
            start_worker()

            # all should be ready
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 0
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "ready", None, 0)]

            # we add again the picture into the picture_to_process table
            r = conn.execute("INSERT INTO job_queue (picture_id, task) VALUES (%s, 'prepare')", [pic_id])
            conn.commit()

            # no worker start yet, pictures should be waiting for process
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 1
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [
                (UUID(pic_id), "ready", None, 0)
            ]  # picture is ready even if it need processing, because it has already been processed once

            # start a background job that stop when all pictures have been processed
            start_worker()

            # all should be ready
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 0
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "ready", None, 0)]


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_split_workers_reprocess_pic_blur(monkeypatch, datafiles, dburl, tmp_path):
    monkeypatch.setattr(utils.pictures, "createBlurredHDPicture", conftest.mockCreateBlurredHDPictureFactory(datafiles))
    """
    Test posting new picture with some split workers to do the job
    After the picture has been processed, we try to reprocess the picture, and this should work even if blurring is needed
    """

    def start_worker():
        start_background_worker(
            dburl,
            tmp_path,
            config={
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "API_BLUR_URL": conftest.MOCK_BLUR_API,
            },
        )

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
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
        }
    ) as app:
        with app.test_client() as client, psycopg.connect(dburl) as conn:
            seq_location = conftest.createSequence(client, os.path.basename(datafiles))
            pic_id = conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1, isBlurred=False)

            # no worker start yet, pictures should be waiting for process
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 1
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "waiting-for-process", None, 0)]

            # start a background job that stop when all pictures have been processed
            start_worker()

            # all should be ready
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 0
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "ready", None, 0)]

            # we add again the picture into the picture_to_process table
            r = conn.execute("INSERT INTO job_queue (picture_id, task) VALUES (%s, 'prepare')", [pic_id])
            conn.commit()

            # no worker start yet, pictures should be waiting for process
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 1
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [
                (UUID(pic_id), "ready", None, 0)
            ]  # picture is ready even if it need processing, because it has already been processed once

            # start a background job that stop when all pictures have been processed
            start_worker()

            # all should be ready
            r = conn.execute("SELECT count(*) FROM job_queue").fetchone()
            assert r and r[0] == 0
            r = conn.execute("SELECT id, status, process_error, nb_errors FROM pictures").fetchall()
            assert r and list(r) == [(UUID(pic_id), "ready", None, 0)]


NB_PROCESS_PIC_CALLS = 0


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_retry_ok(datafiles, dburl, tmp_path, monkeypatch):
    """
    If picture process raises a RecoverableException (like if the blurring API is momentanously unavailable), the preparing job should be retried
    """
    from geovisio.workers import runner_pictures

    global NB_PROCESS_PIC_CALLS
    NB_PROCESS_PIC_CALLS = 0

    def new_processPictureFiles(dbJob, _config):
        """Mock function that raises an exception the first 3 times it is called"""
        global NB_PROCESS_PIC_CALLS
        NB_PROCESS_PIC_CALLS += 1
        if NB_PROCESS_PIC_CALLS <= 3:
            raise runner_pictures.RecoverableProcessException("oh no! pic process failed")

    monkeypatch.setattr(runner_pictures, "processPictureFiles", new_processPictureFiles)

    def start_worker():
        start_background_worker(
            dburl,
            tmp_path,
            config={
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "PICTURE_PROCESS_NB_RETRIES": 3,
            },
        )

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
            "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            seq_id = UUID(seq_location.split("/")[-1])
            pic1_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1))

            start_worker()

            def wanted_state(seq):
                pic_status = {p["rank"]: p["status"] for p in seq.json["items"]}
                return pic_status == {1: "ready"}

            s = conftest.waitForSequenceState(client, seq_location, wanted_state)

            # check that all jobs have been correctly persisted in the database
            with psycopg.connect(dburl, row_factory=dict_row) as conn:
                jobs = conn.execute(
                    "SELECT id, picture_id, job_task, started_at, finished_at, error FROM job_history WHERE picture_id IS NOT NULL ORDER BY started_at"
                ).fetchall()
                # there should be 4 jobs, 3 failures and a job ok
                assert jobs and len(jobs) == 4

                for job in jobs:
                    assert job["job_task"] == "prepare"
                    assert job["started_at"].date() == date.today()
                    assert job["finished_at"].date() == date.today()
                    assert job["started_at"] < job["finished_at"]
                    assert job["picture_id"] == pic1_id

                for job in jobs[0:2]:
                    assert job["error"] == "oh no! pic process failed"

                assert jobs[3]["error"] is None

                # and there should be one sequence completion job
                jobs = conn.execute(
                    "SELECT id, sequence_id, job_task, started_at, finished_at, error FROM job_history WHERE sequence_id IS NOT NULL ORDER BY started_at",
                ).fetchall()
                # there should be 4 jobs, 3 failures and a job ok
                assert jobs and len(jobs) == 1
                assert jobs[0]["job_task"] == "finalize"
                assert jobs[0]["started_at"].date() == date.today()
                assert jobs[0]["finished_at"].date() == date.today()
                assert jobs[0]["started_at"] < jobs[0]["finished_at"]
                assert jobs[0]["sequence_id"] == seq_id

                # and no jobs should be in queue
                pic_to_process = conn.execute("SELECT picture_id from job_queue").fetchall()
                assert pic_to_process == []

            # we should also have those info via the geovisio_status route
            s = client.get(f"{seq_location}/geovisio_status")
            assert s and s.status_code == 200 and s.json
            assert s.json["status"] == "ready"  # sequence should be ready
            assert len(s.json["items"]) == 1
            item = s.json["items"][0]

            processed_at = item.pop("processed_at")
            assert processed_at.startswith(date.today().isoformat())

            assert item == {
                "id": str(pic1_id),
                "nb_errors": 3,
                "processing_in_progress": False,
                "rank": 1,
                "status": "ready",
            }


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_retry_ko_without_separate_workers(datafiles, dburl, tmp_path, monkeypatch):
    """
    Retry should also work with separate workers
    """
    from geovisio.workers import runner_pictures

    global NB_PROCESS_PIC_CALLS
    NB_PROCESS_PIC_CALLS = 0

    def new_processPictureFiles(dbJob, _config):
        """Mock function that raises an exception for 1.jpg the first 3 times it is called"""
        global NB_PROCESS_PIC_CALLS
        NB_PROCESS_PIC_CALLS += 1
        if NB_PROCESS_PIC_CALLS <= 3:
            raise runner_pictures.RecoverableProcessException("oh no! pic process failed")

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
            seq_id = UUID(seq_location.split("/")[-1])
            pic1_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1))

            def wanted_state(seq):
                pic_status = {p["rank"]: p["status"] for p in seq.json["items"]}
                return pic_status == {1: "ready"}

            s = conftest.waitForSequenceState(client, seq_location, wanted_state)

            # check that all jobs have been correctly persisted in the database
            with psycopg.connect(dburl, row_factory=dict_row) as conn:
                jobs = conn.execute(
                    "SELECT id, picture_id, job_task, started_at, finished_at, error FROM job_history WHERE picture_id IS NOT NULL ORDER BY started_at",
                ).fetchall()
                # there should be 4 jobs, 3 failures and a job ok
                assert jobs and len(jobs) == 4

                for job in jobs:
                    assert job["job_task"] == "prepare"
                    assert job["started_at"].date() == date.today()
                    assert job["finished_at"].date() == date.today()
                    assert job["started_at"] < job["finished_at"]
                    assert job["picture_id"] == pic1_id

                for job in jobs[0:2]:
                    assert job["error"] == "oh no! pic process failed"

                assert jobs[3]["error"] is None

                # wait for the sequence to be finalized
                s = conftest.waitForAllJobsDone(app)
                jobs = conn.execute(
                    "SELECT id, sequence_id, job_task, started_at, finished_at, error FROM job_history WHERE sequence_id IS NOT NULL AND finished_at IS NOT NULL ORDER BY started_at",
                ).fetchall()
                # there should be 1 finalization job
                assert jobs and len(jobs) == 1
                assert jobs[0]["job_task"] == "finalize"
                assert jobs[0]["started_at"].date() == date.today()
                assert jobs[0]["finished_at"].date() == date.today()
                assert jobs[0]["started_at"] < jobs[0]["finished_at"]
                assert jobs[0]["sequence_id"] == seq_id

                # and no jobs should be in queue
                pic_to_process = conn.execute("SELECT picture_id from job_queue").fetchall()
                assert pic_to_process == []

            # we should also have those info via the geovisio_status route
            s = client.get(f"{seq_location}/geovisio_status")
            assert s and s.status_code == 200 and s.json
            assert s.json["status"] == "ready"  # sequence should be ready
            assert len(s.json["items"]) == 1
            item = s.json["items"][0]

            processed_at = item.pop("processed_at")
            assert processed_at.startswith(date.today().isoformat())

            assert item == {
                "id": str(pic1_id),
                "nb_errors": 3,
                "processing_in_progress": False,
                "rank": 1,
                "status": "ready",
            }


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_process_picture_with_retry_ko(datafiles, dburl, tmp_path, monkeypatch):
    """
    If picture process raises a RecoverableException, the job should be retried a certain number of times, but if it continue to fail, it should stop and mark the process as error
    """
    from geovisio.workers import runner_pictures

    def new_processPictureFiles(dbJob, _config):
        """Mock function that always raises an exception"""
        raise runner_pictures.RecoverableProcessException("oh no! pic process failed")

    monkeypatch.setattr(runner_pictures, "processPictureFiles", new_processPictureFiles)

    def start_worker():
        start_background_worker(
            dburl,
            tmp_path,
            config={
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "PICTURE_PROCESS_NB_RETRIES": 2,
            },
        )

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
            "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
        }
    ) as app:
        with app.test_client() as client:
            seq_location = conftest.createSequence(client, "a_sequence")
            pic1_id = UUID(conftest.uploadPicture(client, seq_location, open(datafiles / "1.jpg", "rb"), "1.jpg", 1))

            pics = conftest.getPictureIds(dburl)[0].pictures
            assert not os.path.exists(pics[0].get_permanent_file(datafiles))
            assert not os.path.exists(pics[0].get_derivate_dir(datafiles))
            assert os.path.exists(pics[0].get_temporary_file(datafiles))

            start_worker()

            def wanted_state(seq):
                pic_status = {p["rank"]: p["status"] for p in seq.json["items"]}
                return pic_status == {1: "broken"}

            s = conftest.waitForSequenceState(client, seq_location, wanted_state)

            # check that all jobs have been correctly persisted in the database
            with psycopg.connect(dburl, row_factory=dict_row) as conn:
                jobs = conn.execute(
                    "SELECT id, picture_id, job_task, started_at, finished_at, error FROM job_history ORDER BY started_at"
                ).fetchall()
                # 2 retry means there should be 3 jobs, 3 failures
                assert jobs and len(jobs) == 3

                for job in jobs:
                    assert job["job_task"] == "prepare"
                    assert job["started_at"].date() == date.today()
                    assert job["finished_at"].date() == date.today()
                    assert job["started_at"] < job["finished_at"]
                    assert job["picture_id"] == pic1_id
                    assert job["error"] == "oh no! pic process failed"

                # and no jobs should be in queue
                pic_to_process = conn.execute("SELECT picture_id from job_queue").fetchall()
                assert pic_to_process == []

            # we should also have those info via the geovisio_status route
            s = client.get(f"{seq_location}/geovisio_status")
            assert s and s.status_code == 200 and s.json
            assert s.json["status"] == "waiting-for-process"  # sequence should be waiting for a valid picture
            assert len(s.json["items"]) == 1
            item = s.json["items"][0]

            processed_at = item.pop("processed_at")
            assert processed_at.startswith(date.today().isoformat())

            assert item == {
                "id": str(pic1_id),
                "nb_errors": 3,
                "processing_in_progress": False,
                "process_error": "oh no! pic process failed",
                "rank": 1,
                "status": "broken",
            }
            assert not os.path.exists(pics[0].get_permanent_file(datafiles))
            assert not os.path.exists(pics[0].get_derivate_dir(datafiles))
            # at the end, we kept the file in the temporary storage
            assert os.path.exists(pics[0].get_temporary_file(datafiles))


def almost_equals(dt, expected):
    assert abs(dt - expected) < timedelta(minutes=1), f"dt = {dt}, expected = {expected}"


def test_get_next_periodic_task_dt(dburl, tmp_path):
    with (
        create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "PICTURE_PROCESS_REFRESH_CRON": "59 23 * * *",  # refresh stats every day at 23:59
            }
        ) as worker,
        psycopg.connect(dburl, autocommit=True) as conn,
    ):
        # set that a db refresh has never been done
        conn.execute("UPDATE refresh_database SET refreshed_at = NULL")

        worker = runner_pictures.PictureProcessor(app=worker, stop=True)
        next_task = worker.get_next_periodic_task_dt(conn)
        current_time = datetime.now(timezone.utc)

        # since refresh has never been done, refresh should be done around now
        almost_equals(current_time, next_task)

        # we ask the worker to check task, task should be run
        worker.check_periodic_tasks()

        r = conn.execute("SELECT refreshed_at FROM refresh_database").fetchone()
        assert r
        almost_equals(r[0], current_time)

        # next task, should be at 23:59 today
        next_task = worker.get_next_periodic_task_dt(conn)
        expected = datetime.combine(datetime.today(), time=time(hour=23, minute=59), tzinfo=timezone.utc)
        almost_equals(next_task, expected)


@conftest.SEQ_IMGS
@conftest.SEQ_IMG_BLURRED
def test_dispatch_retry(datafiles, dburl, tmp_path, monkeypatch, defaultAccountID):
    """If an upload_set dispatch fails, it is retried"""
    from geovisio.utils import upload_set

    cpt = 0

    def new_dispath(conn, upload_set_id):
        """Mock function that always raises an exception"""
        nonlocal cpt
        cpt += 1
        if cpt <= 2:
            raise Exception("oh no! upload set dispatch failed")

    monkeypatch.setattr(upload_set, "dispatch", new_dispath)

    with (
        create_test_app(
            {
                "TESTING": True,
                "API_BLUR_URL": conftest.MOCK_BLUR_API,
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "PICTURE_PROCESS_THREADS_LIMIT": 0,  # we run the API without any picture worker, so no pictures will be processed
            }
        ) as app,
        db.cursor(app, row_factory=dict_row) as cur,
    ):

        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()["id"]
        # setting the upload set as completed will add the dispatch task to the queue
        cur.execute("UPDATE upload_sets SET completed = True WHERE id = %(id)s", {"id": upload_id})

        jobs = cur.execute("SELECT task, upload_set_id, nb_errors FROM job_queue").fetchall()
        assert jobs == [{"task": "dispatch", "upload_set_id": upload_id, "nb_errors": 0}]

        worker = runner_pictures.PictureProcessor(app=app, stop=True)
        worker.process_jobs()

        jobs = cur.execute("SELECT task, upload_set_id, nb_errors FROM job_queue").fetchall()
        assert jobs == []

        # the job should have failed twice and be ok the third attempt
        job_history = cur.execute("SELECT upload_set_id, job_task, error FROM job_history ORDER BY finished_at").fetchall()
        assert job_history == [
            {"upload_set_id": upload_id, "job_task": "dispatch", "error": "Upload set dispatch error: oh no! upload set dispatch failed"},
            {"upload_set_id": upload_id, "job_task": "dispatch", "error": "Upload set dispatch error: oh no! upload set dispatch failed"},
            {"upload_set_id": upload_id, "job_task": "dispatch", "error": None},
        ]


@pytest.mark.parametrize(
    ("raw_detections", "expected_error", "as_multipart_response"),
    [
        ('{"info": [{"class": "sign", "confidence": 0.9, "xywh": [0, 0, 100, 100]}]}', None, True),
        ('{"info": [{"class": "sign", "confidence": 0.9, "xywh": [0, 0, 100, 100]}]}', None, False),
        (
            # real example from sgblur
            '{"info": [{"class": "sign", "confidence": 0.664, "xywh": [2064, 2240, 64, 80], "bbox": [2078, 2245, 2116, 2291]}, {"class": "sign", "confidence": 0.404, "xywh": [2960, 2176, 48, 80], "bbox": [2971, 2190, 3002, 2236]}, {"class": "face", "confidence": 0.485, "xywh": [2704, 2096, 144, 160], "bbox": [2716, 2100, 2837, 2231]}], "salt": "56e83230-4e88-4700-9311-18a8197088bb"}',
            None,
            False,
        ),
        ("pouet", "Impossible to parse blurring metadata API response", False),
        ("pouet", "Impossible to parse blurring metadata API response", True),
        (None, None, False),
        (
            '{"some_json": "with a weird structure"}',
            None,
            False,
        ),  # we do not do any structure validation on the detections, we store them as we reveive them, we just need them to be valid json
        (
            """{
    "annotations": [
        {
            "shape": [144, 96, 64, 64],
            "semantics": [
                {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                {"key": "osm|traffic_sign", "value": "yes"}
            ]
        }
    ],
    "blurring_id": "56e83230-4e88-4700-9311-18a8197088bb",
    "some_other_metadata": "blabla"
}""",
            None,
            True,
        ),
    ],
)
@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_blur_detections(
    requests_mock, caplog, datafiles, tmp_path, fsesUrl, dburl, bobAccountToken, raw_detections, expected_error, as_multipart_response
):
    conftest.mockBlurringAPIPost(datafiles, requests_mock, detections=raw_detections, as_multipart_response=as_multipart_response)

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "SECRET_KEY": "a very secret key",
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
        }
    ) as app:

        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]}, jwtToken=bobAccountToken())
        conftest.waitForAllJobsDone(app)

        blurring_id = db.fetchone(app, "SELECT blurring_id FROM pictures limit 1")[0]
        # the blurring_id should not have been kept as we do not ask to store unblurred parts
        assert blurring_id is None
        if expected_error:
            assert expected_error in caplog.text
            return

        if not raw_detections:
            return
        expected_detections = json.loads(raw_detections)

        expected_annotations = expected_detections.pop("annotations", [])

        # the tags should have been added as semantics
        if not expected_annotations:
            return
        seq, pic = conftest.getFirstPictureIds(dburl)
        item = app.test_client().get(f"/api/collections/{seq}/items/{pic}")
        assert item.status_code == 200, item.text
        item_annotations = item.json["properties"]["annotations"]
        for a in item_annotations:
            a.pop("id")  # we remove ids before comparison
        for a in expected_annotations:
            # and we change the shape since we always store a polygon in the db (not a bbox)
            bbox = a["shape"]
            a["shape"] = {
                "coordinates": [[[bbox[0], bbox[1]], [bbox[2], bbox[1]], [bbox[2], bbox[3]], [bbox[0], bbox[3]], [bbox[0], bbox[1]]]],
                "type": "Polygon",
            }
        assert item_annotations == expected_annotations


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_blur_detections_shape_outside_range(
    requests_mock, caplog, datafiles, tmp_path, fsesUrl, dburl, bobAccountToken
):
    """having a shape outside of the boundary of the image should just trigger a warning (and the annotation should be skipped)"""
    conftest.mockBlurringAPIPost(
        datafiles,
        requests_mock,
        detections="""{
    "annotations": [
        {
            "shape": [144000, 96000, 640000, 640000],
            "semantics": [{"key": "osm|traffic_sign", "value": "yes"}]
        }
    ],
    "blurring_id": "56e83230-4e88-4700-9311-18a8197088bb"
}""",
        as_multipart_response=True,
    )

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "SECRET_KEY": "a very secret key",
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
        }
    ) as app:

        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]}, jwtToken=bobAccountToken())
        conftest.waitForAllJobsDone(app)

        blurring_id = db.fetchone(app, "SELECT blurring_id FROM pictures limit 1")[0]
        expected_error = """Annotation shape is outside the range of the picture: {\'details\': "Annotation shape\'s coordinates should be in pixel, between [0, 0] and [5760, 2880]", \'value\': {\'x\': 144000, \'y\': 96000}}"""
        # error should be stored, but as a warning since it should not stop the picture processing
        assert db.fetchall(app, "SELECT warning FROM job_history where picture_id is not null") == [(expected_error,)]
        assert expected_error in caplog.text


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_blur_detections_on_rebluring(
    requests_mock,
    datafiles,
    fsesUrl,
    dburl,
    bobAccountToken,
):
    """If a picture is blurring multiple times (for example if a /prepare has been called again), we do not store the detections twice"""
    blurring_detections = {
        "annotations": [
            {
                "shape": [144, 96, 64, 64],
                "semantics": [
                    {"key": "osm|traffic_sign", "value": "yes"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                ],
            }
        ],
        "blurring_id": "56e83230-4e88-4700-9311-18a8197088bb",
        "service_name": "SGBlur",
        "some_other_metadata": "blabla",
    }
    conftest.mockBlurringAPIPost(datafiles, requests_mock, detections=json.dumps(blurring_detections), as_multipart_response=True)

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "SECRET_KEY": "a very secret key",
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_KEEP_UNBLURRED_PARTS": True,
        }
    ) as app:

        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]}, jwtToken=bobAccountToken())
        conftest.waitForAllJobsDone(app)
        seq, pic = conftest.getFirstPictureIds(dburl)

        blur_id = db.fetchone(app, "SELECT blurring_id FROM pictures limit 1")[0]
        assert blur_id == "56e83230-4e88-4700-9311-18a8197088bb"

        item = app.test_client().get(f"/api/collections/{seq}/items/{pic}")
        assert item.status_code == 200, item.text
        item_annotations = item.json["properties"]["annotations"]
        for a in item_annotations:
            a.pop("id")  # we remove ids before comparison

        assert item_annotations == [
            {
                "shape": {"coordinates": [[[144, 96], [64, 96], [64, 64], [144, 64], [144, 96]]], "type": "Polygon"},
                "semantics": [
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.313"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.1.0"},
                    {"key": "osm|traffic_sign", "value": "yes"},
                ],
            }
        ]

        # let's say someone added some semantic tags on the picture, they should be preserved
        response = app.test_client().post(
            f"/api/collections/{seq}/items/{pic}/annotations",
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
            json={
                "shape": [2, 2, 20, 20],
                "semantics": [{"key": "a very important tag", "value": "🔐"}],
            },
        )
        assert response.status_code == 200

        # and now if we blur again the picture, we should only have the new detections

        # for the test, the bluring api return another annotation on the second call, the detection model has been updated
        new_bluring_id = "12345678-4e88-4700-9311-18a8197088bb"
        blurring_detections = {
            "annotations": [
                {
                    "shape": [144, 96, 64, 64],
                    "semantics": [
                        {"key": "osm|traffic_sign", "value": "yes"},
                        {"key": "a cool new tag", "value": "yes"},
                        {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.613"},
                        {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.2.0"},
                    ],
                },
                {
                    "shape": [244, 100, 50, 50],
                    "semantics": [
                        {"key": "osm|traffic_sign", "value": "yes"},
                        {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.5"},
                        {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.2.0"},
                    ],
                },
            ],
            "blurring_id": new_bluring_id,
            "service_name": "SGBlur",  # w- but the same service_name, it is used to cleanup the old semantics
            "some_other_metadata": "another blabla",
        }
        conftest.mockBlurringAPIPost(datafiles, requests_mock, detections=json.dumps(blurring_detections), as_multipart_response=True)

        # we call for another preparation of the picture, with a blurring
        r = app.test_client().post(f"/api/collections/{seq}/items/{pic}/prepare")
        assert r.status_code == 202
        conftest.waitForAllJobsDone(app)

        assert db.fetchone(app, "SELECT blurring_id FROM pictures limit 1")[0] == new_bluring_id

        item = app.test_client().get(f"/api/collections/{seq}/items/{pic}")
        assert item.status_code == 200, item.text
        item_annotations = conftest.cleanup_annotations(item.json["properties"]["annotations"])

        assert item_annotations == [
            {
                "shape": {"coordinates": [[[2, 2], [20, 2], [20, 20], [2, 20], [2, 2]]], "type": "Polygon"},
                "semantics": [{"key": "a very important tag", "value": "🔐"}],
            },
            {
                "shape": {"coordinates": [[[144, 96], [64, 96], [64, 64], [144, 64], [144, 96]]], "type": "Polygon"},
                "semantics": [
                    {"key": "a cool new tag", "value": "yes"},
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.613"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.2.0"},
                    {"key": "osm|traffic_sign", "value": "yes"},
                ],
            },
            {
                "shape": {"coordinates": [[[244, 100], [50, 100], [50, 50], [244, 50], [244, 100]]], "type": "Polygon"},
                "semantics": [
                    {"key": "detection_confidence[osm|traffic_sign=yes]", "value": "0.5"},
                    {"key": "detection_model[osm|traffic_sign=yes]", "value": "SGBlur-yolo11n/0.2.0"},
                    {"key": "osm|traffic_sign", "value": "yes"},
                ],
            },
        ]


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_keep_unblured_parts(requests_mock, datafiles, fsesUrl, dburl, bobAccountToken):
    """If the service is configured to ask for the blurring to keep unblurred parts, the blur should have the `keep=1` query parameter"""
    blurring_detections = {
        "annotations": [],
        "blurring_id": "56e83230-4e88-4700-9311-18a8197088bc",
        "service_name": "SGBlur",
        "some_other_metadata": "blabla",
    }
    conftest.mockBlurringAPIPost(
        datafiles, requests_mock, detections=json.dumps(blurring_detections), as_multipart_response=True, keep_blurring=True
    )

    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS",
            "SECRET_KEY": "a very secret key",
            "API_BLUR_URL": conftest.MOCK_BLUR_API,
            "PICTURE_PROCESS_KEEP_UNBLURRED_PARTS": True,
        }
    ) as app:
        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]}, jwtToken=bobAccountToken())
        conftest.waitForAllJobsDone(app)

        # and the blurring_id should be stored
        assert db.fetchone(app, "SELECT blurring_id FROM pictures limit 1")[0] == "56e83230-4e88-4700-9311-18a8197088bc"


@conftest.SEQ_IMG
def test_processPictureFiles_read_metadata_no_file_reread(datafiles, app, dburl, monkeypatch, tmp_path):
    """We can add pictures to the job_queue to reread their metadata.

    The tag reader is mocked, and the first 2 times will return the same results, and a different at the 3rd attempt
    (mocking an update of the library)"""
    global attempt_idx
    attempt_idx = 0

    def mocked_getPictureMetadata(exif, width, height, lang="en"):
        global attempt_idx
        attempt_idx += 1
        if attempt_idx <= 2:
            return reader.GeoPicTags(
                lat=49.00688961988304,
                lon=1.9191854417991367,
                ts=datetime(2021, 7, 29, 11, 16, 54, tzinfo=timezone.utc),
                heading=349,
                type="equirectangular",
                make="GoPro",
                model="Max",
                focal_length=3.0,
                crop=None,
                exif={},
                tagreader_warnings=[],
                altitude=93,
                pitch=0.0,
                roll=0.0,
                yaw=0.0,
                ts_by_source=reader.TimeBySource(gps=datetime(2021, 7, 29, 11, 16, 54, 0), camera=datetime(2021, 7, 29, 11, 16, 42, 0)),
                sensor_width=6.17,
                field_of_view=360,
                gps_accuracy=4,
            )
        else:
            # at second call, `heading`, `lon`, `roll`, `model` and `gps_accuracy` are updated
            return reader.GeoPicTags(
                lat=49.00688961988304,
                lon=2,
                ts=datetime(2021, 7, 29, 11, 16, 54, tzinfo=timezone.utc),
                heading=300,
                type="equirectangular",
                make="GoPro",
                model="Max2",
                focal_length=3.0,
                crop=None,
                exif={},
                tagreader_warnings=[],
                altitude=93,
                pitch=0.0,
                roll=12.0,
                yaw=0.0,
                ts_by_source=reader.TimeBySource(gps=datetime(2021, 7, 29, 11, 16, 54, 0), camera=datetime(2021, 7, 29, 11, 16, 42, 0)),
                sensor_width=6.17,
                field_of_view=360,
                gps_accuracy=4,
            )

    monkeypatch.setattr(reader, "getPictureMetadata", mocked_getPictureMetadata)

    with app.test_client() as client, db.conn(app) as conn, conn.cursor(row_factory=dict_row) as cursor:
        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]})
        conftest.waitForAllJobsDone(app)
        seq_id, pic_id = conftest.getFirstPictureIds(dburl)

        initial_metadata = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading FROM pictures WHERE id = %s", [pic_id]
        ).fetchone()
        initial_col_update = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]

        # we ask for a new read of the metadata
        # nothing should change (since it's the second call to the reader)
        utils.pictures.ask_for_metadata_update(pic_id)
        r = db.fetchall(app, "select * from job_queue")
        assert len(r) == 1

        worker = runner_pictures.PictureProcessor(app=app, stop=True)
        worker.process_jobs()

        jobs = db.fetchall(
            app,
            "SELECT job_task, picture_id, error, args FROM job_history WHERE picture_id = %s ORDER BY started_at",
            [pic_id],
            row_factory=dict_row,
        )
        assert jobs == [
            {"job_task": "prepare", "picture_id": pic_id, "error": None, "args": None},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": None},
        ]

        metadata_after_first = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading FROM pictures WHERE id = %s", [pic_id]
        ).fetchone()
        col_update_after_first = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]
        assert initial_col_update == col_update_after_first
        assert initial_metadata == metadata_after_first

        # we ask again for a new read of the metadata, this should change some stuff
        utils.pictures.ask_for_metadata_update(pic_id)

        worker = runner_pictures.PictureProcessor(app=app, stop=True)
        worker.process_jobs()

        jobs = db.fetchall(
            app,
            "SELECT job_task, picture_id, args, error FROM job_history WHERE picture_id = %s ORDER BY started_at",
            [pic_id],
            row_factory=dict_row,
        )
        assert jobs == [
            {"job_task": "prepare", "picture_id": pic_id, "error": None, "args": None},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": None},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": None},
        ]

        metadata_after = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading FROM pictures WHERE id = %s", [pic_id]
        ).fetchone()
        col_update_after = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]
        # updated_at should have been updated
        assert col_update_after_first < col_update_after

        assert initial_metadata == metadata_after_first

        assert metadata_after["lon"] != initial_metadata["lon"]
        assert metadata_after["lon"] == 2
        assert metadata_after["heading"] == 300
        assert metadata_after["lat"] == initial_metadata["lat"]
        assert metadata_after["metadata"]["roll"] != initial_metadata["metadata"]["roll"]
        assert metadata_after["metadata"]["model"] != initial_metadata["metadata"]["model"]
        assert metadata_after["gps_accuracy_m"] == 4


@conftest.SEQ_IMG
def test_processPictureFiles_read_metadata_with_file_reread(datafiles, app, dburl, monkeypatch, tmp_path):
    """We can add pictures to the job_queue to reread their metadata with a file read.

    In this test, we'll update the file's metadata, but in reality it will likely be the tag reader that will be updated.
    """

    with app.test_client() as client, db.conn(app) as conn, conn.cursor(row_factory=dict_row) as cursor:
        conftest.app_with_data(app=app, sequences={"seq1": [Path(conftest.FIXTURE_DIR) / "1.jpg"]})
        conftest.waitForAllJobsDone(app)
        seq_id, pic_id = conftest.getFirstPictureIds(dburl)

        # we cheat and fake the fact that the heading was computed, so it should not be overrided
        cursor.execute("UPDATE pictures SET heading_computed = TRUE WHERE id = %s", [pic_id])

        initial_metadata = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading FROM pictures WHERE id = %s", [pic_id]
        ).fetchone()
        initial_col_update = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]

        # we ask for a new read of the metadata
        # nothing should change since we did not update anything
        utils.pictures.ask_for_metadata_update(pic_id, read_file=True)
        r = db.fetchall(app, "select * from job_queue")
        assert len(r) == 1

        worker = runner_pictures.PictureProcessor(app=app, stop=True)
        worker.process_jobs()

        jobs = db.fetchall(
            app,
            "SELECT job_task, picture_id, error, args FROM job_history WHERE picture_id = %s ORDER BY started_at",
            [pic_id],
            row_factory=dict_row,
        )
        assert jobs == [
            {"job_task": "prepare", "picture_id": pic_id, "error": None, "args": None},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": {"read_file": True}},
        ]

        metadata_after_first = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading FROM pictures WHERE id = %s", [pic_id]
        ).fetchone()
        col_update_after_first = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]
        assert initial_col_update == col_update_after_first
        assert initial_metadata == metadata_after_first

        # we update the exif tag on the file
        overrided_dt = datetime(2021, 7, 29, 11, 16, 54, tzinfo=timezone.utc)
        permanent_pic_path = f"{datafiles}/permanent{geovisio.utils.pictures.getHDPicturePath(pic_id)}"
        with open(permanent_pic_path, "rb") as f:
            orig = f.read()
            image_file_upd = writer.writePictureMetadata(
                orig,
                writer.PictureMetadata(capture_time=overrided_dt, latitude=42.2, longitude=4.2, direction=writer.Direction(200)),
            )
        with open(permanent_pic_path, "wb") as f:
            f.write(image_file_upd)

        # we ask again for a new read of the metadata, this should change some stuff
        utils.pictures.ask_for_metadata_update(pic_id, read_file=True)

        worker = runner_pictures.PictureProcessor(app=app, stop=True)
        worker.process_jobs()

        jobs = db.fetchall(
            app,
            "SELECT job_task, picture_id, args, error FROM job_history WHERE picture_id = %s ORDER BY started_at",
            [pic_id],
            row_factory=dict_row,
        )
        assert jobs == [
            {"job_task": "prepare", "picture_id": pic_id, "error": None, "args": None},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": {"read_file": True}},
            {"job_task": "read_metadata", "picture_id": pic_id, "error": None, "args": {"read_file": True}},
        ]

        metadata_after = cursor.execute(
            "SELECT metadata, st_x(geom) as lon, st_y(geom) as lat, ts, gps_accuracy_m, heading, heading_computed FROM pictures WHERE id = %s",
            [pic_id],
        ).fetchone()
        col_update_after = cursor.execute("SELECT updated_at FROM sequences WHERE id = %s", [seq_id]).fetchone()["updated_at"]
        # updated_at should have been updated
        assert col_update_after_first < col_update_after

        assert initial_metadata == metadata_after_first

        assert metadata_after["lon"] == 4.2
        assert metadata_after["lat"] == 42.2
        assert metadata_after["heading"] == initial_metadata["heading"]  # heading has not been updated since it was computed
        assert metadata_after["heading_computed"] == True
        assert metadata_after["ts"] == overrided_dt


@conftest.SEQ_IMG
@conftest.SEQ_IMG_BLURRED
def test_processPictureFiles_with_blurring_rotation(datafiles, dburl, requests_mock, tmp_path, monkeypatch, bobAccountToken):
    """The blurring api can apply a lossless rotation of the pictures, and in those cases, the width/height should be updated
    to match the new size
    """
    requests_mock.post(
        conftest.MOCK_BLUR_API + "/blur/",
        [
            {"body": open(datafiles / "1_blurred.jpg", "rb")},
        ],
    )

    global pic_size_nb_calls
    pic_size_nb_calls = 0

    def new_getPictureSizing(pic_pillow):
        """Mock function, that returns inverted with/height for 1_blurred.jpg"""
        global pic_size_nb_calls
        pic_size_nb_calls += 1

        if pic_size_nb_calls == 1:
            return {"width": pic_pillow.size[0], "height": pic_pillow.size[1], "cols": 8, "rows": 4}
        if pic_size_nb_calls == 2:
            # second call should be the one for the blurred picture
            return {"width": pic_pillow.size[1], "height": pic_pillow.size[0], "cols": 4, "rows": 8}
        raise Exception("We should not call this 3 times")

    monkeypatch.setattr(utils.pictures, "getPictureSizing", new_getPictureSizing)

    with (
        conftest.create_test_app(
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
                "PICTURE_PROCESS_THREADS_LIMIT": 0,  # no background workers, so we can check the metadata before and after processing
            }
        ) as app,
        app.test_client() as client,
    ):
        us_id = conftest.create_upload_set(client, jwtToken=bobAccountToken(), estimated_nb_files=1)

        r = client.post(
            f"/api/upload_sets/{us_id}/files",
            data={
                "file": (datafiles / "1.jpg").open("rb"),
                "override_Exif.Image.Orientation": "6",  # Orientation = 6 means rotated 90°
            },
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        pic_id = r.json["picture_id"]
        initial_width = 5760
        initial_height = 2880

        res = db.fetchone(app, "SELECT metadata, exif FROM pictures WHERE id = %s", [pic_id], row_factory=dict_row)
        assert res and res["exif"]["Exif.Image.Orientation"] == "6"
        assert res["metadata"]["width"] == initial_width
        assert res["metadata"]["height"] == initial_height
        assert res["metadata"]["cols"] == 8
        assert res["metadata"]["rows"] == 4
        assert res["exif"]["Exif.Photo.PixelXDimension"] == str(initial_width)
        assert res["exif"]["Exif.Photo.PixelYDimension"] == str(initial_height)

        runner_pictures.process_next_job(app)

        assert pic_size_nb_calls == 2

        # after process, width/height should be inverted
        res = db.fetchone(app, "SELECT metadata, exif FROM pictures WHERE id = %s", [pic_id], row_factory=dict_row)
        assert res
        assert res["exif"].get("Exif.Image.Orientation") is None
        assert res["metadata"]["width"] == initial_height
        assert res["metadata"]["height"] == initial_width
        assert res["metadata"]["cols"] == 4
        assert res["metadata"]["rows"] == 8
        assert res["exif"]["Exif.Photo.PixelXDimension"] == initial_height
        assert res["exif"]["Exif.Photo.PixelYDimension"] == initial_width
