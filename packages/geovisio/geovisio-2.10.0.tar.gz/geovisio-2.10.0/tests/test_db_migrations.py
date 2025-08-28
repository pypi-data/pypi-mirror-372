import psycopg
from geovisio import db_migrations
from . import conftest
import pytest
from dataclasses import dataclass


@pytest.fixture(autouse=True)
def update_schema(dburl):
    """After each of those test, the schema should be up to date (to not mess with other tests)"""
    # load test.env file if available
    yield
    db_migrations.update_db_schema(dburl, force=True)


def test_upgrade_downgrade_upgrade(dburl, app):
    """Tests that schema upgrade -> downgrade -> upgrade"""
    # At startup the database should have an up to date schema
    assert _pictures_table_exists(dburl)

    # downgrade the schema
    db_migrations.rollback_db_schema(dburl, rollback_all=True)

    # after the downgrade there should not be a pictures table anymore
    assert not _pictures_table_exists(dburl)

    # if we apply the schema again we get back the table
    db_migrations.update_db_schema(dburl, force=True)
    assert _pictures_table_exists(dburl)


def test_one_rollback(dburl):
    """Creating an app with an invalid database lead to an error"""
    db_migrations.update_db_schema(dburl, force=True)
    assert _pictures_table_exists(dburl)
    backend = db_migrations.get_yoyo_backend(dburl)
    initial_migrations_applyed = backend.get_applied_migration_hashes()
    assert len(initial_migrations_applyed) > 0

    # downgrade the schema
    db_migrations.rollback_db_schema(dburl, rollback_all=False)

    # we should have one less migration
    migrations_applyed = backend.get_applied_migration_hashes()
    assert len(migrations_applyed) == len(initial_migrations_applyed) - 1


def test_init_bad_db(tmp_path):
    """Creating an app with an invalid database lead to an error"""
    invalidUrl = "postgres://postgres@invalid_host/geovisio"
    with pytest.raises(psycopg.OperationalError):
        with conftest.create_test_app(
            {
                "TESTING": True,
                "DB_URL": invalidUrl,
                "FS_URL": str(tmp_path),
                "FS_TMP_URL": None,
                "FS_DERIVATES_URL": None,
                "FS_PERMANENT_URL": None,
            }
        ):
            pass


@dataclass
class GeomAndBbox:
    geom: str
    bbox: str


def get_geom_and_bbox(db, id):
    r = db.execute("SELECT ST_AsText(geom) AS geom, ST_AsText(bbox) FROM sequences WHERE id = %s", [id]).fetchone()
    assert r
    return GeomAndBbox(geom=r[0], bbox=r[1])


@conftest.SEQ_IMGS
def test_db_update_pictures_sequences(datafiles, initSequenceApp, dburl):
    # Checks behaviour of DB migration 20230425_01_gYP77-pictures-edits-triggers.sql
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId, _ = conftest.getFirstPictureIds(dburl)
        init = get_geom_and_bbox(db, seqId)
        assert (
            init.geom
            == "MULTILINESTRING((1.919185441799137 49.00688961988304,1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235,1.919199780601944 49.00695484980094,1.919194019996227 49.00697341759938))"
        )
        assert (
            init.bbox
            == "POLYGON((1.919185441799137 49.00688961988304,1.919185441799137 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.00688961988304,1.919185441799137 49.00688961988304))"
        )

        # Change first picture location -> edits sequence geom
        db.execute(
            "UPDATE pictures SET geom = ST_SetSRID(ST_Point(1.919189621, 49.0068986459), 4326) WHERE id = (SELECT pic_id FROM sequences_pictures WHERE rank = 1 AND seq_id = %s)",
            [seqId],
        )
        new_geom = get_geom_and_bbox(db, seqId)

        assert (
            new_geom.geom
            == "MULTILINESTRING((1.919189621 49.0068986459,1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235,1.919199780601944 49.00695484980094,1.919194019996227 49.00697341759938))"
        )
        assert new_geom.bbox != init.bbox and (
            new_geom.bbox
            == "POLYGON((1.919189621 49.0068986458004,1.919189621 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.0068986458004,1.919189621 49.0068986458004))"
        )

        # If we move too many points, it might lead to the geometry being split (not to have too long strings in the map)
        db.execute(
            "UPDATE pictures SET geom = ST_SetSRID(ST_Point(ST_X(geom) + 10, ST_Y(geom)), 4326) WHERE id IN (SELECT pic_id FROM sequences_pictures WHERE rank IN (4, 5) AND seq_id = %s)",
            [seqId],
        )

        after_move = get_geom_and_bbox(db, seqId)
        assert (
            after_move.geom
            == "MULTILINESTRING((1.919189621 49.0068986459,1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235),(11.919199780601945 49.00695484980094,11.919194019996226 49.00697341759938))"
        )

        assert (
            new_geom.bbox
            == "POLYGON((1.919189621 49.0068986458004,1.919189621 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.0068986458004,1.919189621 49.0068986458004))"
        )


@conftest.SEQ_IMGS
def test_db_delete_pictures_sequences(datafiles, initSequenceApp, dburl):
    # Checks behaviour of DB migration 20230425_01_gYP77-pictures-edits-triggers.sql
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId, _ = conftest.getFirstPictureIds(dburl)
        init = get_geom_and_bbox(db, seqId)
        assert (
            init.geom
            == "MULTILINESTRING((1.919185441799137 49.00688961988304,1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235,1.919199780601944 49.00695484980094,1.919194019996227 49.00697341759938))"
        )
        assert (
            init.bbox
            == "POLYGON((1.919185441799137 49.00688961988304,1.919185441799137 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.00688961988304,1.919185441799137 49.00688961988304))"
        )

        # Delete first picture in sequence -> edits sequence geom
        db.execute("DELETE FROM sequences_pictures WHERE rank = 1 AND seq_id = %s", [seqId])
        new_geom = get_geom_and_bbox(db, seqId)

        assert (
            new_geom.geom
            == "MULTILINESTRING((1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235,1.919199780601944 49.00695484980094,1.919194019996227 49.00697341759938))"
        )
        assert new_geom.bbox != init.bbox
        assert (
            new_geom.bbox
            == "POLYGON((1.919189623000528 49.0068986458004,1.919189623000528 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.0068986458004,1.919189623000528 49.0068986458004))"
        )


@conftest.SEQ_IMGS
def test_db_delete_all_pics(datafiles, initSequenceApp, dburl):
    # Checks behaviour of DB migration 20240514_01_IT7DD-picture-delete-cascade.sql
    # we don't want to recompute the geometry when deleting a sequence and all its pictures
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId, _ = conftest.getFirstPictureIds(dburl)
        init = get_geom_and_bbox(db, seqId)
        assert (
            init.geom
            == "MULTILINESTRING((1.919185441799137 49.00688961988304,1.919189623000528 49.0068986458004,1.919196360602742 49.00692625960235,1.919199780601944 49.00695484980094,1.919194019996227 49.00697341759938))"
        )
        assert (
            init.bbox
            == "POLYGON((1.919185441799137 49.00688961988304,1.919185441799137 49.00697341759938,1.919199780601944 49.00697341759938,1.919199780601944 49.00688961988304,1.919185441799137 49.00688961988304))"
        )

        # mark a sequence as deleted, and delete all it's pictures, this should cascade to the `sequences_pictures` table
        with db.transaction():
            db.execute("UPDATE sequences SET status = 'deleted' WHERE id = %s", [seqId])
            db.execute("DELETE FROM pictures")

        nb_seq_pic = db.execute("SELECT count(*) FROM sequences_pictures").fetchone()
        assert nb_seq_pic == (0,)

        new_geom = get_geom_and_bbox(db, seqId)

        assert new_geom.geom == init.geom
        assert new_geom.bbox == init.bbox


@conftest.SEQ_IMGS
def test_db_pic_update_seq_date(datafiles, initSequenceApp, dburl):
    # Checks behaviour of DB migration 20231103_01_ZVKEm-update-seq-on-pic-change.sql
    with initSequenceApp(datafiles, preprocess=False), psycopg.connect(dburl, autocommit=True) as db:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        # Force sequence updated time to old time
        db.execute("UPDATE sequences SET updated_at = '2023-01-01T00:00:00Z' WHERE id = %s", [seqId])

        # Make any change on picture
        db.execute("UPDATE pictures SET status = 'hidden' WHERE id = %s", [picId])

        # Check sequence updated time
        isTimeOk = db.execute(
            "SELECT current_timestamp - updated_at <= interval '15 seconds' FROM sequences WHERE id = %s", [seqId]
        ).fetchone()[0]
        assert isTimeOk

        # Also check for deletions
        db.execute("UPDATE sequences SET updated_at = '2023-01-01T00:00:00Z' WHERE id = %s", [seqId])
        db.execute("DELETE FROM pictures WHERE id = %s", [picId])
        isTimeOk = db.execute(
            "SELECT current_timestamp - updated_at <= interval '15 seconds' FROM sequences WHERE id = %s", [seqId]
        ).fetchone()[0]
        assert isTimeOk


def _pictures_table_exists(dburl):
    with psycopg.connect(dburl) as conn:
        with conn.cursor() as cursor:
            return cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = 'pictures')").fetchone()[0]
