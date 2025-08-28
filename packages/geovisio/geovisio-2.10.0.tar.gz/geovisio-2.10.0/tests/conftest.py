from datetime import datetime
import json
from uuid import UUID
from PIL import Image, ImageChops, ImageStat
from psycopg.types.json import Jsonb
import pytest
import psycopg
from psycopg.sql import SQL
from psycopg.rows import dict_row
import os
import re
import time
from flask import current_app
import typing
from typing import Dict, List, Any, Optional, TypeAlias
from pathlib import Path
import shutil
from dataclasses import dataclass, field
from contextlib import contextmanager
import functools
import urllib3

from geovisio import create_app, db_migrations, tokens
from geovisio.utils import annotations, filesystems, db, pictures, semantics, upload_set
from geovisio.workers import runner_pictures


@pytest.fixture(scope="session")
def dburl():
    # load test.env file if available
    import dotenv

    dotenv.load_dotenv("test.env")

    db = os.environ["DB_URL"]

    db_migrations.update_db_schema(db, force=True)
    # do a vacuum for the st_extent to work
    with psycopg.connect(db, autocommit=True) as c:
        c.execute("VACUUM ANALYZE pictures")

    return db


def prepare_fs(base_dir):
    fstmp = base_dir / "tmp"
    fstmp.mkdir()
    fspermanent = base_dir / "permanent"
    fspermanent.mkdir()
    fsderivates = base_dir / "derivates"
    fsderivates.mkdir()
    return filesystems.FilesystemsURL(
        tmp="osfs://" + str(fstmp), permanent="osfs://" + str(fspermanent), derivates="osfs://" + str(fsderivates)
    )


@pytest.fixture
def fsesUrl(tmp_path):
    return prepare_fs(tmp_path)


@contextmanager
def create_test_app(config):
    app = create_app(config)

    with app.app_context():
        try:
            yield app
        finally:
            app.pool.close()
            app.background_processor.stop()


@pytest.fixture
def app(dburl, tmp_path, fsesUrl):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "SERVER_NAME": "localhost:5000",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
            "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
            "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
        }
    ) as app:
        yield app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# Code for having at least one sequence in tests
FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")

SEQ_IMG = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "1.jpg"))
SEQ_IMG_FLAT = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "c1.jpg"))
SEQ_IMG_ARTIST = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "e1_artist.jpg"))
SEQ_IMG_CROP = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "crop.jpg"))

SEQ_IMGS = pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "1.jpg"),
    os.path.join(FIXTURE_DIR, "2.jpg"),
    os.path.join(FIXTURE_DIR, "3.jpg"),
    os.path.join(FIXTURE_DIR, "4.jpg"),
    os.path.join(FIXTURE_DIR, "5.jpg"),
)

SEQ_IMGS_FLAT = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "b1.jpg"), os.path.join(FIXTURE_DIR, "b2.jpg"))

SEQ_IMGS_NOHEADING = pytest.mark.datafiles(
    os.path.join(FIXTURE_DIR, "e1.jpg"),
    os.path.join(FIXTURE_DIR, "e2.jpg"),
    os.path.join(FIXTURE_DIR, "e3.jpg"),
    os.path.join(FIXTURE_DIR, "e4.jpg"),
    os.path.join(FIXTURE_DIR, "e5.jpg"),
)

SEQ_IMG_BLURRED = pytest.mark.datafiles(os.path.join(FIXTURE_DIR, "1_blurred.jpg"))
MOCK_BLUR_API = "https://geovisio-blurring.net"


def app_with_data(app, sequences: Dict[str, List[Path]], jwtToken=None):
    with app.app_context():
        with app.test_client() as client:
            for title, pics_path in sequences.items():
                uploadSequenceFromPics(test_client=client, title=title, wait=True, jwtToken=jwtToken, pics=pics_path)

            return client


@pytest.fixture
def initSequenceApp(tmp_path, dburl, fsesUrl, bobAccountToken):
    """Create an App and fill it with data, making 2 sequences if needed, and using the old collections API for upload"""
    seqPath = tmp_path / "seq1"
    seqPath.mkdir()

    @contextmanager
    def fct(datafiles, preprocess=True, blur=False, withBob=False):
        twoSeqs = os.path.isfile(datafiles / "1.jpg") and os.path.isfile(datafiles / "b1.jpg")

        if twoSeqs:
            seq2Path = tmp_path / "seq2"
            seq2Path.mkdir()
            for f in os.listdir(datafiles):
                if f not in ["seq1", "seq2", "1_blurred.jpg", "tmp", "derivates", "permanent"]:
                    os.rename(datafiles / f, (seq2Path if f[0:1] == "b" else seqPath) / re.sub("^[a-z]+", "", f))
        else:
            for f in os.listdir(datafiles):
                if f not in ["seq1", "1_blurred.jpg", "tmp", "derivates", "permanent"]:
                    os.rename(datafiles / f, seqPath / re.sub("^[a-z]+", "", f))
        with create_test_app(
            {
                "TESTING": True,
                "API_BLUR_URL": MOCK_BLUR_API if blur else "",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS" if preprocess else "ON_DEMAND",
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SECRET_KEY": "cest beau la vie",
                "SERVER_NAME": "localhost:5000",
                "API_FORCE_AUTH_ON_UPLOAD": "true" if withBob else None,
            }
        ) as app:
            with app.test_client() as client:
                jwtToken = None
                if withBob:
                    jwtToken = bobAccountToken()

                uploadSequence(client, tmp_path / "seq1", jwtToken=jwtToken)
                if twoSeqs:
                    uploadSequence(client, tmp_path / "seq2", jwtToken=jwtToken)

                yield client

    return fct


@pytest.fixture
def initAppWithData(dburl, fsesUrl, bobAccountToken):
    """Create an app, and fill it with data using the uploadsets APIs"""

    @contextmanager
    def fct(datafiles, preprocess=True, blur=False, withBob=False):
        with create_test_app(
            {
                "TESTING": True,
                "API_BLUR_URL": MOCK_BLUR_API if blur else "",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "PREPROCESS" if preprocess else "ON_DEMAND",
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SECRET_KEY": "cest beau la vie",
                "SERVER_NAME": "localhost:5000",
                "API_FORCE_AUTH_ON_UPLOAD": "true" if withBob else None,
            }
        ) as app:
            with app.test_client() as client:
                jwtToken = None
                if withBob:
                    jwtToken = bobAccountToken()

                upload_files_in_dir(client, datafiles, jwtToken=jwtToken)

                yield client

    return fct


def createSequence(test_client, title, jwtToken=None) -> str:
    headers = {}
    if jwtToken:
        headers["Authorization"] = "Bearer " + jwtToken

    seq = test_client.post(
        "/api/collections",
        headers=headers,
        data={
            "title": title,
        },
    )
    assert seq.status_code < 400
    return seq.headers["Location"]


def uploadPicture(test_client, sequence_location, pic, filename, position, isBlurred=False, jwtToken=None, overrides=None) -> str:
    postData = {"position": position, "picture": (pic, filename)}

    if isBlurred:
        postData["isBlurred"] = "true"

    if overrides:
        postData.update(overrides)

    headers = {}
    if jwtToken:
        headers["Authorization"] = "Bearer " + jwtToken

    picture_response = test_client.post(f"{sequence_location}/items", headers=headers, data=postData, content_type="multipart/form-data")
    assert picture_response.status_code < 400, picture_response.text
    return picture_response.json["id"]


def uploadSequenceFromPics(test_client, title: str, pics: List[Path], wait=True, jwtToken=None):
    seq_location = createSequence(test_client, title, jwtToken=jwtToken)

    for i, p in enumerate(pics):
        uploadPicture(test_client, seq_location, open(p, "rb"), p.name, i + 1, jwtToken=jwtToken)

    if wait:
        waitForSequence(test_client, seq_location)


def uploadSequence(test_client, directory, wait=True, jwtToken=None):
    seq_location = createSequence(test_client, os.path.basename(directory), jwtToken=jwtToken)

    pictures_filenames = sorted([f for f in os.listdir(directory) if re.search(r"\.jpe?g$", f, re.IGNORECASE)])

    for i, p in enumerate(pictures_filenames):
        uploadPicture(test_client, seq_location, open(directory / p, "rb"), p, i + 1, jwtToken=jwtToken)

    if wait:
        waitForSequence(test_client, seq_location)


def upload_files_in_dir(test_client, directory, wait=True, jwtToken=None):
    """Upload all jpg files from a directory to a new upload set"""
    pictures_filenames = sorted([directory / f for f in os.listdir(directory) if re.search(r"\.jpe?g$", f, re.IGNORECASE)])

    upload_files(test_client, pictures_filenames, wait=wait, jwtToken=jwtToken)


@dataclass
class UploadSetIds:
    id: UUID
    pics: Dict[str, UUID]


@dataclass
class PicToUpload:
    path: Path
    additional_data: Dict[str, Any]


def upload_files(test_client, pics: List[Path | PicToUpload], wait=True, jwtToken=None, title: str = None):
    """Upload all jpg files to a new upload set"""

    upload_set_id = create_upload_set(test_client, jwtToken=jwtToken, estimated_nb_files=len(pics))

    ids = UploadSetIds(id=UUID(upload_set_id), pics={})

    for p in pics:
        if isinstance(p, PicToUpload):
            pic_path = p.path
            additional_data = p.additional_data
        else:
            pic_path = p
            additional_data = {}
        r = add_files_to_upload_set(test_client, upload_set_id, pic_path, jwtToken=jwtToken, additional_data=additional_data)
        ids.pics[pic_path.name] = UUID(r["picture_id"])

    if wait:
        waitForUploadSetStateReady(test_client, upload_set_id)

    return ids


def waitForSequence(test_client, seq_location):
    return waitForSequenceState(
        test_client,
        seq_location,
        wanted_state=lambda s: all(p["status"] == "ready" for p in s.json["items"]) and s.json["status"] == "ready",
    )


def waitForSequenceState(test_client, seq_location, wanted_state) -> Dict[str, Any]:
    """
    Wait for a sequence to have a given state
    `wanted_state` should be a function returning true when the sequence state is the one wanted
    """

    def _call_seq_status(test_client, seq_location, wanted_state):
        s = test_client.get(f"{seq_location}/geovisio_status")
        assert s.status_code < 400

        final_state = {p["rank"]: p["status"] for p in s.json["items"]} | {"sequence_status": s.json["status"]}

        return wanted_state(s), final_state

    return waitFor(lambda: _call_seq_status(test_client, seq_location, wanted_state), timeout=10)


def waitForUploadSetState(test_client, upload_set_id, wanted_state, timeout=5) -> Dict[str, Any]:
    """
    Wait for an upload_set to have a given state
    `wanted_state` should be a function returning true when the sequence state is the one wanted
    """

    def _call_upload_set(test_client, upload_set_id, wanted_state):
        s = test_client.get(f"/api/upload_sets/{upload_set_id}")
        assert s.status_code < 400

        return wanted_state(s), s.json

    return waitFor(lambda: _call_upload_set(test_client, upload_set_id, wanted_state), timeout=timeout)


def waitForUploadSetStateReady(test_client, upload_set_id, timeout=5) -> Dict[str, Any]:
    """
    Wait for an upload_set to be ready (dispatched, and all pictures prepared)
    """
    return waitForUploadSetState(test_client, upload_set_id, wanted_state=lambda x: x.json["ready"] is True, timeout=timeout)


def waitFor(function, *, timeout=5) -> Dict[str, Any]:
    """
    Wait for an upload_set to have a given state
    `wanted_state` should be a function returning true when the sequence state is the one wanted
    """
    waiting_time = 0.1
    total_time = 0
    state = {}
    while total_time < timeout:
        stop, state = function()
        if stop:
            return state
        time.sleep(waiting_time)
        total_time += waiting_time
    assert False, f"Wait for has not reached wanted state, final state = {state}"


def waitForAllJobsDone(app, timeout=5):
    def _all_jobs_done():
        from geovisio.utils import db

        jobs = db.fetchall(app, SQL("SELECT * FROM job_queue"))
        return jobs == [], jobs

    waitFor(_all_jobs_done, timeout=timeout)


def start_background_worker(dburl, tmp_path, config, wait=True):
    import threading

    def pic_background_process():
        with create_test_app(config) as worker_app:
            import logging

            logging.info("Running picture worker in test")
            worker = runner_pictures.PictureProcessor(app=worker_app, stop=True)
            worker.process_jobs()
            return

    t = threading.Thread(target=pic_background_process, daemon=True)

    t.start()

    if wait:
        t.join()
    else:
        return t


@pytest.fixture(autouse=True)
def dbCleanup(dburl):
    with psycopg.connect(dburl, options="-c statement_timeout=5000") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """TRUNCATE TABLE sequences, sequences_pictures, pictures, job_queue, pictures_changes, sequences_changes, upload_sets, excluded_areas, pages CASCADE;"""
            )


@pytest.fixture(autouse=True)
def wait_for_jobs_completion(dburl):
    """At end of test, wait a bit for all background jobs to be processed
    We do this by removing all rows from the job queue, and that will be possible only if no worker has locked a given job
    """
    yield
    with psycopg.connect(dburl, options="-c statement_timeout=2000") as conn:
        conn.execute("DELETE FROM job_queue")


@pytest.fixture(autouse=True)
def datafilesCleanup(datafiles):
    yield
    for filename in os.listdir(datafiles):
        file_path = os.path.join(datafiles, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception:
            pass


def get_acccount_id(conn, *, create=False, name=None, is_default=False):
    assert name is not None or is_default
    if is_default:
        assert not create

    with conn.cursor() as cursor:
        params = [name] if name else []
        filter = SQL("name = %s") if name else SQL("is_default = true")
        accountID = cursor.execute(SQL("SELECT id from accounts where {filter}").format(filter=filter), params).fetchone()
        if not accountID and create and name:
            accountID = cursor.execute("INSERT INTO accounts (name) VALUES (%s) RETURNING id", [name]).fetchone()
        assert accountID
        return accountID[0]


@pytest.fixture()
def defaultAccountID(dburl):
    with psycopg.connect(dburl) as conn:
        return get_acccount_id(conn, is_default=True)


@pytest.fixture()
def bobAccountID(dburl):
    with psycopg.connect(dburl) as conn:
        return get_acccount_id(conn, name="bob", create=True)


@pytest.fixture()
def camilleAccountID(dburl):
    with psycopg.connect(dburl) as conn:
        return get_acccount_id(conn, name="camille", create=True)


def _getToken(accountID, dburl):
    with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
        accountToken = cursor.execute("SELECT id FROM tokens WHERE account_id = %s", [accountID]).fetchone()
        assert accountToken
        accountToken = accountToken[0]
        return tokens._generate_jwt_token(accountToken)


@pytest.fixture()
def bobAccountToken(bobAccountID, dburl):
    @functools.cache
    def f():
        return _getToken(bobAccountID, dburl)

    return f


@pytest.fixture()
def camilleAccountToken(camilleAccountID, dburl):
    @functools.cache
    def f():
        return _getToken(camilleAccountID, dburl)

    return f


@pytest.fixture()
def defaultAccountToken(defaultAccountID, dburl):
    @functools.cache
    def f():
        return _getToken(defaultAccountID, dburl)

    return f


def getFirstPictureIds(dburl) -> typing.Tuple[str, str]:
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            p = cursor.execute("SELECT seq_id, pic_id FROM sequences_pictures WHERE rank = 1").fetchone()
            assert p is not None
            return (p[0], p[1])


@dataclass
class Picture(object):
    id: str

    def get_derivate_dir(self, datafiles):
        return os.path.join(datafiles, "derivates", self.id[0:2], self.id[2:4], self.id[4:6], self.id[6:8], self.id[9:])

    def get_permanent_file(self, datafiles):
        return os.path.join(datafiles, "permanent", self.id[0:2], self.id[2:4], self.id[4:6], self.id[6:8], f"{self.id[9:]}.jpg")

    def get_temporary_file(self, datafiles):
        return os.path.join(datafiles, "tmp", self.id[0:2], self.id[2:4], self.id[4:6], self.id[6:8], f"{self.id[9:]}.jpg")


@dataclass
class Sequence(object):
    id: str
    pictures: typing.List[Picture] = field(default_factory=lambda: [])


def getPictureIds(dburl) -> typing.List[Sequence]:
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            pics = cursor.execute("SELECT seq_id, pic_id FROM sequences_pictures ORDER BY rank").fetchall()
            assert pics is not None

            sequences = []
            for seq_id, pic_id in pics:
                s = next((s for s in sequences if s.id == str(seq_id)), None)
                if s is None:
                    s = Sequence(id=str(seq_id))
                    sequences.append(s)
                s.pictures.append(Picture(id=str(pic_id)))

            return sequences


def mockCreateBlurredHDPictureFactory(datafiles):
    """Mock function for pictures.createBlurredHDPicture"""

    def mockCreateBlurredHDPicture(fs, blurApi, pictureBytes, outputFilename, keep_unblured_parts=False):
        with open(datafiles / "1_blurred.jpg", "rb") as f:
            fs.writebytes(outputFilename, f.read())
            return pictures.BlurredPicture(image=Image.open(datafiles / "1_blurred.jpg"))

    return mockCreateBlurredHDPicture


def mockBlurringAPIPost(datafiles, requests_mock, detections=None, as_multipart_response=True, keep_blurring=False):
    with open(datafiles / "1_blurred.jpg", "rb") as mask:
        if as_multipart_response:
            fields = {"image": ("filename", mask.read(), "image/jpeg")}
            if detections:
                fields["metadata"] = ("metadata", detections, {"Content-Type": "application/json"})
            content, content_type = urllib3.encode_multipart_formdata(fields)
            headers = {"Content-Type": content_type}
        else:
            headers = {"Content-Type": "image/jpeg"} | ({"x-sgblur": detections} if detections else {})
            content = mask.read()
        params = "?keep=1" if keep_blurring else ""
        requests_mock.post(f"{MOCK_BLUR_API}/blur/{params}", headers=headers, content=content)


def arePicturesSimilar(pic1, pic2, limit=1):
    """Checks if two images have less than limit % of differences"""
    diff = ImageChops.difference(pic1.convert("RGB"), pic2.convert("RGB"))
    stat = ImageStat.Stat(diff)
    diff_ratio = sum(stat.mean) / (len(stat.mean) * 255) * 100
    return diff_ratio <= limit


STAC_VERSION = "1.0.0"


@pytest.fixture
def no_license_app_client(dburl, fsesUrl):
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
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
                "SECRET_KEY": "a very secret key",
            }
        ) as app,
        app.test_client() as client,
    ):
        yield client


def create_upload_set(client, jwtToken=None, title="some title", **kwargs):
    h = {"Authorization": f"Bearer {jwtToken}"} if jwtToken else {}

    json = {"title": title} | kwargs
    response = client.post(
        "/api/upload_sets",
        json=json,
        headers=h,
    )
    assert response.status_code == 200, response.text
    upload_set_id = response.json["id"]
    assert upload_set_id
    UUID(upload_set_id)  # should be a valid uuid
    return upload_set_id


def add_files_to_upload_set(client, id, file, jwtToken=None, raw_response=False, additional_data=None, headers=None):
    additional_data = additional_data or {}
    headers = headers or {}
    if jwtToken:
        headers["Authorization"] = f"Bearer {jwtToken}"

    response = client.post(
        f"/api/upload_sets/{id}/files",
        data={"file": file.open("rb")} | additional_data,
        headers=headers,
    )
    if raw_response:
        # no check, we let the caller do it
        return response
    assert response.status_code == 202, response.text
    return response.json


def get_upload_set(client, id, token=None, raw_response=False):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    response = client.get(
        f"/api/upload_sets/{id}",
        headers=h,
    )
    if raw_response:
        # no check, we let the caller do it
        return response
    assert response.status_code == 200, response.text
    return response.json


def get_tags_history():
    from flask import current_app

    res = {}
    pic_history = db.fetchall(
        current_app,
        SQL(
            """SELECT picture_id, accounts.name, updates
    FROM pictures_semantics_history
    JOIN accounts ON accounts.id = account_id
    ORDER BY ts ASC"""
        ),
    )
    if pic_history:
        res["pictures"] = pic_history
    seq_history = db.fetchall(
        current_app,
        SQL(
            """SELECT sequence_id, accounts.name, updates
    FROM sequences_semantics_history
    JOIN accounts ON accounts.id = account_id
    ORDER BY ts ASC"""
        ),
    )
    if seq_history:
        res["sequences"] = seq_history

    return res


TestTag: TypeAlias = str


TAG_REGEXP = re.compile(r"(?P<key>.+)=(?P<value>[^=]+)")


def tag_to_action(t: TestTag) -> semantics.SemanticTagUpdate:
    """To ease tests writing, tags are added in the form key=value"""
    key, value = TAG_REGEXP.search(t).groups()
    return semantics.SemanticTagUpdate(key=key, value=value, action=semantics.TagAction.add)


@dataclass
class TAnnotation:
    shape: List[int] = field(default_factory=lambda: [0, 0, 1, 1])
    semantics: List[TestTag] = field(default_factory=lambda: [])


@dataclass
class PictureToInsert:
    ts: datetime = datetime(year=2024, month=7, day=21, hour=10)
    lon: float = 12
    lat: float = 42
    type: str = "flat"
    heading: float = 0
    capture_time: datetime = datetime(year=2023, month=7, day=21, hour=10)
    original_file_name: str = "1.jpg"
    width: int = 5760
    height: int = 4320
    original_content_md5 = UUID("5726ea34eb5750af7a78a73ad966cf86")
    exif = {}
    gps_accuracy_m = 16
    semantics: List[TestTag] = field(default_factory=lambda: [])
    annotations: List[TAnnotation] = field(default_factory=lambda: [])


@dataclass
class SequenceToInsert(object):
    pictures: typing.List[PictureToInsert] = field(default_factory=lambda: [])
    title: str = "sequence title"
    semantics: List[TestTag] = field(default_factory=lambda: [])


@dataclass
class UploadSetToInsert(object):
    sequences: typing.List[SequenceToInsert] = field(default_factory=lambda: [])
    account_id: Optional[UUID] = None
    semantics: List[TestTag] = field(default_factory=lambda: [])


@dataclass
class ModelToInsert(object):
    upload_sets: typing.List[UploadSetToInsert] = field(default_factory=lambda: [])


def insert_db_pic(cur, upload_set_id: UUID, account_id: UUID, pic: PictureToInsert):
    pic_id = cur.execute(
        """INSERT INTO pictures (ts, heading, metadata, geom, account_id, exif, original_content_md5, upload_set_id, gps_accuracy_m, status)
    VALUES (%(ts)s, %(heading)s, %(metadata)s, ST_SetSRID(ST_MakePoint(%(lat)s, %(lon)s), 4326), %(account_id)s,%(exif)s, %(original_content_md5)s, %(upload_set_id)s, %(gps_accuracy_m)s, %(status)s)
    RETURNING id""",
        {
            "ts": pic.ts.isoformat(),
            "account_id": account_id,
            "upload_set_id": upload_set_id,
            "lon": pic.lon,
            "lat": pic.lat,
            "heading": pic.heading,
            "exif": Jsonb(pic.exif),
            "original_content_md5": pic.original_content_md5,
            "gps_accuracy_m": pic.gps_accuracy_m,
            "metadata": Jsonb(
                {
                    "type": pic.type,
                    "width": pic.width,
                    "height": pic.height,
                    "ts": pic.capture_time.isoformat(),
                    "originalFileName": pic.original_file_name,
                    "originalFileSize": 12,
                }
            ),
            "status": "ready",
        },
    ).fetchone()[0]

    if pic.semantics:
        semantics.update_tags(
            cur,
            semantics.Entity(type=semantics.EntityType.pic, id=pic_id),
            account=account_id,
            actions=[tag_to_action(t) for t in pic.semantics],
        )
    for a in pic.annotations:
        annotations.creation_annotation(
            annotations.AnnotationCreationParameter(
                account_id=account_id, picture_id=pic_id, shape=a.shape, semantics=[tag_to_action(t) for t in a.semantics]
            ),
            cur.connection,
        )
    return pic_id


def insert_db_model(model: ModelToInsert):
    """Import a fake model into the database.

    This should be used in tests that do not really need associated pictures, only the database model. This should speed up tests a lot compared to uploading pictures.
    """
    from flask import current_app
    from geovisio.utils import sequences

    with db.conn(current_app) as conn, conn.cursor() as cur:
        for us in model.upload_sets:
            if us.account_id is None:
                us.account_id = get_acccount_id(conn, is_default=True)
            assert us.account_id
            upload_id = cur.execute(
                "INSERT INTO upload_sets (title, account_id) VALUES (%(title)s, %(account)s) RETURNING id",
                {"title": "some title", "account": us.account_id},
            ).fetchone()[0]

            if us.semantics:
                semantics.update_tags(
                    cur,
                    semantics.Entity(type=semantics.EntityType.upload_set, id=upload_id),
                    account=us.account_id,
                    actions=[tag_to_action(t) for t in us.semantics],
                )

            for seq in us.sequences:
                seq_id = sequences.createSequence({"title": seq.title}, accountId=us.account_id)

                if seq.semantics:
                    semantics.update_tags(
                        cur,
                        semantics.Entity(type=semantics.EntityType.seq, id=seq_id),
                        account=us.account_id,
                        actions=[tag_to_action(t) for t in seq.semantics],
                    )

                upload_set.copy_upload_set_semantics_to_sequence(cur, upload_id, seq_id)

                pics_id = []
                for i, pic in enumerate(seq.pictures, start=1):
                    pic_id = insert_db_pic(cur, upload_set_id=upload_id, account_id=us.account_id, pic=pic)
                    pics_id.append(pic_id)

                    cur.execute("INSERT INTO sequences_pictures (seq_id, rank, pic_id) VALUES (%s, %s, %s)", [seq_id, i, pic_id])
                cur.execute("UPDATE sequences SET status = 'ready' WHERE id = %s", [seq_id])


def is_valid_datetime(dt):
    from dateutil import parser

    return parser.parse(dt)


def decode_session_cookie(cookie):
    """Decode a Flask cookie."""
    from itsdangerous import base64_decode
    import zlib

    compressed = False
    if cookie.startswith("."):
        compressed = True
        cookie = cookie[1:]

    data = cookie.split(".")[0]

    data = base64_decode(data)
    if compressed:
        data = zlib.decompress(data)

    cookie = data.decode("utf-8")
    return json.loads(cookie)


def cleanup_annotations(a):
    a.sort(key=lambda a: a["shape"]["coordinates"])
    for b in a:
        i = b.pop("id")  # and we do not want to compare the id, we just want them to be uuid
        UUID(i)
    return a


def get_job_history(with_time: bool = False):
    """Get all job history.
    Provide with_time if you want start/finishe time, but it will be more difficult to assert equality on this"""
    jobs = db.fetchall(
        current_app,
        f"SELECT job_task, picture_id, sequence_id, upload_set_id, picture_to_delete_id, error{', started_at::time, finished_at::time' if with_time else ''} FROM job_history ORDER BY started_at",
        row_factory=dict_row,
    )
    return [{k: v for k, v in j.items() if v is not None} for j in jobs]
