from enum import Enum
import logging
import psycopg.rows
from pydantic import BaseModel, ConfigDict, computed_field, Field, field_serializer
from geovisio.utils.extent import TemporalExtent
from uuid import UUID
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from geovisio.utils import cql2, db, sequences
from geovisio import errors
from geovisio.utils.link import make_link, Link
import psycopg
from psycopg.types.json import Jsonb
from psycopg.sql import SQL
from psycopg.rows import class_row, dict_row
from flask import current_app
from flask_babel import gettext as _
from geopic_tag_reader import sequence as geopic_sequence, reader
from geovisio.utils.tags import SemanticTag

from geovisio.utils.loggers import getLoggerWithExtra


class AggregatedStatus(BaseModel):
    """Aggregated status"""

    prepared: int
    """Number of pictures successfully processed"""
    preparing: Optional[int]
    """Number of pictures being processed"""
    broken: Optional[int]
    """Number of pictures that failed to be processed. It is likely a server problem."""
    rejected: Optional[int] = None
    """Number of pictures that were rejected by the server. It is likely a client problem."""
    not_processed: Optional[int]
    """Number of pictures that have not been processed yet"""

    model_config = ConfigDict(use_attribute_docstrings=True)


class AssociatedCollection(BaseModel):
    """Collection associated to an UploadSet"""

    id: UUID
    nb_items: int
    extent: Optional[TemporalExtent] = None
    title: Optional[str] = None
    items_status: Optional[AggregatedStatus] = None
    status: Optional[str] = Field(exclude=True, default=None)

    @computed_field
    @property
    def links(self) -> List[Link]:
        return [
            make_link(rel="self", route="stac_collections.getCollection", collectionId=self.id),
        ]

    @computed_field
    @property
    def ready(self) -> Optional[bool]:
        if self.items_status is None:
            return None
        return self.items_status.not_processed == 0 and self.status == "ready"


class UploadSet(BaseModel):
    """The UploadSet represent a group of files sent in one upload. Those files will be distributed among one or more collections."""

    id: UUID
    created_at: datetime
    completed: bool
    dispatched: bool
    account_id: UUID
    title: str
    estimated_nb_files: Optional[int] = None
    sort_method: geopic_sequence.SortMethod
    no_split: Optional[bool] = None
    split_distance: Optional[int] = None
    split_time: Optional[timedelta] = None
    no_deduplication: Optional[bool] = None
    duplicate_distance: Optional[float] = None
    duplicate_rotation: Optional[int] = None
    metadata: Optional[Dict[str, Any]]
    user_agent: Optional[str] = Field(exclude=True)
    associated_collections: List[AssociatedCollection] = []
    nb_items: int = 0
    items_status: Optional[AggregatedStatus] = None
    semantics: List[SemanticTag] = Field(default_factory=list)
    """Semantic tags associated to the upload_set"""
    relative_heading: Optional[int] = None
    """The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture upload_sets, 0° is heading north). Is applied to all associated collections if set."""

    @computed_field
    @property
    def links(self) -> List[Link]:
        return [
            make_link(rel="self", route="upload_set.getUploadSet", upload_set_id=self.id),
        ]

    @computed_field
    @property
    def ready(self) -> bool:
        return self.dispatched and all(c.ready for c in self.associated_collections)

    model_config = ConfigDict(use_enum_values=True, ser_json_timedelta="float", use_attribute_docstrings=True)


class UploadSets(BaseModel):
    upload_sets: List[UploadSet]


class FileType(Enum):
    """Type of uploadedfile"""

    picture = "picture"
    # Note: for the moment we only support pictures, but later we might accept more kind of files (like gpx traces, video, ...)


class FileRejectionStatusSeverity(Enum):
    error = "error"
    warning = "warning"
    info = "info"


class FileRejectionStatus(Enum):
    capture_duplicate = "capture_duplicate"
    """capture duplicate means there was another picture too near (in space and time)"""
    file_duplicate = "file_duplicate"
    """File duplicate means the same file was already uploaded"""
    invalid_file = "invalid_file"
    """invalid_file means the file is not a valid jpeg"""
    invalid_metadata = "invalid_metadata"
    """invalid_metadata means the file has invalid metadata"""
    other_error = "other_error"
    """other_error means there was an error that is not related to the picture itself"""


class FileRejection(BaseModel):
    """Details about a file rejection"""

    reason: str
    severity: FileRejectionStatusSeverity
    message: Optional[str]
    details: Optional[Dict[str, Any]]

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)


class UploadSetFile(BaseModel):
    """File uploaded in an UploadSet"""

    picture_id: Optional[UUID] = None
    """ID of the picture this file belongs to. Can only be seen by the owner of the File"""
    file_name: str
    content_md5: Optional[UUID] = None
    inserted_at: datetime
    upload_set_id: UUID = Field(..., exclude=True)
    rejection_status: Optional[FileRejectionStatus] = Field(None, exclude=True)
    rejection_message: Optional[str] = Field(None, exclude=True)
    rejection_details: Optional[Dict[str, Any]] = Field(None, exclude=True)
    file_type: Optional[FileType] = None
    size: Optional[int] = None

    @computed_field
    @property
    def links(self) -> List[Link]:
        return [
            make_link(rel="parent", route="upload_set.getUploadSet", upload_set_id=self.upload_set_id),
        ]

    @computed_field
    @property
    def rejected(self) -> Optional[FileRejection]:
        if self.rejection_status is None:
            return None
        msg = None
        severity = FileRejectionStatusSeverity.error
        if self.rejection_message is None:
            if self.rejection_status == FileRejectionStatus.capture_duplicate.value:
                msg = _("The picture is too similar to another one (nearby and taken almost at the same time)")
                severity = FileRejectionStatusSeverity.info
            if self.rejection_status == FileRejectionStatus.invalid_file.value:
                msg = _("The sent file is not a valid JPEG")
                severity = FileRejectionStatusSeverity.error
            if self.rejection_status == FileRejectionStatus.invalid_metadata.value:
                msg = _("The picture has invalid EXIF or XMP metadata, making it impossible to use")
                severity = FileRejectionStatusSeverity.error
            if self.rejection_status == FileRejectionStatus.other_error.value:
                msg = _("Something went very wrong, but not due to the picture itself")
                severity = FileRejectionStatusSeverity.error
        else:
            msg = self.rejection_message
        return FileRejection(reason=self.rejection_status, severity=severity, message=msg, details=self.rejection_details)

    @field_serializer("content_md5")
    def serialize_md5(self, md5: UUID, _info):
        return md5.hex

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)


class UploadSetFiles(BaseModel):
    """List of files uploaded in an UploadSet"""

    files: List[UploadSetFile]
    upload_set_id: UUID = Field(..., exclude=True)

    @computed_field
    @property
    def links(self) -> List[Link]:
        return [
            make_link(rel="self", route="upload_set.getUploadSet", upload_set_id=self.upload_set_id),
        ]


def get_simple_upload_set(id: UUID) -> Optional[UploadSet]:
    """Get the DB representation of an UploadSet, without associated collections and statuses"""
    u = db.fetchone(
        current_app,
        SQL("SELECT * FROM upload_sets WHERE id = %(id)s"),
        {"id": id},
        row_factory=class_row(UploadSet),
    )

    return u


def get_upload_set(id: UUID) -> Optional[UploadSet]:
    """Get the UploadSet corresponding to the ID"""
    db_upload_set = db.fetchone(
        current_app,
        SQL(
            """WITH picture_last_job AS (
    SELECT p.id as picture_id,
        -- Note: to know if a picture is being processed, check the latest job_history entry for this picture
        -- If there is no finished_at, the picture is still being processed
        (MAX(ARRAY [started_at, finished_at])) AS last_job,
        p.preparing_status,
        p.status,
        p.upload_set_id
    FROM pictures p
        LEFT JOIN job_history ON p.id = job_history.picture_id
    WHERE p.upload_set_id = %(id)s
    GROUP BY p.id
),
picture_statuses AS (
    SELECT
        *,
        (last_job[1] IS NOT NULL AND last_job[2] IS NULL) AS is_job_running
        FROM picture_last_job psj
),
associated_collections AS (
    SELECT
        ps.upload_set_id,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'broken') AS nb_broken,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'prepared') AS nb_prepared,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'not-processed') AS nb_not_processed,
        COUNT(ps.picture_id) FILTER (WHERE ps.is_job_running AND ps.status != 'waiting-for-delete') AS nb_preparing,
        s.id as collection_id,
        s.nb_pictures AS nb_items,
        s.min_picture_ts AS mints,
        s.max_picture_ts AS maxts,
        s.metadata->>'title' AS title,
        s.status AS status
    FROM picture_statuses ps
        JOIN sequences_pictures sp ON sp.pic_id = ps.picture_id
        JOIN sequences s ON s.id = sp.seq_id
    WHERE ps.upload_set_id = %(id)s AND s.status != 'deleted'
    GROUP BY ps.upload_set_id,
        s.id
),
semantics AS (
    SELECT upload_set_id, json_agg(json_strip_nulls(json_build_object(
        'key', key,
        'value', value
    )) ORDER BY key, value) AS semantics
    FROM upload_sets_semantics
    WHERE upload_set_id = %(id)s
    GROUP BY upload_set_id
),
upload_set_statuses AS (
    SELECT ps.upload_set_id,
        COUNT(ps.picture_id) AS nb_items,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'broken') AS nb_broken,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'prepared') AS nb_prepared,
        COUNT(ps.picture_id) FILTER (WHERE ps.preparing_status = 'not-processed') AS nb_not_processed,
        COUNT(ps.picture_id) FILTER (WHERE ps.is_job_running) AS nb_preparing
    FROM picture_statuses ps
    GROUP BY ps.upload_set_id
)
SELECT u.*,
    COALESCE(us.nb_items, 0) AS nb_items,
    COALESCE(s.semantics, '[]'::json) AS semantics,
    json_build_object(
        'broken', COALESCE(us.nb_broken, 0),
        'prepared', COALESCE(us.nb_prepared, 0),
        'not_processed', COALESCE(us.nb_not_processed, 0),
        'preparing', COALESCE(us.nb_preparing, 0),
        'rejected', (
            SELECT count(*) FROM files
            WHERE upload_set_id = %(id)s AND rejection_status IS NOT NULL
        )
    ) AS items_status,
    COALESCE(
        (
            SELECT json_agg(
                    json_build_object(
                        'id',
                        ac.collection_id,
                        'title',
                        ac.title,
                        'nb_items',
                        ac.nb_items,
                        'status',
                        ac.status,
                        'extent',
                        json_build_object(
                            'temporal',
                            json_build_object(
                                'interval',
                                json_build_array(
                                    json_build_array(ac.mints, ac.maxts)
                                )
                            )
                        ),
                        'items_status',
                        json_build_object(
                            'broken', ac.nb_broken,
                            'prepared', ac.nb_prepared,
                            'not_processed', ac.nb_not_processed,
                            'preparing', ac.nb_preparing
                        )
                    )
                )
            FROM associated_collections ac
        ),
        '[]'::json
    ) AS associated_collections
FROM upload_sets u
LEFT JOIN upload_set_statuses us on us.upload_set_id = u.id
LEFT JOIN semantics s on s.upload_set_id = u.id
WHERE u.id = %(id)s"""
        ),
        {"id": id},
        row_factory=class_row(UploadSet),
    )

    return db_upload_set


FIELD_TO_SQL_FILTER = {
    "completed": "completed",
    "dispatched": "dispatched",
}


def _parse_filter(filter: Optional[str]) -> SQL:
    """
    Parse a filter string and return a SQL expression

    >>> _parse_filter('')
    SQL('TRUE')
    >>> _parse_filter(None)
    SQL('TRUE')
    >>> _parse_filter('completed = TRUE')
    SQL('(completed = True)')
    >>> _parse_filter('completed = TRUE AND dispatched = FALSE')
    SQL('((completed = True) AND (dispatched = False))')
    """
    if not filter:
        return SQL("TRUE")
    return cql2.parse_cql2_filter(filter, FIELD_TO_SQL_FILTER)


def list_upload_sets(account_id: UUID, limit: int = 100, filter: Optional[str] = None) -> UploadSets:
    filter_sql = _parse_filter(filter)
    l = db.fetchall(
        current_app,
        SQL(
            """SELECT
            u.*,
            COALESCE(
                (
                    SELECT
                        json_agg(json_build_object(
                            'id', s.id,
                            'nb_items', s.nb_pictures
                        ))
                    FROM sequences s
                    WHERE s.upload_set_id = u.id
                ),
                '[]'::json
            ) AS associated_collections,
            (
                SELECT count(*) AS nb
                FROM pictures p
                WHERE p.upload_set_id = u.id
            ) AS nb_items
        FROM upload_sets u
        WHERE account_id = %(account_id)s AND {filter}
        ORDER BY created_at ASC
        LIMIT %(limit)s
        """
        ).format(filter=filter_sql),
        {"account_id": account_id, "limit": limit},
        row_factory=class_row(UploadSet),
    )

    return UploadSets(upload_sets=l)


def ask_for_dispatch(upload_set_id: UUID):
    """Add a dispatch task to the job queue for the upload set. If there is already a task, postpone it."""
    with db.conn(current_app) as conn:
        conn.execute(
            """INSERT INTO
            job_queue(sequence_id, task)
            VALUES (%(upload_set_id)s, 'dispatch')
            ON CONFLICT (upload_set_id) DO UPDATE SET ts = CURRENT_TIMESTAMP""",
            {"upload_set_id": upload_set_id},
        )


@dataclass
class PicToDelete:
    picture_id: UUID
    detail: Optional[Dict] = None


def dispatch(conn: psycopg.Connection, upload_set_id: UUID):
    """Finalize an upload set.

    For the moment we only create a collection around all the items of the upload set, but later we'll split the items into several collections

    Note: even if all pictures are not prepared, it's not a problem as we only need the pictures metadata for distributing them in collections
    """

    db_upload_set = get_simple_upload_set(upload_set_id)
    if not db_upload_set:
        raise Exception(f"Upload set {upload_set_id} not found")

    logger = getLoggerWithExtra("geovisio.upload_set", {"upload_set_id": str(upload_set_id)})
    with conn.transaction(), conn.cursor(row_factory=dict_row) as cursor:
        # we put a lock on the upload set, to avoid new semantics being added while dispatching it
        # Note: I did not find a way to only put a lock on the upload_sets_semantics table, so we lock the whole upload_set row (and any child rows)
        _us_lock = cursor.execute(SQL("SELECT id FROM upload_sets WHERE id = %s FOR UPDATE"), [upload_set_id])

        # get all the pictures of the upload set
        db_pics = cursor.execute(
            SQL(
                """SELECT
    p.id,
    p.ts,
    ST_X(p.geom) as lon,
    ST_Y(p.geom) as lat,
    p.heading as heading,
    p.metadata->>'originalFileName' as file_name,
    p.metadata,
    s.id as sequence_id,
    f is null as has_no_file,
    p.heading_computed
FROM pictures p
LEFT JOIN sequences_pictures sp ON sp.pic_id = p.id
LEFT JOIN sequences s ON s.id = sp.seq_id
LEFT JOIN files f ON f.picture_id = p.id
WHERE p.upload_set_id = %(upload_set_id)s"""
            ),
            {"upload_set_id": upload_set_id},
        ).fetchall()

        config = cursor.execute(
            SQL(
                "SELECT default_split_distance, default_split_time, default_duplicate_distance, default_duplicate_rotation FROM configurations"
            )
        ).fetchone()

        # there is currently a bug where 2 pictures can be uploaded for the same file, so only 1 is associated to it.
        # we want to delete one of them
        # Those duplicates happen when a client send an upload that timeouts, but the client retries the upload and the server is not aware of this timeout (the connection is not closed).
        # Note: later, if we are confident the bug has been removed, we might clean this code.
        pics_to_delete_bug = [PicToDelete(picture_id=p["id"]) for p in db_pics if p["has_no_file"]]
        db_pics = [p for p in db_pics if p["has_no_file"] is False]  # pictures without files will be deleted, we don't need them
        pics_by_filename = {p["file_name"]: p for p in db_pics}

        pics = [
            geopic_sequence.Picture(
                p["file_name"],
                reader.GeoPicTags(
                    lon=p["lon"],
                    lat=p["lat"],
                    ts=p["ts"],
                    type=p["metadata"]["type"],
                    heading=p["heading"],
                    make=p["metadata"]["make"],
                    model=p["metadata"]["model"],
                    focal_length=p["metadata"]["focal_length"],
                    crop=p["metadata"]["crop"],
                    exif={},
                ),
                heading_computed=p["heading_computed"],
            )
            for p in db_pics
        ]

        split_params = None
        if not db_upload_set.no_split:
            distance = db_upload_set.split_distance if db_upload_set.split_distance is not None else config["default_split_distance"]
            t = db_upload_set.split_time if db_upload_set.split_time is not None else config["default_split_time"]
            if t is not None and distance is not None:
                split_params = geopic_sequence.SplitParams(maxDistance=distance, maxTime=t.total_seconds())
        merge_params = None
        if not db_upload_set.no_deduplication:
            distance = (
                db_upload_set.duplicate_distance if db_upload_set.duplicate_distance is not None else config["default_duplicate_distance"]
            )
            rotation = (
                db_upload_set.duplicate_rotation if db_upload_set.duplicate_rotation is not None else config["default_duplicate_rotation"]
            )
            if distance is not None and rotation is not None:
                merge_params = geopic_sequence.MergeParams(maxDistance=distance, maxRotationAngle=rotation)

        report = geopic_sequence.dispatch_pictures(
            pics, mergeParams=merge_params, sortMethod=db_upload_set.sort_method, splitParams=split_params
        )
        reused_sequence = set()

        pics_to_delete_duplicates = [
            PicToDelete(
                picture_id=pics_by_filename[d.picture.filename]["id"],
                detail={
                    "duplicate_of": str(pics_by_filename[d.duplicate_of.filename]["id"]),
                    "distance": d.distance,
                    "angle": d.angle,
                },
            )
            for d in report.duplicate_pictures
        ]
        pics_to_delete = pics_to_delete_duplicates + pics_to_delete_bug
        if pics_to_delete:
            logger.debug(
                f"nb duplicate pictures {len(pics_to_delete_duplicates)} {f' and {len(pics_to_delete_bug)} pictures without files' if pics_to_delete_bug else ''}"
            )
            logger.debug(f"duplicate pictures {[p.picture.filename for p in report.duplicate_pictures]}")

            cursor.execute(SQL("CREATE TEMPORARY TABLE tmp_duplicates(picture_id UUID, details JSONB) ON COMMIT DROP"))
            with cursor.copy("COPY tmp_duplicates(picture_id, details) FROM stdin;") as copy:
                for p in pics_to_delete:
                    copy.write_row((p.picture_id, Jsonb(p.detail) if p.detail else None))

            cursor.execute(
                SQL(
                    """UPDATE files SET 
    rejection_status = 'capture_duplicate', rejection_details = d.details 
FROM tmp_duplicates d 
WHERE d.picture_id = files.picture_id"""
                )
            )
            # set all the pictures as waiting for deletion and add background jobs to delete them
            # Note: we do not delte the picture's row because it can cause some deadlocks if some workers are preparing thoses pictures.
            cursor.execute(SQL("UPDATE pictures SET status = 'waiting-for-delete' WHERE id IN (select picture_id FROM tmp_duplicates)"))
            cursor.execute(
                SQL(
                    """INSERT INTO job_queue(picture_to_delete_id, task)
    SELECT picture_id, 'delete' FROM tmp_duplicates"""
                )
            )

        number_title = len(report.sequences) > 1
        existing_sequences = set(p["sequence_id"] for p in db_pics if p["sequence_id"])
        new_sequence_ids = set()
        for i, s in enumerate(report.sequences, start=1):
            existing_sequence = next(
                (seq for p in s.pictures if (seq := pics_by_filename[p.filename]["sequence_id"]) not in reused_sequence),
                None,
            )
            # if some of the pictures were already in a sequence, we should not create a new one
            if existing_sequence:
                logger.info(f"sequence {existing_sequence} already contains pictures, we will not create a new one")
                # we should wipe the sequences_pictures though
                seq_id = existing_sequence
                cursor.execute(
                    SQL("DELETE FROM sequences_pictures WHERE seq_id = %(seq_id)s"),
                    {"seq_id": seq_id},
                )
                reused_sequence.add(seq_id)
                # Note: we do not update the sequences_semantics if reusing a sequence, because the sequence semantics's updates are reported to the existing sequences if there are some
            else:
                new_title = f"{db_upload_set.title}{f'-{i}' if number_title else ''}"
                seq_id = cursor.execute(
                    SQL(
                        """INSERT INTO sequences(account_id, metadata, user_agent, upload_set_id)
                VALUES (%(account_id)s, %(metadata)s, %(user_agent)s, %(upload_set_id)s)
                RETURNING id"""
                    ),
                    {
                        "account_id": db_upload_set.account_id,
                        "metadata": Jsonb({"title": new_title}),
                        "user_agent": db_upload_set.user_agent,
                        "upload_set_id": db_upload_set.id,
                    },
                ).fetchone()
                seq_id = seq_id["id"]

                # Pass all semantics to the new sequence
                copy_upload_set_semantics_to_sequence(cursor, db_upload_set.id, seq_id)
            new_sequence_ids.add(seq_id)

            with cursor.copy("COPY sequences_pictures(seq_id, pic_id, rank) FROM stdin;") as copy:
                for i, p in enumerate(s.pictures, 1):
                    copy.write_row(
                        (seq_id, pics_by_filename[p.filename]["id"], i),
                    )

            sequences.add_finalization_job(cursor=cursor, seqId=seq_id)

        # we can delete all the old sequences
        sequences_to_delete = existing_sequences - new_sequence_ids
        if sequences_to_delete:
            logger.debug(f"sequences to delete = {sequences_to_delete} (existing = {existing_sequences}, new = {new_sequence_ids})")
            conn.execute(SQL("DELETE FROM sequences_pictures WHERE seq_id = ANY(%(seq_ids)s)"), {"seq_ids": list(sequences_to_delete)})
            conn.execute(SQL("UPDATE sequences SET status = 'deleted' WHERE id = ANY(%(seq_ids)s)"), {"seq_ids": list(sequences_to_delete)})

        for s in report.sequences_splits or []:
            logger.debug(f"split = {s.prevPic.filename} -> {s.nextPic.filename} : {s.reason}")
        conn.execute(SQL("UPDATE upload_sets SET dispatched = true WHERE id = %(upload_set_id)s"), {"upload_set_id": db_upload_set.id})


def copy_upload_set_semantics_to_sequence(cursor, db_upload_id: UUID, seq_id: UUID):
    cursor.execute(
        SQL(
            """WITH upload_set_semantics AS (
                SELECT key, value, upload_set_id, account_id
                FROM upload_sets_semantics
                WHERE upload_set_id = %(upload_set_id)s
            ),
            seq_sem AS (
                INSERT INTO sequences_semantics(sequence_id, key, value)
                SELECT %(seq_id)s, key, value
                FROM upload_set_semantics
            )
            INSERT INTO sequences_semantics_history(sequence_id, account_id, ts, updates)
            SELECT %(seq_id)s, account_id, NOW(), jsonb_build_object('key', key, 'value', value, 'action', 'add')
            FROM upload_set_semantics
            """
        ),
        {
            "upload_set_id": db_upload_id,
            "seq_id": seq_id,
        },
    )


def insertFileInDatabase(
    *,
    cursor: psycopg.Cursor[psycopg.rows.DictRow],
    upload_set_id: UUID,
    file_name: str,
    content_md5: Optional[str] = None,
    size: Optional[int] = None,
    file_type: Optional[FileType] = None,
    picture_id: Optional[UUID] = None,
    rejection_status: Optional[FileRejectionStatus] = None,
    rejection_message: Optional[str] = None,
    rejection_details: Optional[Dict[str, Any]] = None,
) -> UploadSetFile:
    """Insert a file linked to an UploadSet into the database"""

    # we check if there is already a file with this name in the upload set with an associated picture.
    # If there is no picture (because the picture has been rejected), we accept that the file is overridden
    with cursor.connection.transaction():
        existing_file = cursor.execute(
            SQL(
                """SELECT picture_id, rejection_status
                FROM files
                WHERE upload_set_id = %(upload_set_id)s AND file_name = %(file_name)s AND picture_id IS NOT NULL"""
            ),
            params={
                "upload_set_id": upload_set_id,
                "file_name": file_name,
            },
        ).fetchone()
        if existing_file:
            raise errors.InvalidAPIUsage(
                _("A different picture with the same name has already been added to this uploadset"),
                status_code=409,
                payload={"existing_item": {"id": existing_file["picture_id"]}},
            )

        f = cursor.execute(
            SQL(
                """INSERT INTO files(
        upload_set_id, picture_id, file_type, file_name,
        size, content_md5, rejection_status, rejection_message, rejection_details)
    VALUES (
        %(upload_set_id)s, %(picture_id)s, %(type)s, %(file_name)s,
        %(size)s, %(content_md5)s, %(rejection_status)s, %(rejection_message)s, %(rejection_details)s)
    ON CONFLICT (upload_set_id, file_name)
    DO UPDATE SET picture_id = %(picture_id)s, size = %(size)s, content_md5 = %(content_md5)s,
        rejection_status = %(rejection_status)s, rejection_message = %(rejection_message)s, rejection_details = %(rejection_details)s
    WHERE files.picture_id IS NULL -- check again that we do not override an existing picture
    RETURNING *"""
            ),
            params={
                "upload_set_id": upload_set_id,
                "type": file_type,
                "picture_id": picture_id,
                "file_name": file_name,
                "size": size,
                "content_md5": content_md5,
                "rejection_status": rejection_status,
                "rejection_message": rejection_message,
                "rejection_details": Jsonb(rejection_details),
            },
        )
        u = f.fetchone()
        if u is None:
            logging.error(f"Impossible to add file {file_name} to uploadset {upload_set_id}")
            raise errors.InvalidAPIUsage(
                _("Impossible to add the picture to this uploadset"),
                status_code=500,
            )
        return UploadSetFile(**u)


def get_upload_set_files(upload_set_id: UUID) -> UploadSetFiles:
    """Get the files of an UploadSet"""
    files = db.fetchall(
        current_app,
        SQL(
            """SELECT
    upload_set_id,
    file_type,
    file_name,
    size,
    content_md5,
    rejection_status,
    rejection_message,
    rejection_details,
    picture_id,
    inserted_at
FROM files
WHERE upload_set_id = %(upload_set_id)s
ORDER BY inserted_at"""
        ),
        {"upload_set_id": upload_set_id},
        row_factory=dict_row,
    )
    return UploadSetFiles(files=files, upload_set_id=upload_set_id)


def delete(upload_set: UploadSet):
    """Delete an UploadSet"""
    logging.info(f"Asking for deletion of uploadset {upload_set.id}")
    with db.conn(current_app) as conn:
        # clean job queue, to ensure no async runner are currently processing pictures/sequences/upload_sets
        # Done outside the real deletion transaction to not trigger deadlock
        conn.execute(SQL("DELETE FROM job_queue WHERE picture_id IN (SELECT id FROM pictures where upload_set_id = %s)"), [upload_set.id])
        for c in upload_set.associated_collections:
            conn.execute(SQL("DELETE FROM job_queue WHERE sequence_id = %s"), [c.id])

        with conn.transaction(), conn.cursor() as cursor:
            for c in upload_set.associated_collections:
                # Mark all collections as deleted, but do not delete them
                # Note: we do not use utils.sequences.delete_collection here, since we also want to remove the pictures not associated to any collection
                cursor.execute(SQL("UPDATE sequences SET status = 'deleted' WHERE id = %s"), [c.id])

            # after the task have been added to the queue, we delete the upload set, and this will delete all pictures associated to it
            cursor.execute(SQL("DELETE FROM upload_sets WHERE id = %(upload_set_id)s"), {"upload_set_id": upload_set.id})
