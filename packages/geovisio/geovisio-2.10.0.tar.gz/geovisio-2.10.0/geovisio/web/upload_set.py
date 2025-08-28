from copy import deepcopy
from dataclasses import dataclass
import PIL
from geovisio.utils import auth, model_query
from psycopg.rows import class_row, dict_row
from psycopg.sql import SQL
from flask import current_app, request, Blueprint, url_for
from flask_babel import gettext as _, get_locale
from geopic_tag_reader import sequence as geopic_sequence
from geovisio.web.utils import accountIdOrDefault
from geovisio.utils.fields import parse_relative_heading
from geovisio.web.params import (
    as_latitude,
    as_longitude,
    parse_datetime,
)
import logging
from geovisio.utils import db
from geovisio import utils
from geopic_tag_reader.writer import writePictureMetadata, PictureMetadata
from geovisio.utils.params import validation_error
from geovisio.utils.semantics import SemanticTagUpdate
from geovisio.utils import semantics
from geovisio import errors
from pydantic import BaseModel, ConfigDict, ValidationError, Field, field_validator, model_validator
from uuid import UUID
from werkzeug.datastructures import FileStorage
from datetime import timedelta, datetime
from geovisio.utils.upload_set import (
    FileRejectionStatus,
    FileType,
    UploadSet,
    get_simple_upload_set,
    get_upload_set,
    get_upload_set_files,
    list_upload_sets,
)
import os
import hashlib
import sentry_sdk
from typing import Optional, Any, Dict, List


bp = Blueprint("upload_set", __name__, url_prefix="/api")


class UploadSetCreationParameter(BaseModel):
    """Parameters used to create an UploadSet"""

    title: str
    """Title of the upload. The title will be used to generate a name for the collections"""
    estimated_nb_files: Optional[int] = None
    """Estimated number of items that will be sent to the UploadSet"""
    sort_method: Optional[geopic_sequence.SortMethod] = None
    """Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order."""
    no_split: Optional[bool] = None
    """If True, all pictures of this upload set will be grouped in the same sequence. Is incompatible with split_distance / split_time."""
    split_distance: Optional[int] = None
    """Maximum distance between two pictures to be considered in the same sequence (in meters). If not set, the instance default will be used. The instance defaults can be see in /api/configuration."""
    split_time: Optional[timedelta] = None
    """Maximum time interval between two pictures to be considered in the same sequence.
    If not set, the instance default will be used. The instance defaults can be see in /api/configuration."""
    no_deduplication: Optional[bool] = None
    """If True, no duplication will be done. Is incompatible with duplicate_distance / duplicate_rotation."""
    duplicate_distance: Optional[float] = None
    """Maximum distance between two pictures to be considered as duplicates (in meters).
    If not set, the instance default will be used. The instance defaults can be see in /api/configuration."""
    duplicate_rotation: Optional[int] = None
    """Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).
    If not set, the instance default will be used. The instance defaults can be see in /api/configuration."""
    metadata: Optional[Dict[str, Any]] = None
    """Optional metadata associated to the upload set. Can contain any key-value pair."""
    user_agent: Optional[str] = None
    """Software used by client to create this upload set, in HTTP Header User-Agent format"""
    semantics: Optional[List[SemanticTagUpdate]] = None
    """Semantic tags associated to the upload_set. Those tags will be added to all sequences linked to this upload set"""
    relative_heading: Optional[int] = None
    """The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture upload_sets, 0° is heading north). Headings are unchanged if this parameter is not set."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    def validate(self):
        if self.no_split is True and (self.split_distance is not None or self.split_time is not None):
            raise errors.InvalidAPIUsage("The `no_split` parameter is incompatible with specifying `split_distance` / `split_duration`")
        if self.no_deduplication is True and (self.duplicate_distance is not None or self.duplicate_rotation is not None):
            raise errors.InvalidAPIUsage(
                "The `no_deduplication` parameter is incompatible with specifying `duplicate_distance` / `duplicate_rotation`"
            )

    @field_validator("relative_heading", mode="before")
    @classmethod
    def parse_relative_heading(cls, value):
        return parse_relative_heading(value)


class UploadSetUpdateParameter(BaseModel):
    """Parameters used to update an UploadSet"""

    sort_method: Optional[geopic_sequence.SortMethod] = None
    """Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order."""
    no_split: Optional[bool] = None
    """If True, all pictures of this upload set will be grouped in the same sequence. Is incompatible with split_distance / split_time."""
    split_distance: Optional[int] = None
    """Maximum distance between two pictures to be considered in the same sequence (in meters)."""
    split_time: Optional[timedelta] = None
    """Maximum time interval between two pictures to be considered in the same sequence."""
    no_deduplication: Optional[bool] = None
    """If True, no deduplication will be done. Is incompatible with duplicate_distance / duplicate_rotation

    Note that if the upload_set has already been dispatched, the deduplication has already been done so it cannot be deactivated.
    """
    duplicate_distance: Optional[float] = None
    """Maximum distance between two pictures to be considered as duplicates (in meters)."""
    duplicate_rotation: Optional[int] = None
    """Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees)."""
    semantics: Optional[List[SemanticTagUpdate]] = None
    """Semantic tags associated to the upload_set. Those tags will be added to all sequences linked to this upload set.
    By default each tag will be added to the upload set's tags, but you can change this behavior by setting the `action` parameter to `delete`.

    If you want to replace a tag, you need to first delete it, then add it again.

    Like:
    [
        {"key": "some_key", "value": "some_value", "action": "delete"},
        {"key": "some_key", "value": "some_new_value"}
    ]
    
    Note: for the moment it's not possible to update the semantics of an upload set after it has been dispatched.
    If that is something needed, feel free to open an issue.
    """
    relative_heading: Optional[int] = None
    """The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture upload_sets, 0° is heading north). Headings are unchanged if this parameter is not set."""

    model_config = ConfigDict(use_attribute_docstrings=True, extra="forbid")

    def validate(self):
        if self.no_split is True and (self.split_distance is not None or self.split_time is not None):
            raise errors.InvalidAPIUsage("The `no_split` parameter is incompatible with specifying `split_distance` / `split_duration`")
        if self.no_deduplication is True and (self.duplicate_distance is not None or self.duplicate_rotation is not None):
            raise errors.InvalidAPIUsage(
                "The `no_deduplication` parameter is incompatible with specifying `duplicate_distance` / `duplicate_rotation`"
            )

    def has_only_semantics_updates(self):
        return self.model_fields_set == {"semantics"}

    @field_validator("relative_heading", mode="before")
    @classmethod
    def parse_relative_heading(cls, value):
        return parse_relative_heading(value)


def create_upload_set(params: UploadSetCreationParameter, accountId: UUID) -> UploadSet:
    sem = params.semantics
    params.semantics = None
    db_params = model_query.get_db_params_and_values(params, account_id=accountId)
    with db.conn(current_app) as conn, conn.transaction():

        with conn.cursor(row_factory=class_row(UploadSet)) as cursor:
            db_upload_set = cursor.execute(
                SQL("INSERT INTO upload_sets({fields}) VALUES({values}) RETURNING *").format(
                    fields=db_params.fields(), values=db_params.placeholders()
                ),
                db_params.params_as_dict,
            ).fetchone()

            if db_upload_set is None:
                raise Exception("Impossible to insert upload_set in database")

        if sem:
            with conn.cursor() as cursor:
                semantics.update_tags(
                    cursor=cursor,
                    entity=semantics.Entity(semantics.EntityType.upload_set, db_upload_set.id),
                    actions=sem,
                    account=accountId,
                )

    return db_upload_set


def update_upload_set(upload_set_id: UUID, params: UploadSetUpdateParameter, account) -> UploadSet:
    """Update an upload set
    Since the semantic tags are handled in a separate table, split the update in 2, the semantic update, and the upload_sets table update"""
    with db.conn(current_app) as conn, conn.transaction():
        if params.semantics:
            # update the semantics if needed, and remove the semantic from the params for the other fields update
            sem = params.semantics
            params.semantics = None

            with conn.cursor() as cursor:
                semantics.update_tags(
                    cursor=cursor,
                    entity=semantics.Entity(semantics.EntityType.upload_set, upload_set_id),
                    actions=sem,
                    account=account.id if account is not None else None,
                )

                us_dispatched = cursor.execute(
                    SQL("SELECT dispatched FROM upload_sets WHERE id = %(upload_set_id)s"),
                    {"upload_set_id": upload_set_id},
                ).fetchone()

                if us_dispatched[0] is True:
                    # if the upload set is already dispatched, we propagate the semantic update to all the associated collections
                    # Note that there is a lock on the `upload_sets` row to avoid updating the semantics while dispatching the upload set
                    associated_cols = conn.execute("SELECT id FROM sequences WHERE upload_set_id = %s", [upload_set_id]).fetchall()
                    for c in associated_cols:
                        col_id = c[0]
                        semantics.update_tags(
                            cursor=cursor,
                            entity=semantics.Entity(semantics.EntityType.seq, col_id),
                            actions=sem,
                            account=account.id if account is not None else None,
                        )

        if params.model_fields_set != {"semantics"}:
            # if there was other fields to update
            db_params = model_query.get_db_params_and_values(params)

            conn.execute(
                SQL("UPDATE upload_sets SET {fields} WHERE id = %(upload_set_id)s").format(fields=db_params.fields_for_set()),
                db_params.params_as_dict | {"upload_set_id": upload_set_id},
            )
    # we get a full uploadset response
    return get_upload_set(upload_set_id)


@bp.route("/upload_sets", methods=["POST"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def postUploadSet(account=None):
    """Create a new UploadSet

    The UploadSet are used to group pictures during an upload.
    The pictures will be dispatch to several collections when the UploadSet will be completed
    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - in: header
          name: User-Agent
          required: false
          schema:
            type: string
          description: An explicit User-Agent value is preferred if you create a production-ready tool, formatted like "GeoVisioCLI/1.0"
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostUploadSet'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSet'
    """

    if request.is_json and request.json is not None:
        try:
            params = UploadSetCreationParameter(user_agent=request.user_agent.string, **request.json)
        except ValidationError as ve:
            raise errors.InvalidAPIUsage(_("Impossible to create an UploadSet"), payload=validation_error(ve))
    else:
        raise errors.InvalidAPIUsage(_("Parameter for creating an UploadSet should be a valid JSON"), status_code=415)

    params.validate()
    account_id = UUID(accountIdOrDefault(account))

    upload_set = create_upload_set(params, account_id)

    return (
        upload_set.model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",  # Needed for allowing web browsers access Location header
            "Location": url_for("upload_set.getUploadSet", _external=True, upload_set_id=upload_set.id),
        },
    )


@bp.route("/upload_sets/<uuid:upload_set_id>", methods=["PATCH"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def patchUploadSet(upload_set_id, account=None):
    """Update an existing UploadSet.

    For most fields, only the owner of the UploadSet can update it. The only exception is the `semantics` field, which can be updated by any user.

    Note that the upload set will not be dispatched again, so if you changed the dispatch parameters (like split_distance, split_time, duplicate_distance, duplicate_rotation, relative_heading, ...), you need to call the `POST /api/upload_sets/:id/complete` endpoint to dispatch the upload set afterward.
    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/UploadSetUpdateParameter'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSet'
    """

    if request.is_json and request.json is not None:
        try:
            params = UploadSetUpdateParameter(**request.json)
        except ValidationError as ve:
            raise errors.InvalidAPIUsage(_("Impossible to update the UploadSet"), payload=validation_error(ve))
    else:
        raise errors.InvalidAPIUsage(_("Parameter for updating an UploadSet should be a valid JSON"), status_code=415)

    params.validate()
    upload_set = get_simple_upload_set(upload_set_id)
    if upload_set is None:
        raise errors.InvalidAPIUsage(_("UploadSet doesn't exist"), status_code=404)

    if account and str(upload_set.account_id) != account.id:
        if not params.has_only_semantics_updates():
            raise errors.InvalidAPIUsage(_("You are not allowed to update this upload set"), status_code=403)

    if not params.model_fields_set:
        # nothing to update, return the upload set
        upload_set = get_upload_set(upload_set_id)
    else:
        upload_set = update_upload_set(upload_set_id, params, account)

    return upload_set.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/upload_sets/<uuid:upload_set_id>", methods=["GET"])
def getUploadSet(upload_set_id):
    """Get an existing UploadSet

    The UploadSet are used to group pictures during an upload.
    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet to retrieve
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSet'
    """
    upload_set = get_upload_set(upload_set_id)
    if upload_set is None:
        raise errors.InvalidAPIUsage(_("UploadSet doesn't exist"), status_code=404)

    return upload_set.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/upload_sets/<uuid:upload_set_id>/files", methods=["GET"])
def getUploadSetFiles(upload_set_id):
    """List the files of an UploadSet
    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet files list
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSetFiles'
    """
    account = utils.auth.get_current_account()

    u = get_simple_upload_set(upload_set_id)
    if u is None:
        raise errors.InvalidAPIUsage(_("UploadSet doesn't exist"), status_code=404)

    upload_set_files = get_upload_set_files(upload_set_id)

    if account is None or account.id != str(u.account_id):
        # if the user is not the owner of the upload set, we remove the picture_id since we might leak too many information
        # not sure about this one, this could evolve in the future
        for f in upload_set_files.files:
            f.picture_id = None

    return upload_set_files.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


class ListUploadSetParameter(BaseModel):
    """Parameters used to list a user's UploadSet"""

    account_id: UUID
    limit: int = Field(default=100, ge=0, le=1000)
    filter: Optional[str] = "dispatched = FALSE"
    """Filter to apply to the list of UploadSet. The filter should be a valid SQL WHERE clause"""


@bp.route("/users/me/upload_sets", methods=["GET"])
@auth.login_required_with_redirect()
def listUserUpload(account):
    """List the upload of a user

    The UploadSet are used to group pictures during an upload.
    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - $ref: '#/components/parameters/UploadSetFilter'
        - name: limit
          in: query
          description: limit to the number of upload set to retrieve
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 100
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSets'
    """
    try:
        params = ListUploadSetParameter(account_id=UUID(account.id), **request.args)
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    upload_sets = list_upload_sets(account_id=params.account_id, limit=params.limit, filter=params.filter)

    return upload_sets.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


# Note: class used to generate documentation
class AddFileToUploadSetParameter(BaseModel):
    """Parameters used to add an item to an UploadSet"""

    override_capture_time: Optional[datetime] = None
    """Override the capture time of the picture. The new capture time will also be persisted in the picture's exif tags"""
    override_longitude: Optional[float] = None
    """Override the longitude of the picture. The new longitude will also be persisted in the picture's exif tags"""
    override_latitude: Optional[float] = None
    """Override the latitude of the picture. The new latitude will also be persisted in the picture's exif tags"""

    extra_exif: Optional[Dict[str, str]] = None
    """Extra Exif metadata can be added to the picture. They need to be named `override_` and have the full exiv2 path of the tag.
    For example, to override the `Exif.Image.Orientation` tag, you should use `override_Exif.Image.Orientation` as the key"""

    """External metadata to add to the picture"""
    isBlurred: bool = False
    """True if the picture is already blurred, False otherwise"""

    file: bytes
    """File to upload"""

    model_config = ConfigDict(use_attribute_docstrings=True)

    @field_validator("override_capture_time", mode="before")
    @classmethod
    def parse_capture_time(cls, value):
        if value is None:
            return None
        return parse_datetime(
            value,
            error=_(
                "Parameter `override_capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z')."
            ),
        )

    @field_validator("override_longitude")
    @classmethod
    def parse_longitude(cls, value):
        return as_longitude(value, error=_("For parameter `override_longitude`, `%(v)s` is not a valid longitude", v=value))

    @field_validator("override_latitude")
    @classmethod
    def parse_latitude(cls, value):
        return as_latitude(value, error=_("For parameter `override_latitude`, `%(v)s` is not a valid latitude", v=value))

    @model_validator(mode="before")
    @classmethod
    def parse_extra_exif(cls, values: Dict) -> Dict:
        # Check if others override elements were given
        exif = {}
        override_exif = [k for k in values.keys() if (k.startswith("override_Exif.") or k.startswith("override_Xmp."))]
        for k in override_exif:
            v = values.pop(k)
            exif_tag = k.replace("override_", "")
            exif[exif_tag] = v

        values["extra_exif"] = exif

        return values

    @model_validator(mode="after")
    def validate(self):
        if self.override_latitude is None and self.override_longitude is not None:
            raise errors.InvalidAPIUsage(_("Longitude cannot be overridden alone, override_latitude also needs to be set"))
        if self.override_longitude is None and self.override_latitude is not None:
            raise errors.InvalidAPIUsage(_("Latitude cannot be overridden alone, override_longitude also needs to be set"))
        return self


# Note: class used to store parameters
@dataclass
class AddFileToUploadSetParsedParameter:
    file: FileStorage
    ext_mtd: Optional[PictureMetadata] = None
    isBlurred: bool = False

    file_type: FileType = Field(exclude=True)


class TrackedFileException(errors.InvalidAPIUsage):
    def __init__(
        self,
        message: str,
        rejection_status: FileRejectionStatus,
        payload=None,
        status_code: int = 400,
        file: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message=message, status_code=status_code, payload=payload)
        self.rejection_status = rejection_status
        self.file = file


def _read_add_items_params(form, files) -> AddFileToUploadSetParsedParameter:

    if "file" not in files:
        # Note: we do not want to track this as it is a bad use of the API
        raise errors.InvalidAPIUsage(_("No file was sent"), status_code=400)
    # Note: for the moment we only accept `picture` in files, but later we might accept more kind of files (like gpx traces, video, ...) and autodetect them here
    file_type = FileType.picture

    file = files["file"]
    if not (file.filename and "." in file.filename and file.filename.rsplit(".", 1)[1].lower() in ["jpg", "jpeg"]):
        raise TrackedFileException(
            _("Picture file is either missing or in an unsupported format (should be jpg)"),
            rejection_status=FileRejectionStatus.invalid_file,
            file=dict(file_name=os.path.basename(file.filename), file_type=file_type),
        )

    try:
        params = AddFileToUploadSetParameter(file=b"", **form)
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    # Check if datetime was given
    if (
        params.override_capture_time is not None
        or params.override_latitude is not None
        or params.override_longitude is not None
        or params.extra_exif
    ):
        ext_mtd = PictureMetadata(
            capture_time=params.override_capture_time,
            latitude=params.override_latitude,
            longitude=params.override_longitude,
            additional_exif=params.extra_exif,
        )
    else:
        ext_mtd = None

    return AddFileToUploadSetParsedParameter(ext_mtd=ext_mtd, isBlurred=params.isBlurred, file=file, file_type=file_type)


def un_complete_upload_set(cursor, upload_set_id: UUID):
    """Marks the upload set as uncompleted"""
    cursor.execute(
        "UPDATE upload_sets SET completed = FALSE WHERE id = %(id)s",
        {"id": upload_set_id},
    )


def mark_upload_set_completed_if_needed(cursor, upload_set_id: UUID) -> bool:
    """
    Marks the upload set as completed if the number of pictures in the upload set
    is greater than or equal to the estimated number of files.

    Args:
        cursor: The database cursor object.
        upload_set_id: The ID of the upload set.

    Returns:
        bool: True if the upload set is marked as completed, False otherwise.
    """
    r = cursor.execute(
        """WITH nb_items AS (
            SELECT count(*) AS nb, upload_set_id
            FROM files f
            WHERE upload_set_id = %(id)s
            GROUP BY upload_set_id
        )
        UPDATE upload_sets
        SET completed = (nb_items.nb = estimated_nb_files)
        FROM nb_items
        WHERE id = %(id)s AND estimated_nb_files IS NOT NULL
        RETURNING completed;""",
        {"id": upload_set_id},
    ).fetchone()

    return r is not None and r["completed"]


def handle_completion(cursor, upload_set):
    """
    At the end of an upload, we need to check if the upload needs to be completed or not
     * If is not yet completed, we check if we received the expected number of files
     * If is already completed, we mark it as uncompleted as we don't know if the client will send more pictures
    """
    if not upload_set["completed"]:
        mark_upload_set_completed_if_needed(cursor, upload_set["id"])
    else:
        # if the upload set is already completed and some pictures were added, we need to mark it as uncompleted as we don't know if the client will send more pictures
        un_complete_upload_set(cursor, upload_set["id"])


@bp.route("/upload_sets/<uuid:upload_set_id>/files", methods=["POST"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def addFilesToUploadSet(upload_set_id: UUID, account=None):
    """Add files to an UploadSet

    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet
          required: true
          schema:
            type: string
    requestBody:
        content:
            multipart/form-data:
                schema:
                    $ref: '#/components/schemas/GeoVisioAddToUploadSet'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        202:
            description: The UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSetFile'
        400:
            description: Error if the request is malformed
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        401:
            description: Error if you're not logged in
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        403:
            description: Error if you're not authorized to add picture to this upload set
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        404:
            description: Error if the UploadSet doesn't exist
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        409:
            description: Error if the item has already been added to this upload set or to another upload set
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        415:
            description: Error if the content type is not multipart/form-data
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
    """

    if not request.headers.get("Content-Type", "").startswith("multipart/form-data") or request.form is None:
        raise errors.InvalidAPIUsage(_("Content type should be multipart/form-data"), status_code=415)

    with db.conn(current_app) as conn:
        try:
            with conn.transaction(), conn.cursor(row_factory=dict_row) as cursor:
                upload_set = cursor.execute("SELECT id, account_id, completed FROM upload_sets WHERE id = %s", [upload_set_id]).fetchone()
                if not upload_set:
                    raise errors.InvalidAPIUsage(_("UploadSet %(u)s does not exist", u=upload_set_id), status_code=404)

                # Account associated to uploadset doesn't match current user
                if account is not None and account.id != str(upload_set["account_id"]):
                    raise errors.InvalidAPIUsage(_("You're not authorized to add picture to this upload set"), status_code=403)

                # parse params
                params = _read_add_items_params(request.form, request.files)

                file: Dict[str, Any] = dict(
                    file_name=os.path.basename(params.file.filename or ""),
                    file_type=params.file_type,
                )
                # Compute various metadata
                accountId = accountIdOrDefault(account)
                raw_pic = params.file.read()
                filesize = len(raw_pic)
                file["size"] = filesize

                with sentry_sdk.start_span(description="computing md5"):
                    # we save the content hash md5 as uuid since md5 is 128bit and uuid are efficiently handled in postgres
                    md5 = hashlib.md5(raw_pic).digest()
                    md5 = UUID(bytes=md5)
                    file["content_md5"] = md5

                additionalMetadata = {
                    "blurredByAuthor": params.isBlurred,
                    "originalFileName": os.path.basename(params.file.filename),  # type: ignore
                    "originalFileSize": filesize,
                    "originalContentMd5": md5,
                }

                # check if items already exists
                same_pics = cursor.execute(
                    "SELECT id AS existing_item_id, upload_set_id FROM pictures WHERE original_content_md5 = %s", [md5]
                ).fetchall()
                if same_pics:
                    same_pics_in_same_upload_set = next(
                        (p["existing_item_id"] for p in same_pics if p["upload_set_id"] == upload_set_id), None
                    )
                    if same_pics_in_same_upload_set:
                        # same picture sent twice in the same upload set is likely a client error, we don't keep track of it
                        # it's especially important since for the moment we can't track 2 files with the same name in the same uploadset
                        raise errors.InvalidAPIUsage(
                            _("The item has already been added to this upload set"),
                            status_code=409,
                            payload={"existing_item": {"id": same_pics_in_same_upload_set}},
                        )
                    if current_app.config["API_ACCEPT_DUPLICATE"] is False:
                        # If the picture has been sent in another upload set, we reject it and track it as file sent (to advance the counter to the completion)
                        raise TrackedFileException(
                            _("The same picture has already been sent in a past upload"),
                            payload={"upload_sets": same_pics},
                            rejection_status=FileRejectionStatus.file_duplicate,
                            status_code=409,
                            file=file,
                        )

                # Update picture metadata if needed
                if params.ext_mtd:
                    with sentry_sdk.start_span(description="overwriting metadata"):
                        raw_pic = writePictureMetadata(raw_pic, params.ext_mtd)

                # Insert picture into database
                with sentry_sdk.start_span(description="Insert picture in db"):

                    try:
                        picId = utils.pictures.insertNewPictureInDatabase(
                            db=conn,
                            sequenceId=None,
                            position=None,
                            pictureBytes=raw_pic,
                            associatedAccountID=accountId,
                            additionalMetadata=additionalMetadata,
                            uploadSetID=upload_set_id,
                            lang=get_locale().language,
                        )
                    except utils.pictures.MetadataReadingError as e:
                        raise TrackedFileException(
                            _("Impossible to parse picture metadata"),
                            payload={"details": {"error": e.details, "missing_fields": e.missing_mandatory_tags}},
                            rejection_status=FileRejectionStatus.invalid_metadata,
                            file=file,
                        )
                    except utils.pictures.InvalidMetadataValue as e:
                        raise TrackedFileException(
                            _("Picture has invalid metadata"),
                            payload={"details": {"error": e.details}},
                            rejection_status=FileRejectionStatus.invalid_metadata,
                            file=file,
                        )
                    except PIL.UnidentifiedImageError as e:
                        logging.warning("Impossible to open file as an image: " + str(e))
                        raise TrackedFileException(
                            _("Impossible to open file as image. The only supported image format is jpg."),
                            rejection_status=FileRejectionStatus.invalid_file,
                            file=file,
                        )

                    # persist the file in the database
                    file = utils.upload_set.insertFileInDatabase(
                        cursor=cursor,
                        upload_set_id=upload_set_id,
                        picture_id=picId,
                        **file,
                    )
                # Save file into appropriate filesystem
                with sentry_sdk.start_span(description="Saving picture"):
                    try:
                        utils.pictures.saveRawPicture(picId, raw_pic, params.isBlurred)
                    except:
                        logging.exception("Picture wasn't correctly saved in filesystem")
                        raise errors.InvalidAPIUsage(_("Picture wasn't correctly saved in filesystem"), status_code=500)

                handle_completion(cursor, upload_set)
        except TrackedFileException as e:
            # something went wrong, we reject the file, but keep track of it
            with conn.transaction(), conn.cursor(row_factory=dict_row) as cursor:
                msg = e.message
                d = None
                if e.payload and e.payload.get("details", {}).get("error") is not None:
                    d = deepcopy(e.payload["details"])
                    msg = d.pop("error")

                utils.upload_set.insertFileInDatabase(
                    cursor=cursor,
                    upload_set_id=upload_set_id,
                    **e.file,
                    rejection_status=e.rejection_status,
                    rejection_message=msg,
                    rejection_details=d,
                )
                handle_completion(cursor, upload_set)
            raise e

    # prepare the picture in the background
    current_app.background_processor.process_pictures()  # type: ignore

    # Return picture metadata
    return (
        file.model_dump_json(exclude_none=True),
        202,
        {
            "Content-Type": "application/json",
        },
    )


@bp.route("/upload_sets/<uuid:upload_set_id>/complete", methods=["POST"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def completeUploadSet(upload_set_id: UUID, account=None):
    """Complete an UploadSet

    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the UploadSet metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUploadSet'
    """

    with db.conn(current_app) as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            upload_set = cursor.execute("SELECT account_id, completed FROM upload_sets WHERE id = %s", [upload_set_id]).fetchone()
            if not upload_set:
                raise errors.InvalidAPIUsage(_("UploadSet %(u)s does not exist", u=upload_set_id), status_code=404)

            # Account associated to uploadset doesn't match current user
            if account is not None and account.id != str(upload_set["account_id"]):
                raise errors.InvalidAPIUsage(_("You're not authorized to complete this upload set"), status_code=403)

            cursor.execute("UPDATE upload_sets SET completed = True WHERE id = %(id)s", {"id": upload_set_id})

    # dispatch the upload_set in the background
    current_app.background_processor.process_pictures()  # type: ignore

    # query again the upload set, to get the updated status
    upload_set = get_upload_set(upload_set_id)
    if upload_set is None:
        raise errors.InvalidAPIUsage(_("UploadSet doesn't exist"), status_code=404)

    return upload_set.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/upload_sets/<uuid:upload_set_id>", methods=["DELETE"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def deleteUploadSet(upload_set_id: UUID, account=None):
    """Delete an UploadSet

    Deleting an UploadSet will delete all the pictures of the UploadSet, and all the associated collections will be marked as deleted.

    ---
    tags:
        - Upload
        - UploadSet
    parameters:
        - name: upload_set_id
          in: path
          description: ID of the UploadSet
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        204:
            description: The UploadSet has been correctly deleted
    """

    upload_set = get_upload_set(upload_set_id)

    if not upload_set:
        raise errors.InvalidAPIUsage(_("UploadSet %(u)s does not exist", u=upload_set_id), status_code=404)
    # Account associated to uploadset doesn't match current user
    if account is not None and account.id != str(upload_set.account_id):
        raise errors.InvalidAPIUsage(_("You're not authorized to delete this upload set"), status_code=403)

    utils.upload_set.delete(upload_set)

    # run background task to delete the associated pictures
    current_app.background_processor.process_pictures()  # type: ignore

    return "", 204
