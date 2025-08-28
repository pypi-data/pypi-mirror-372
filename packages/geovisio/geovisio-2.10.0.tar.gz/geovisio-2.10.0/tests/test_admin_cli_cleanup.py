from geovisio import utils
import geovisio.admin_cli.cleanup
from . import conftest
import psycopg
import pytest
import os


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
@pytest.mark.parametrize(
    ("singleSeq", "full", "db", "cache", "original"),
    (
        (True, False, False, False, False),
        (True, True, False, False, False),
        (True, False, True, False, False),
        (True, False, False, True, False),
        (True, False, False, False, True),
        (False, False, False, False, False),
        (False, True, False, False, False),
        (False, False, True, False, False),
        (False, False, False, True, False),
        (False, False, False, False, True),
    ),
)
def test_cleanup(datafiles, initSequenceApp, dburl, singleSeq, full, db, cache, original):
    with initSequenceApp(datafiles):
        with psycopg.connect(dburl) as conn:
            sequences = []
            picsSeq1 = sorted(
                [
                    str(p[0])
                    for p in conn.execute(
                        "SELECT pic_id FROM sequences_pictures WHERE seq_id = (SELECT id FROM sequences WHERE metadata->>'title'='seq1')"
                    )
                ]
            )
            picsSeq2 = sorted(
                [
                    str(p[0])
                    for p in conn.execute(
                        "SELECT pic_id FROM sequences_pictures WHERE seq_id = (SELECT id FROM sequences WHERE metadata->>'title'='seq2')"
                    )
                ]
            )

            if singleSeq:
                sequences = [conn.execute("SELECT id FROM sequences WHERE metadata->>'title'='seq1'").fetchone()[0]]

            geovisio.admin_cli.cleanup.cleanup(sequences, full, db, cache, original)

            # Check db cleanup
            if full or db:
                assert [p[0] for p in conn.execute("SELECT metadata->>'title' FROM sequences").fetchall()] == (
                    ["seq2"] if singleSeq else []
                )
                if singleSeq:
                    assert sorted([str(p[0]) for p in conn.execute("SELECT id FROM pictures").fetchall()]) == picsSeq2
                else:
                    assert len(conn.execute("SELECT id FROM pictures").fetchall()) == 0
            else:
                assert sorted([p[0] for p in conn.execute("SELECT metadata->>'title' FROM sequences").fetchall()]) == ["seq1", "seq2"]

            # Check derivates cleanup
            if full or cache:
                if singleSeq:
                    for p in picsSeq1:
                        assert not os.path.isdir(datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / p[9:])
                else:
                    assert len(os.listdir(datafiles / "derivates")) == 0

            # Check original pictures cleanup
            if full or original:
                if singleSeq:
                    for p in picsSeq1:
                        assert not os.path.isdir(datafiles / "permanent" / p[0:2] / p[2:4] / p[4:6] / p[6:8])
                else:
                    assert len(os.listdir(datafiles / "permanent")) == 0


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
def test_cleanup_allInDb_unfinished_allseqs(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles):

        with psycopg.connect(dburl) as conn:
            # Add a single picture to process table
            conn.execute("INSERT INTO job_queue(picture_id, task) SELECT id, 'prepare' FROM pictures LIMIT 1")
            conn.commit()

            geovisio.admin_cli.cleanup.cleanup(database=True)

            assert len(conn.execute("SELECT id FROM pictures").fetchall()) == 0


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
def test_cleanup_allInDb_unfinished_1seq(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles):
        with psycopg.connect(dburl) as conn:
            # Select a single sequence
            seqId = conn.execute("SELECT id FROM sequences LIMIT 1").fetchone()[0]

            # Add a single picture to process table
            conn.execute(
                "INSERT INTO job_queue(picture_id, task) SELECT pic_id, 'prepare' FROM sequences_pictures WHERE seq_id = %s LIMIT 1",
                [seqId],
            )
            conn.commit()

            geovisio.admin_cli.cleanup.cleanup(sequences=[seqId], database=True)

            assert len(conn.execute("SELECT pic_id FROM sequences_pictures WHERE seq_id = %s", [seqId]).fetchall()) == 0


@conftest.SEQ_IMGS
@conftest.SEQ_IMGS_FLAT
@conftest.SEQ_IMG_BLURRED
def test_cleanup_blur(monkeypatch, datafiles, initSequenceApp, tmp_path, dburl):
    monkeypatch.setattr(utils.pictures, "createBlurredHDPicture", conftest.mockCreateBlurredHDPictureFactory(datafiles))
    with initSequenceApp(datafiles, blur=True):
        with psycopg.connect(dburl) as db:
            sequences = [db.execute("SELECT id FROM sequences WHERE metadata->>'title'='seq1'").fetchone()[0]]
            picsSeq1 = sorted(
                [
                    str(p[0])
                    for p in db.execute(
                        "SELECT pic_id FROM sequences_pictures WHERE seq_id = (SELECT id FROM sequences WHERE metadata->>'title' = 'seq1')"
                    )
                ]
            )
            picsSeq2 = sorted(
                [
                    str(p[0])
                    for p in db.execute(
                        "SELECT pic_id FROM sequences_pictures WHERE seq_id = (SELECT id FROM sequences WHERE metadata->>'title' = 'seq2')"
                    )
                ]
            )
            geovisio.admin_cli.cleanup.cleanup(sequences, full=False, database=False, cache=False, permanentPics=True)

            # Check DB and other derivates are untouched
            assert [p[0] for p in db.execute("SELECT metadata->>'title' FROM sequences").fetchall()] == ["seq1", "seq2"]

            for p in picsSeq1:
                assert not (datafiles / "permanent" / p[0:2] / p[2:4] / p[4:6] / p[6:8]).is_dir()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8]).is_dir()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / p[9:] / "sd.jpg").is_file()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / p[9:] / "thumb.jpg").is_file()
            for p in picsSeq2:
                assert (datafiles / "permanent" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / (p[9:] + ".jpg")).is_file()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8]).is_dir()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / p[9:] / "sd.jpg").is_file()
                assert (datafiles / "derivates" / p[0:2] / p[2:4] / p[4:6] / p[6:8] / p[9:] / "thumb.jpg").is_file()
