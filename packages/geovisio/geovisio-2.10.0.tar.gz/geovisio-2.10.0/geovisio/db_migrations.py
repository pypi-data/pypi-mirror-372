import yoyo
import psycopg
from psycopg.sql import SQL, Identifier
import os
import sys


def update_db_schema(dbUrl, force=False):
    # Check if DB has its structure initialized
    with psycopg.connect(dbUrl) as conn:
        with conn.cursor() as cursor:
            # Alert if database is not UTC
            dbTz = cursor.execute("SHOW timezone").fetchone()[0]
            isUtcOffset = cursor.execute(
                "SELECT EXISTS(SELECT * FROM pg_timezone_names WHERE name = %s AND utc_offset='00:00:00' AND NOT is_dst)", [dbTz]
            ).fetchone()[0]
            if not isUtcOffset:
                dbName = Identifier(dbUrl.split("/")[-1])
                if force:
                    cursor.execute(SQL("ALTER DATABASE {db} SET TIMEZONE TO 'UTC'").format(db=dbName))
                else:
                    raise Exception(
                        f"""Database is not running at UTC timezone !

Your database actually uses timezone \"{dbTz}\".
Issues could happen if your database runs at a different timezone.
You can set the database timezone using the following command:

ALTER DATABASE {dbName.as_string()} SET TIMEZONE TO 'UTC';"""
                    )

            picturesTableExists = cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname = 'pictures')").fetchone()[0]
            yoyoExists = cursor.execute("SELECT EXISTS(SELECT relname FROM pg_class WHERE relname like '_yoyo_%')").fetchone()[0]
        conn.close()

    backend = get_yoyo_backend(dbUrl)
    migrations = get_migrations()

    with backend.lock():
        # Yoyo migration was introduced in version >= 1.4.0
        # This block automatically handles migrations of databases created before yoyo era
        if picturesTableExists and not yoyoExists:
            handledMigrations = [
                m for m in migrations if m.id in ["20221201_01_wpCGc-initial-schema", "20221201_02_ZG8AR-camera-information"]
            ]
            print("Database migrated to use Yoyo tools...")
            backend.mark_migrations(handledMigrations)

        migrationToApply = backend.to_apply(migrations)
        migrationNames = ", ".join([m.id for m in migrationToApply])

        if len(migrationToApply) > 0:
            # Migration are applied automatically if database is completely empty
            if force or (not picturesTableExists and not yoyoExists):
                print("Updating database schema:")
                for m in migrationToApply:
                    print(f"  - {m.id}")
                backend.apply_migrations(migrationToApply)
                print("Migrations are done")

            # If database not empty and this function was called during API startup
            # Then we show an error to recommend manually updating (as this can take some time)
            else:
                # Note: it's a bit hacky, but we don't want to go through more checks
                # * neither for the custom `db`` commands
                # 	since in this case we want to either force the schema migration or rollback it
                # * nor for the tests
                if "db" not in sys.argv and "pytest" not in sys.modules:
                    raise Exception(
                        f"""Geovisio database schema needs an update !

The following database migrations are required:
  {migrationNames}

Please apply them using this command:
  flask db upgrade"""
                    )

        # Don't show this message if function was called during classic instance start
        elif force:
            print("Database schema already up-to-date")


def rollback_db_schema(dbUrl, rollback_all):
    backend = get_yoyo_backend(dbUrl)
    migrations = get_migrations()

    with backend.lock():
        migrations_to_rollback = backend.to_rollback(migrations)
        if not rollback_all:
            migrations_to_rollback = migrations_to_rollback[:1]  # we only rollback the last one
        if len(migrations_to_rollback) > 0:
            print("Starting rollback for migrations:")
            for m in migrations_to_rollback:
                print(f"  - {m.id}")
            backend.rollback_migrations(migrations_to_rollback)
            print("Rollbacks are done")
        else:
            print("There are no migrations to rollback")


def get_yoyo_backend(dbUrl):
    dbUrl = dbUrl.replace("postgres://", "postgresql+psycopg://")  # force psycopg3 usage on yolo
    return yoyo.get_backend(dbUrl)


def get_migrations():
    return yoyo.read_migrations(os.path.join(os.path.dirname(__file__), "../migrations"))
