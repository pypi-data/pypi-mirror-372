from datetime import datetime, timezone
from uuid import UUID
import uuid
from flask import current_app
import pytest
from geovisio.errors import InvalidAPIUsage
from geovisio.utils import db, sequences
from geovisio.utils import upload_set
from psycopg.sql import SQL
from psycopg.types.json import Jsonb
from psycopg.rows import dict_row
from geovisio.utils.extent import TemporalExtent, Temporal


def test_get_upload_set(client, defaultAccountID):
    with db.cursor(current_app) as cur:
        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()[0]
        pic_id = cur.execute(
            """INSERT INTO pictures (ts, geom, account_id, upload_set_id)
VALUES (%s, ST_SetSRID(ST_MakePoint(0, 0), 4326), %s, %s)
RETURNING id""",
            [datetime(year=2024, month=7, day=21, hour=10).isoformat(), defaultAccountID, upload_id],
        ).fetchone()[0]

        u = upload_set.get_upload_set(upload_id)
        assert u

        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 1
        assert u.associated_collections == []
        assert u.items_status == upload_set.AggregatedStatus(prepared=0, preparing=0, broken=0, not_processed=1, rejected=0)

        # we add the picture in a collection
        seq_id = sequences.createSequence({"title": "plop"}, defaultAccountID)
        cur.execute("INSERT INTO sequences_pictures (seq_id, pic_id, rank) VALUES (%s, %s, 1)", [seq_id, pic_id])

        u = upload_set.get_upload_set(upload_id)
        assert u
        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 1
        assert u.associated_collections == [
            upload_set.AssociatedCollection(
                id=seq_id,
                nb_items=1,
                status="waiting-for-process",
                extent=TemporalExtent(
                    temporal=Temporal(
                        interval=[
                            [
                                datetime(2024, 7, 21, 10, 0, tzinfo=timezone.utc),
                                datetime(2024, 7, 21, 10, 0, tzinfo=timezone.utc),
                            ]
                        ]
                    ),
                ),
                title="plop",
                items_status=upload_set.AggregatedStatus(prepared=0, preparing=0, broken=0, not_processed=1),
            )
        ]
        assert u.items_status == upload_set.AggregatedStatus(prepared=0, preparing=0, broken=0, not_processed=1, rejected=0)


def test_get_upload_set_status(client, defaultAccountID):
    """Add 5 pictures to an upload set, and check that the status is correct during different stages of the upload"""
    with db.cursor(current_app) as cur:
        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()[0]

        # at first, empty upload set
        u = upload_set.get_upload_set(upload_id)
        assert u
        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 0
        assert u.associated_collections == []
        assert u.items_status == upload_set.AggregatedStatus(prepared=0, preparing=0, broken=0, not_processed=0, rejected=0)

        pics_id = []
        for i in range(5):
            pic_id = cur.execute(
                """INSERT INTO pictures (ts, geom, account_id, upload_set_id)
    VALUES (%(ts)s, ST_SetSRID(ST_MakePoint(0, %(lon)s), 4326), %(account_id)s, %(upload_set_id)s)
    RETURNING id""",
                {
                    "ts": datetime(year=2024, month=7, day=21, hour=10 + i).isoformat(),
                    "account_id": defaultAccountID,
                    "upload_set_id": upload_id,
                    "lon": i,
                },
            ).fetchone()[0]
            pics_id.append(pic_id)

        u = upload_set.get_upload_set(upload_id)
        assert u

        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 5
        assert u.associated_collections == []
        assert u.items_status == upload_set.AggregatedStatus(prepared=0, preparing=0, broken=0, not_processed=5, rejected=0)

        # We mark 1 picture as broken, 2 as processed, and we add one non terminated job in job_history (and one pic is not processed)
        cur.execute("UPDATE pictures SET preparing_status = 'broken' WHERE id = %s", [pics_id[0]])
        cur.execute("UPDATE pictures SET preparing_status = 'prepared' WHERE id in (%s, %s)", [pics_id[1], pics_id[2]])
        history = [
            {
                "pic_id": pics_id[0],
                "started_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "finished_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "error": "ho no something went wrong",
            },
            {
                "pic_id": pics_id[1],
                "started_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "finished_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "error": None,
            },
            {
                "pic_id": pics_id[2],
                "started_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "finished_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "error": None,
            },
            {
                "pic_id": pics_id[3],
                "started_at": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
                "finished_at": None,
                "error": None,
            },
        ]
        for h in history:
            cur.execute(
                "INSERT INTO job_history (job_task, picture_id, started_at, finished_at, error) VALUES ('prepare', %(pic_id)s, %(started_at)s, %(finished_at)s, %(error)s)",
                h,
            )

        u = upload_set.get_upload_set(upload_id)
        assert u

        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 5
        assert u.associated_collections == []
        # Note: the picture being processed is counted in the 'preparing' and in the 'not-processed'
        assert u.items_status == upload_set.AggregatedStatus(prepared=2, preparing=1, broken=1, not_processed=2, rejected=0)

        # we add the pictures in 2 different collections,
        seq1_id = sequences.createSequence({"title": "plop"}, defaultAccountID)
        seq2_id = sequences.createSequence({"title": "plop2"}, defaultAccountID)
        for i, p in enumerate(pics_id):
            col = seq1_id if i < 3 else seq2_id
            cur.execute("INSERT INTO sequences_pictures (seq_id, pic_id, rank) VALUES (%s, %s, %s)", [col, p, i])

        u = upload_set.get_upload_set(upload_id)
        assert u
        assert u.id == upload_id
        assert u.title == "some title"
        assert u.account_id == defaultAccountID
        assert u.estimated_nb_files is None
        assert u.nb_items == 5

        assert len(u.associated_collections) == 2
        assert sorted(u.associated_collections, key=lambda x: x.id) == sorted(
            [
                upload_set.AssociatedCollection(
                    id=seq1_id,
                    nb_items=3,
                    status="waiting-for-process",
                    extent=TemporalExtent(
                        temporal=Temporal(
                            interval=[
                                [
                                    datetime(2024, 7, 21, 10, 0, tzinfo=timezone.utc),
                                    datetime(2024, 7, 21, 12, 0, tzinfo=timezone.utc),
                                ]
                            ]
                        ),
                    ),
                    title="plop",
                    items_status=upload_set.AggregatedStatus(prepared=2, preparing=0, broken=1, not_processed=0),
                ),
                upload_set.AssociatedCollection(
                    id=seq2_id,
                    nb_items=2,
                    status="waiting-for-process",
                    extent=TemporalExtent(
                        temporal=Temporal(
                            interval=[
                                [
                                    datetime(2024, 7, 21, 13, 0, tzinfo=timezone.utc),
                                    datetime(2024, 7, 21, 14, 0, tzinfo=timezone.utc),
                                ]
                            ]
                        ),
                    ),
                    title="plop2",
                    items_status=upload_set.AggregatedStatus(prepared=0, preparing=1, broken=0, not_processed=2),
                ),
            ],
            key=lambda x: x.id,
        )
        assert u.items_status == upload_set.AggregatedStatus(prepared=2, preparing=1, broken=1, not_processed=2, rejected=0)


def test_upload_set_dispatch_with_orphan_picture(client, defaultAccountID):
    """
    There is currently a bug at upload, where a 2 pictures can be created for the same file, leading to 1 picture being without associated file
    The dispatch method should delete this picture.

    Note: this test could be removed at some point when we are confident the bug is fixed.
    """
    with db.cursor(current_app, row_factory=dict_row) as cur:
        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()["id"]

        pics_id = []
        for _ in range(2):
            pic_id = insert_pic(cur, upload_id, "pouet.jpg", defaultAccountID)
            pics_id.append(pic_id)
        cur.execute(
            SQL(
                """INSERT INTO files(
        upload_set_id, picture_id, file_type, file_name, size, content_md5)
    VALUES (%(upload_set_id)s, %(picture_id)s, %(type)s, %(file_name)s, %(size)s, %(content_md5)s)"""
            ),
            params={
                "upload_set_id": upload_id,
                "type": "picture",
                "picture_id": pics_id[0],
                "file_name": "pouet.jpg",
                "size": 12,
                "content_md5": uuid.uuid4(),
            },
        )

        nb_files = cur.execute("SELECT COUNT(*) AS nb FROM files").fetchone()["nb"]
        assert nb_files == 1
        remaining_pics_id = cur.execute("SELECT id FROM pictures").fetchall()
        assert set((p["id"] for p in remaining_pics_id)) == set(pics_id)
        u = upload_set.get_upload_set(upload_id)
        assert u and u.dispatched is False

        upload_set.dispatch(cur.connection, upload_id)

        nb_files = cur.execute("SELECT COUNT(*) AS nb FROM files").fetchone()["nb"]
        remaining_pics_id = cur.execute("SELECT id, status FROM pictures").fetchall()
        # one picture should have been marked for deletion
        assert remaining_pics_id == [
            {"id": pics_id[0], "status": "waiting-for-process"},
            {"id": pics_id[1], "status": "waiting-for-delete"},
        ]
        assert nb_files == 1
        u = upload_set.get_upload_set(upload_id)
        assert u and u.dispatched is True


def insert_pic(cur, upload_set_id, name, account):
    pic_id = cur.execute(
        """INSERT INTO pictures (ts, geom, account_id, upload_set_id, metadata)
    VALUES (%(ts)s, ST_SetSRID(ST_MakePoint(0, %(lon)s), 4326), %(account_id)s, %(upload_set_id)s, %(metadata)s)
    RETURNING id""",
        {
            "ts": datetime(year=2024, month=7, day=21, hour=10).isoformat(),
            "account_id": account,
            "upload_set_id": upload_set_id,
            "lon": 12,
            "metadata": Jsonb(
                {
                    "make": None,
                    "roll": None,
                    "type": "flat",
                    "model": None,
                    "crop": None,
                    "pitch": None,
                    "width": 5760,
                    "height": 4320,
                    "focal_length": None,
                    "originalFileName": name,
                    "originalFileSize": 12,
                }
            ),
        },
    ).fetchone()["id"]
    return pic_id


def test_upload_set_insert_file_twice_for_same_picture(client, defaultAccountID):
    """Sending again a file is invalid if the first existing file is already associated to a picture"""
    with db.cursor(current_app, row_factory=dict_row) as cur:
        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()["id"]

        pic_id = insert_pic(cur, upload_id, "pouet.jpg", defaultAccountID)
        f = upload_set.insertFileInDatabase(
            cursor=cur, upload_set_id=upload_id, picture_id=pic_id, file_name="pouet.jpg", file_type="picture", content_md5=uuid.uuid4()
        )

        with pytest.raises(InvalidAPIUsage) as e:
            f = upload_set.insertFileInDatabase(
                cursor=cur, upload_set_id=upload_id, picture_id=pic_id, file_name="pouet.jpg", file_type="picture", content_md5=uuid.uuid4()
            )
        assert str(e.value) == "A different picture with the same name has already been added to this uploadset"


def test_upload_set_insert_file_twice_for_picture_same_name_no_associated_pic(client, defaultAccountID):
    """Attempting to send again a file is valid is there is not associated picture for this file (can be the case where the first attempt was not succesfull)"""
    with db.cursor(current_app, row_factory=dict_row) as cur:
        upload_id = cur.execute(
            "INSERT INTO upload_sets (title, account_id) VALUES (%s, %s) RETURNING id", ["some title", defaultAccountID]
        ).fetchone()["id"]

        pic_id = insert_pic(cur, upload_id, "pouet.jpg", defaultAccountID)
        # first upload is not valid
        f = upload_set.insertFileInDatabase(
            cursor=cur,
            upload_set_id=upload_id,
            file_name="pouet.jpg",
            file_type="picture",
            rejection_status=upload_set.FileRejectionStatus.invalid_file,
        )

        # it's ok to send again the file
        md5 = uuid.uuid4()
        f = upload_set.insertFileInDatabase(
            cursor=cur, upload_set_id=upload_id, picture_id=pic_id, file_name="pouet.jpg", file_type="picture", content_md5=md5
        )

        files = upload_set.get_upload_set_files(upload_id)
        assert files == upload_set.UploadSetFiles(
            files=[
                upload_set.UploadSetFile(
                    picture_id=pic_id,
                    file_name="pouet.jpg",
                    content_md5=md5,
                    inserted_at=files.files[0].inserted_at,  # we don't care about the insertion date
                    upload_set_id=upload_id,
                    rejection_status=None,
                    rejection_message=None,
                    rejection_details=None,
                    file_type="picture",
                    size=None,
                    rejected=None,
                    links=files.files[0].links,  # we don't care either about the links
                )
            ],
            upload_set_id=upload_id,
        )
