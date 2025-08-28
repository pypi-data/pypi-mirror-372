from enum import Enum
from geovisio import errors, utils, db
from geovisio.utils import auth, sequences
from geovisio.utils.params import validation_error
from geovisio.utils.semantics import Entity, EntityType, update_tags
from geovisio.utils.tags import SemanticTagUpdate
from geovisio.web.params import (
    parse_datetime,
    parse_datetime_interval,
    parse_bbox,
    parse_collection_filter,
    parse_collection_sortby,
    parse_collections_limit,
)
from geovisio.utils.sequences import (
    STAC_FIELD_MAPPINGS,
    CollectionsRequest,
    get_collections,
    get_dataset_bounds,
)
from geovisio.utils.fields import SortBy, SortByField, SQLDirection, BBox, parse_relative_heading
from geovisio.web.rss import dbSequencesToGeoRSS
from psycopg.rows import dict_row
from psycopg.sql import SQL
from pydantic import BaseModel, Field, ValidationError, field_validator
from flask import current_app, request, url_for, Blueprint, stream_with_context
from flask_babel import gettext as _
from geovisio.web.utils import (
    STAC_VERSION,
    accountIdOrDefault,
    cleanNoneInDict,
    cleanNoneInList,
    dbTsToStac,
    get_license_link,
    get_root_link,
    removeNoneInDict,
)
from typing import List, Optional


bp = Blueprint("stac_collections", __name__, url_prefix="/api")


class UploadClient(Enum):
    unknown = "unknown"
    other = "other"
    website = "website"
    cli = "cli"
    mobile_app = "mobile_app"


def userAgentToClient(user_agent: Optional[str] = None) -> UploadClient:
    """Transforms an open user agent string into a limited set of clients."""
    if user_agent is None:
        return UploadClient.unknown

    software = user_agent.split("/")[0].lower().strip()

    if software == "geovisiocli" or software == "panoramaxcli":
        return UploadClient.cli
    elif software == "geovisiowebsite":
        return UploadClient.website
    elif software == "panoramaxapp":
        return UploadClient.mobile_app
    else:
        return UploadClient.other


def dbSequenceToStacCollection(dbSeq, description="A sequence of geolocated pictures"):
    """Transforms a sequence extracted from database into a STAC Collection

    Parameters
    ----------
    dbSeq : dict
        A row from sequences table in database (with id, name, minx, miny, maxx, maxy, mints, maxts fields)
    request
    current_app

    Returns
    -------
    object
        The equivalent in STAC Collection format
    """
    mints, maxts = dbSeq.get("mints"), dbSeq.get("maxts")
    nb_pic = int(dbSeq.get("nbpic")) if "nbpic" in dbSeq else None
    return removeNoneInDict(
        {
            "type": "Collection",
            "stac_version": STAC_VERSION,
            "stac_extensions": [
                "https://stac-extensions.github.io/stats/v0.2.0/schema.json",  # For stats: fields
                "https://stac.linz.govt.nz/v0.0.15/quality/schema.json",  # For quality: fields
            ],
            "id": str(dbSeq["id"]),
            "title": str(dbSeq["name"]),
            "description": description,
            "keywords": ["pictures", str(dbSeq["name"])],
            "semantics": dbSeq.get("semantics", []),
            "license": current_app.config["API_PICTURES_LICENSE_SPDX_ID"],
            "created": dbTsToStac(dbSeq["created"]),
            "updated": dbTsToStac(dbSeq.get("updated")),
            "geovisio:status": (
                dbSeq.get("status") if dbSeq.get("status") != "ready" else None
            ),  # we do not want to add a `geovisio:status` = 'ready', we only use it for hidden/deleted status
            "geovisio:sorted-by": dbSeq.get("current_sort"),
            "geovisio:upload-software": userAgentToClient(dbSeq.get("user_agent")).value,
            "geovisio:length_km": dbSeq.get("length_km"),
            "quality:horizontal_accuracy": (
                float("{:.1f}".format(dbSeq["computed_gps_accuracy"])) if dbSeq.get("computed_gps_accuracy") else None
            ),
            "quality:horizontal_accuracy_type": "95% confidence interval" if "computed_gps_accuracy" in dbSeq else None,
            "providers": [
                {"name": dbSeq["account_name"], "roles": ["producer"], "id": str(dbSeq["account_id"])},
            ],
            "extent": {
                "spatial": {"bbox": [[dbSeq["minx"] or -180.0, dbSeq["miny"] or -90.0, dbSeq["maxx"] or 180.0, dbSeq["maxy"] or 90.0]]},
                "temporal": {
                    "interval": [
                        [
                            dbTsToStac(mints),
                            dbTsToStac(maxts),
                        ]
                    ]
                },
            },
            "summaries": cleanNoneInDict(
                {
                    "pers:interior_orientation": dbSeq.get("metas"),
                    "panoramax:horizontal_pixel_density": (
                        [dbSeq["computed_h_pixel_density"]] if "computed_h_pixel_density" in dbSeq else None
                    ),
                }
            ),
            "stats:items": removeNoneInDict({"count": nb_pic}),
            "links": cleanNoneInList(
                [
                    (
                        {
                            "rel": "items",
                            "type": "application/geo+json",
                            "title": "Pictures in this sequence",
                            "href": url_for("stac_items.getCollectionItems", _external=True, collectionId=dbSeq["id"]),
                        }
                        if not str(dbSeq["id"]).startswith("user:")
                        else None
                    ),
                    {
                        "rel": "parent",
                        "type": "application/json",
                        "title": "Instance catalog",
                        "href": url_for("stac.getLanding", _external=True),
                    },
                    get_root_link(),
                    {
                        "rel": "self",
                        "type": "application/json",
                        "title": "Metadata of this sequence",
                        "href": url_for("stac_collections.getCollection", _external=True, collectionId=dbSeq["id"]),
                    },
                    get_license_link(),
                    (
                        {
                            "rel": "upload_set",
                            "type": "application/json",
                            "title": "Link to the upload set",
                            "href": url_for("upload_set.getUploadSet", _external=True, upload_set_id=dbSeq["upload_set_id"]),
                        }
                        if dbSeq.get("upload_set_id")
                        else None
                    ),
                ]
            ),
        }
    )


@bp.route("/collections")
def getAllCollections():
    """List available collections
    ---
    tags:
        - Sequences
    parameters:
        - $ref: '#/components/parameters/STAC_collections_limit'
        - name: created_after
          in: query
          description: Deprecated, use "filter" parameter instead (`filter=created > some_date`). Filter for collection uploaded after this date. To filter by capture date, use datetime instead.
          required: false
          deprecated: true
          schema:
            type: string
            format: date-time
        - name: created_before
          in: query
          description: Deprecated, use "filter" parameter instead (`filter=created < some_date`). Filter for collection uploaded before this date. To filter by capture date, use datetime instead.
          required: false
          deprecated: true
          schema:
            type: string
            format: date-time
        - name: format
          in: query
          description: Expected output format (STAC JSON or RSS XML)
          required: false
          schema:
            type: string
            enum: [rss, json]
            default: json
        - $ref: '#/components/parameters/STAC_bbox'
        - $ref: '#/components/parameters/STAC_collections_filter'
        - name: datetime
          in: query
          required: false
          schema:
            type: string
          explode: false
          description: >-
            Filter sequence by capture date. To filter by upload date, use "filter" parameter instead.

            You can filter by a single date or a date interval, open or closed.

            Adhere to RFC 3339. Open intervals are expressed using double-dots.

            This endpoint will only answer based on date (not time) value, even
            if time can be set in query (for STAC compatibility purposes).

            Examples:

            * A date-time: "2018-02-12"

            * A closed interval: "2018-02-12/2018-03-18"

            * Open intervals: "2018-02-12/.." or "../2018-03-18"

    responses:
        200:
            description: the list of available collections
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollections'
                application/rss+xml:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionsRSS'
    """

    args = request.args

    # Expected output format
    format = args["format"] if args.get("format") in ["rss", "json"] else "json"
    if (
        args.get("format") is None
        and request.accept_mimetypes.best_match(["application/json", "application/rss+xml"], "application/json") == "application/rss+xml"
    ):
        format = "rss"

    # Sort-by parameter
    sortBy = parse_collection_sortby(request.args.get("sortby"))
    if not sortBy:
        direction = SQLDirection.DESC if format == "rss" else SQLDirection.ASC
        sortBy = SortBy(fields=[SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=direction)])
    # we always add the creation date fields in the sort list (after the selected ones), this will we'll get the `created` bounds of the dataset
    # we'll also get
    if not any(s.field == STAC_FIELD_MAPPINGS["created"] for s in sortBy.fields):
        sortBy.fields.append(SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC))
    if not any(s.field == STAC_FIELD_MAPPINGS["id"] for s in sortBy.fields):
        sortBy.fields.append(SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC))

    collection_request = CollectionsRequest(sort_by=sortBy)

    # Filter parameter
    collection_request.user_filter = parse_collection_filter(request.args.get("filter"))
    collection_request.pagination_filter = parse_collection_filter(request.args.get("page"))

    # Limit parameter
    collection_request.limit = parse_collections_limit(request.args.get("limit"))

    # Datetime
    min_dt, max_dt = parse_datetime_interval(args.get("datetime"))
    collection_request.min_dt = min_dt
    collection_request.max_dt = max_dt

    # Bounding box
    bbox = parse_bbox(args.get("bbox"))
    if bbox:
        collection_request.bbox = BBox(
            minx=bbox[0],
            miny=bbox[1],
            maxx=bbox[2],
            maxy=bbox[3],
        )

    # Created after/before
    created_after = args.get("created_after")
    created_before = args.get("created_before")

    if created_after:
        collection_request.created_after = parse_datetime(created_after, error="Invalid `created_after` argument", fallback_as_UTC=True)

    if created_before:
        collection_request.created_before = parse_datetime(created_before, error="Invalid `created_before` argument", fallback_as_UTC=True)

    links = [
        get_root_link(),
        {"rel": "parent", "type": "application/json", "href": url_for("stac.getLanding", _external=True)},
        {
            "rel": "self",
            "type": "application/json",
            "href": url_for(
                "stac_collections.getAllCollections",
                _external=True,
                limit=args.get("limit"),
                created_after=args.get("created_after"),
            ),
        },
    ]

    with db.conn(current_app) as conn:
        datasetBounds = get_dataset_bounds(conn, collection_request.sort_by, additional_filters=collection_request.user_filter)
        if datasetBounds is None:
            return ({"collections": [], "links": links}, 200, {"Content-Type": "application/json"})
        creation_date_index = collection_request.sort_by.get_field_index("created")
        if collection_request.created_after and collection_request.created_after > datasetBounds.last[creation_date_index]:
            raise errors.InvalidAPIUsage(_("There is no collection created after %(d)s", d=collection_request.created_after))
        if collection_request.created_before and collection_request.created_before < datasetBounds.first[creation_date_index]:
            raise errors.InvalidAPIUsage(_("There is no collection created before %(d)s", d=collection_request.created_before))

    db_collections = get_collections(collection_request)

    # RSS results
    if format == "rss":
        return (dbSequencesToGeoRSS(db_collections.collections).rss(), 200, {"Content-Type": "text/xml"})

    stac_collections = [dbSequenceToStacCollection(c) for c in db_collections.collections]
    pagination_links = []

    additional_filters = request.args.get("filter")

    pagination_links = sequences.get_pagination_links(
        route="stac_collections.getAllCollections",
        routeArgs={"limit": collection_request.limit},
        sortBy=sortBy,
        datasetBounds=datasetBounds,
        dataBounds=db_collections.query_bounds,
        additional_filters=additional_filters,
    )

    # Compute paginated links
    links.extend(pagination_links)

    return (
        {
            "collections": stac_collections,
            "links": links,
        },
        200,
        {"Content-Type": "application/json"},
    )


@bp.route("/collections/<uuid:collectionId>")
def getCollection(collectionId):
    """Retrieve metadata of a single collection
    ---
    tags:
        - Sequences
    parameters:
        - name: collectionId
          in: path
          description: ID of collection to retrieve
          required: true
          schema:
            type: string
    responses:
        200:
            description: the collection metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollection'
    """

    account = auth.get_current_account()

    params = {
        "id": collectionId,
        # Only the owner of an account can view sequence not 'ready'
        "account": account.id if account is not None else None,
    }

    record = db.fetchone(
        current_app,
        """SELECT
                s.id,
                s.metadata->>'title' AS name,
                ST_XMin(s.bbox) AS minx,
                ST_YMin(s.bbox) AS miny,
                ST_XMax(s.bbox) AS maxx,
                ST_YMax(s.bbox) AS maxy,
                s.status AS status,
                accounts.name AS account_name,
                s.account_id AS account_id,
                s.upload_set_id,
                s.inserted_at AS created,
                s.updated_at AS updated,
                s.current_sort AS current_sort,
                a.*,
                min_picture_ts AS mints,
                max_picture_ts AS maxts,
                nb_pictures AS nbpic,
                s.user_agent,
                ROUND(ST_Length(s.geom::geography)) / 1000 as length_km,
                s.computed_h_pixel_density,
                s.computed_gps_accuracy,
                COALESCE(seq_sem.semantics, '[]'::json) AS semantics
            FROM sequences s
            LEFT JOIN (
                SELECT sequence_id, json_agg(json_strip_nulls(json_build_object(
                    'key', key,
                    'value', value
                )) ORDER BY key, value) AS semantics
                FROM sequences_semantics
                GROUP BY sequence_id
            ) seq_sem ON seq_sem.sequence_id = s.id
            JOIN accounts ON s.account_id = accounts.id, (
                SELECT
                    array_agg(DISTINCT jsonb_build_object(
                        'make', metadata->>'make',
                        'model', metadata->>'model',
                        'focal_length', metadata->>'focal_length',
                        'field_of_view', metadata->>'field_of_view'
                    )) AS metas
                FROM pictures p
                JOIN sequences_pictures sp ON sp.seq_id = %(id)s AND sp.pic_id = p.id
            ) a
            WHERE s.id = %(id)s
                AND (s.status != 'hidden' OR s.account_id = %(account)s)
                AND s.status != 'deleted'
        """,
        params,
        row_factory=dict_row,
    )

    if record is None:
        raise errors.InvalidAPIUsage(_("Collection doesn't exist"), status_code=404)

    return (
        dbSequenceToStacCollection(record),
        200,
        {
            "Content-Type": "application/json",
        },
    )


@bp.route("/collections/<uuid:collectionId>/thumb.jpg", methods=["GET"])
def getCollectionThumbnail(collectionId):
    """Get the thumbnail representing a single collection
    ---
    tags:
        - Sequences
    parameters:
        - name: collectionId
          in: path
          description: ID of collection to retrieve
          required: true
          schema:
            type: string
    responses:
        200:
            description: 500px wide ready-for-display image
            content:
                image/jpeg:
                    schema:
                        type: string
                        format: binary
    """
    account = auth.get_current_account()

    params = {
        "seq": collectionId,
        # Only the owner of an account can view pictures not 'ready'
        "account": account.id if account is not None else None,
    }

    records = db.fetchone(
        current_app,
        """SELECT
                sp.pic_id
            FROM sequences_pictures sp
            JOIN pictures p ON sp.pic_id = p.id
            JOIN sequences s ON sp.seq_id = s.id
            WHERE
                sp.seq_id = %(seq)s
                AND (p.status = 'ready' OR p.account_id = %(account)s)
                AND is_sequence_visible_by_user(s, %(account)s)
            ORDER BY RANK ASC
            LIMIT 1""",
        params,
        row_factory=dict_row,
    )

    if records is None:
        raise errors.InvalidAPIUsage(_("Impossible to find a thumbnail for the collection"), status_code=404)

    return utils.pictures.sendThumbnail(records["pic_id"], "jpg")


@bp.route("/collections", methods=["POST"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def postCollection(account=None):
    """Create a new sequence

    Note that this is the legacy API, upload should be done using the [UploadSet](#UploadSet) endpoints if possible.

    Using an upload set makes it possible to handle more use cases like dispatching pictures into several collections, removing capture duplicates, parralele upload, ...
    ---
    tags:
        - Upload
    parameters:
        - in: header
          name: User-Agent
          required: false
          schema:
            type: string
          description: An explicit User-Agent value is preferred if you create a production-ready tool, formatted like "PanoramaxCLI/1.0"
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostCollection'
            application/x-www-form-urlencoded:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostCollection'
            multipart/form-data:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostCollection'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the collection metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollection'
    """

    # Parse received parameters
    metadata = {}
    content_type = request.headers.get("Content-Type")
    if request.is_json and request.json:
        metadata["title"] = request.json.get("title")
    elif content_type in ["multipart/form-data", "application/x-www-form-urlencoded"]:
        metadata["title"] = request.form.get("title")

    metadata = removeNoneInDict(metadata)

    # Create sequence folder
    accountId = accountIdOrDefault(account)
    seqId = sequences.createSequence(metadata, accountId, request.user_agent.string)

    # Return created sequence
    return (
        getCollection(seqId)[0],
        200,
        {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",  # Needed for allowing web browsers access Location header
            "Location": url_for("stac_collections.getCollection", _external=True, collectionId=seqId),
        },
    )


class PatchCollectionParameter(BaseModel):
    """Parameters used to add an item to an UploadSet"""

    relative_heading: Optional[int] = None
    """The relative heading (in degrees), offset based on movement path (0° = looking forward, -90° = looking left, 90° = looking right). For single picture collections, 0° is heading north). Headings are unchanged if this parameter is not set."""
    visible: Optional[bool] = None
    """Should the sequence be publicly visible ?"""
    title: Optional[str] = Field(max_length=250, default=None)
    """The sequence title (publicly displayed)"""
    sortby: Optional[str] = None
    """Define the pictures sort order based on given property. Sort order is defined based on preceding '+' (asc) or '-' (desc).

Available properties are:
* `gpsdate`: sort by GPS datetime
* `filedate`: sort by the camera-generated capture date. This is based on EXIF tags `Exif.Image.DateTimeOriginal`, `Exif.Photo.DateTimeOriginal`, `Exif.Image.DateTime` or `Xmp.GPano.SourceImageCreateTime` (in this order).
* `filename`: sort by the original picture file name

If unset, sort order is unchanged."""
    semantics: Optional[List[SemanticTagUpdate]] = None
    """Tags to update on the picture. By default each tag will be added to the picture's tags, but you can change this behavior by setting the `action` parameter to `delete`.
    
    Like:
[
    {"key": "some_key", "value": "some_value", "action": "delete"},
    {"key": "some_key", "value": "some_new_value"}
]

    Note that updating tags is only possible with JSON data, not with form-data."""

    def has_override(self) -> bool:
        return self.model_fields_set

    @field_validator("visible", mode="before")
    @classmethod
    def parse_visible(cls, value):
        if value not in ["true", "false"]:
            raise errors.InvalidAPIUsage(_("Picture visibility parameter (visible) should be either unset, true or false"), status_code=400)
        return value == "true"

    @field_validator("sortby", mode="before")
    @classmethod
    def check_sortby(cls, value):
        if value not in ["+gpsdate", "-gpsdate", "+filedate", "-filedate", "+filename", "-filename"]:
            raise errors.InvalidAPIUsage(_("Sort order parameter is invalid"), status_code=400)
        return value

    @field_validator("relative_heading", mode="before")
    @classmethod
    def parse_relative_heading(cls, value):
        return parse_relative_heading(value)

    def has_only_semantics_updates(self):
        return self.model_fields_set == {"semantics"}


@bp.route("/collections/<uuid:collectionId>", methods=["PATCH"])
@auth.login_required()
def patchCollection(collectionId, account):
    """Edits properties of an existing collection

    Note that there are rules on the editing of a sequence's metadata:

    - Only the owner of a picture can change its visibility and title
    - For core metadata (relative_heading, sort_by), the owner can restrict their change by other accounts (see `collaborative_metadata` field in `/api/users/me`) and if not explicitly defined by the user, the instance's default value is used.
    - Everyone can add/edit/delete semantics tags.
    ---
    tags:
        - Editing
        - Semantics
    parameters:
        - name: collectionId
          in: path
          description: The sequence ID
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchCollection'
            application/x-www-form-urlencoded:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchCollection'
            multipart/form-data:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchCollection'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the wanted collection
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollection'
    """

    # Parse received parameters
    content_type = (request.headers.get("Content-Type") or "").split(";")[0]
    metadata = None
    try:
        if request.is_json and request.json:
            metadata = PatchCollectionParameter(**request.json)
        elif content_type in ["multipart/form-data", "application/x-www-form-urlencoded"]:
            metadata = PatchCollectionParameter(**request.form)
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    # If no parameter is changed, no need to contact DB, just return sequence as is
    if metadata is None or not metadata.has_override():
        return getCollection(collectionId)

    # Check if sequence exists and if given account is authorized to edit
    with db.conn(current_app) as conn:
        with conn.transaction():
            with conn.cursor(row_factory=dict_row) as cursor:
                seq = cursor.execute(
                    "SELECT status, metadata, account_id, current_sort FROM sequences WHERE id = %s AND status != 'deleted'", [collectionId]
                ).fetchone()

                # Sequence not found
                if not seq:
                    raise errors.InvalidAPIUsage(_("Collection %(c)s wasn't found in database", c=collectionId), status_code=404)

                if account is not None and account.id != str(seq["account_id"]):
                    # Only owner of the sequence is allower to change its visibility and title
                    # tags and headings can be changed by anyone
                    if metadata.visible is not None or metadata.title is not None:
                        raise errors.InvalidAPIUsage(
                            _(
                                "You're not authorized to edit those fields for this sequence. Only the owner can change the visibility and the title"
                            ),
                            status_code=403,
                        )

                    # for core metadata editing (all appart the semantic tags), we check if the user has allowed it
                    if not metadata.has_only_semantics_updates():
                        if not auth.account_allow_collaborative_editing(seq["account_id"]):
                            raise errors.InvalidAPIUsage(
                                _("You're not authorized to edit this sequence, collaborative editing is not allowed"),
                                status_code=403,
                            )

                oldStatus = seq["status"]
                oldMetadata = seq["metadata"]
                oldTitle = oldMetadata.get("title")

                # Check if sequence is in a preparing/broken/... state so no edit possible
                if oldStatus not in ["ready", "hidden"]:
                    if metadata.visible is not None:
                        raise errors.InvalidAPIUsage(
                            _("Sequence %(c)s is in %(s)s state, its visibility can't be changed for now", c=collectionId, s=oldStatus),
                            status_code=400,
                        )

                sqlUpdates = []
                sqlParams = {"id": collectionId, "account": account.id}

                if metadata.visible is not None:
                    newStatus = "ready" if metadata.visible is True else "hidden"
                    if newStatus != oldStatus:
                        sqlUpdates.append(SQL("status = %(status)s"))
                        sqlParams["status"] = newStatus

                new_metadata = {}
                if metadata.title is not None and oldTitle != metadata.title:
                    new_metadata["title"] = metadata.title
                if metadata.relative_heading:
                    new_metadata["relative_heading"] = metadata.relative_heading

                if new_metadata:
                    sqlUpdates.append(SQL("metadata = metadata || %(new_metadata)s"))
                    from psycopg.types.json import Jsonb

                    sqlParams["new_metadata"] = Jsonb(new_metadata)

                if metadata.sortby is not None:
                    sqlUpdates.append(SQL("current_sort = %(sort)s"))
                    sqlParams["sort"] = metadata.sortby

                if len(sqlUpdates) > 0:
                    # Note: we set the field `last_account_to_edit` to track who changed the collection last (later we'll make it possible for everybody to edit some collection fields)
                    # setting this field will trigger the history tracking of the collection (using postgres trigger)
                    sqlUpdates.append(SQL("last_account_to_edit = %(account)s"))

                    cursor.execute(
                        SQL("UPDATE sequences SET {updates} WHERE id = %(id)s").format(updates=SQL(", ").join(sqlUpdates)),
                        sqlParams,
                    )

                # Edits picture sort order
                if metadata.sortby is not None:
                    direction = sequences.Direction(metadata.sortby[0])
                    order = sequences.CollectionSortOrder(metadata.sortby[1:])
                    sequences.sort_collection(cursor, collectionId, sequences.CollectionSort(order=order, direction=direction))
                    if not metadata.relative_heading:
                        # if we do not plan to override headings specifically, we recompute headings that have not bee provided by the users
                        # with the new movement track
                        sequences.update_headings(cursor, collectionId, editingAccount=account.id)

                # Edits relative heading of pictures in sequence
                if metadata.relative_heading is not None:
                    # New heading is computed based on sequence movement track
                    #   We take each picture and its following, compute azimuth,
                    #   then add given relative heading to offset picture heading.
                    #   Last picture is computed based on previous one in sequence.
                    sequences.update_headings(
                        cursor, collectionId, relativeHeading=metadata.relative_heading, updateOnlyMissing=False, editingAccount=account.id
                    )

                if metadata.semantics is not None:
                    # semantic tags are managed separately
                    update_tags(cursor, Entity(type=EntityType.seq, id=collectionId), metadata.semantics, account=account.id)

        # Redirect response to a classic GET
        return getCollection(collectionId)


@bp.route("/collections/<uuid:collectionId>", methods=["DELETE"])
@auth.login_required()
def deleteCollection(collectionId, account):
    """Delete a collection and all the associated pictures
    The associated images will be hidden right away and deleted asynchronously
    ---
    tags:
        - Editing
    parameters:
        - name: collectionId
          in: path
          description: ID of the collection
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        204:
            description: The collection has been correctly deleted
    """
    nb_updated = utils.sequences.delete_collection(collectionId, account)

    # add background task if needed, to really delete pictures
    for _ in range(nb_updated):
        current_app.background_processor.process_pictures()

    return "", 204


@bp.route("/collections/<uuid:collectionId>/geovisio_status")
def getCollectionImportStatus(collectionId):
    """Retrieve import status of all pictures in sequence
    ---
    tags:
        - Upload
    parameters:
        - name: collectionId
          in: path
          description: ID of collection to retrieve
          required: true
          schema:
            type: string
    responses:
        200:
            description: the pictures statuses
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionImportStatus'
    """

    account = auth.get_current_account()
    params = {"seq_id": collectionId, "account": account.id if account is not None else None}
    with db.cursor(current_app, row_factory=dict_row) as cursor:
        sequence_status = cursor.execute(
            SQL(
                """SELECT status 
                FROM sequences
                WHERE id = %(seq_id)s
                    AND (status != 'hidden' OR account_id = %(account)s)-- show deleted sequence here"""
            ),
            params,
        ).fetchone()
        if sequence_status is None:
            raise errors.InvalidAPIUsage(_("Sequence doesn't exists"), status_code=404)

        pics_status = cursor.execute(
            """WITH
pic_jobs_stats AS (
    SELECT
    picture_id,
    (MAX(ARRAY[finished_at::varchar, error]))[2] last_job_error,
    MAX(finished_at) last_job_finished_at,
    (MAX(ARRAY[started_at, finished_at]))[2] IS NULL is_job_running,
    COUNT(job_history.*) as nb_jobs,
    COUNT(job_history.*) FILTER (WHERE job_history.error IS NOT NULL) as nb_errors
    FROM job_history
    WHERE picture_id IN (
        SELECT pic_id from sequences_pictures WHERE seq_id = %(seq_id)s
    )
    GROUP BY picture_id
)
, items AS (
    SELECT
    p.id,
    p.status,
    sp.rank,
    s.id as seq_id,
    pic_jobs_stats.is_job_running,
    pic_jobs_stats.last_job_error,
    pic_jobs_stats.nb_errors,
    pic_jobs_stats.last_job_finished_at
    FROM sequences s
    JOIN sequences_pictures sp ON sp.seq_id = s.id
    JOIN pictures p ON sp.pic_id = p.id
    LEFT JOIN pic_jobs_stats ON pic_jobs_stats.picture_id = p.id
    WHERE
                s.id = %(seq_id)s
                AND (p IS NULL OR p.status != 'hidden' OR p.account_id = %(account)s)
    ORDER BY s.id, sp.rank
)
SELECT json_strip_nulls(
        json_build_object(
            'id', i.id,
            -- status is a bit deprecated, we'll split this field in more fields (like `processing_in_progress`, `hidden`, ...)
            -- but we maintain it for retrocompatibility
            'status', CASE 
                    WHEN i.is_job_running IS TRUE THEN 'preparing' 
                    WHEN i.last_job_error IS NOT NULL THEN 'broken' 
                    ELSE i.status
                END, 
            'processing_in_progress', i.is_job_running,
            'process_error', i.last_job_error,
            'nb_errors', i.nb_errors,
            'processed_at', i.last_job_finished_at,
            'rank', i.rank
        )
    ) as pic_status
FROM items i;""",
            params,
        ).fetchall()
        pics = [p["pic_status"] for p in pics_status if len(p["pic_status"]) > 0]

        return {"status": sequence_status["status"], "items": pics}


def send_collections_as_csv(collection_request: CollectionsRequest):
    """Retrieves all collections of a given user as a CSV file.

    The response is streamed from the database to be more efficient, so for the moment we do not support many parameters
    """
    if collection_request.pagination_filter:
        raise errors.InvalidAPIUsage(_("CSV export does not support pagination"), status_code=400)
    if collection_request.filters():
        raise errors.InvalidAPIUsage(_("CSV export does not support filters"), status_code=400)
    if collection_request.sort_by != SortBy(
        fields=[
            SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.DESC),
            SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC),
        ]
    ):
        raise errors.InvalidAPIUsage(_("CSV export does not support sorting by anything but creation date"), status_code=400)

    def generate_csv():
        # yield f"{','.join([f.name for f in CSV_FIELDS])}\n"
        filters = [SQL("account_id = %(account)s")]
        params = {"account": collection_request.user_id}
        filters.append(SQL("status != 'deleted'") if collection_request.userOwnsAllCollections else SQL("status = 'ready'"))

        with db.cursor(current_app) as cursor:

            with cursor.copy(
                SQL(
                    """COPY (
SELECT 
    s.id AS id,
    s.status AS status,
    s.metadata->>'title' AS name,
    s.inserted_at AS created,
    s.updated_at AS updated,
    s.computed_capture_date AS capture_date,
    s.min_picture_ts AS minimum_capture_time,
    s.max_picture_ts AS maximum_capture_time,
    ST_XMin(s.bbox) AS min_x,
    ST_YMin(s.bbox) AS min_y,
    ST_XMax(s.bbox) AS max_x,
    ST_YMax(s.bbox) AS max_y,
    s.nb_pictures AS nb_pictures,
    ROUND(ST_Length(s.geom::geography)) / 1000 AS length_km,
    s.computed_h_pixel_density AS computed_h_pixel_density,
    s.computed_gps_accuracy AS computed_gps_accuracy
FROM sequences s 
WHERE {filter}
ORDER BY s.inserted_at DESC, id ASC
) TO STDOUT CSV HEADER"""
                ).format(filter=SQL(" AND ").join(filters)),
                params,
            ) as copy:

                for a in copy:
                    yield bytes(a)

    return stream_with_context(generate_csv()), {"Content-Type": "text/csv", "Content-Disposition": "attachment"}


@bp.route("/users/<uuid:userId>/collection")
@auth.isUserIdMatchingCurrentAccount()
def getUserCollection(userId, userIdMatchesAccount=False):
    """Retrieves an collection of the user list collections

    It's quite the same as "/users/<uuid:userId>/catalog/" but with additional information, as a STAC collection have more metadatas than STAC catalogs.

    Links contain information of user sequences (child), as well as pagination links (next/prev).

    Also, links are filtered to match passed conditions, so you can have pagination and filters on client-side.

    Note that on paginated results, filter can only be used with column used in sortby parameter.

    The result can also be a CSV file, if the "Accept" header is set to "text/csv", or if the "format" query parameter is set to "csv".
    Note that when requesting a CSV file, the filters/sortby/pagination parameters are not supported, and `limit` is ignored, you always get the full list of collections.
    ---
    tags:
        - Sequences
        - Users
    parameters:
        - name: userId
          in: path
          description: User ID
          required: true
          schema:
            type: string
        - name: format
          in: query
          description: Expected output format (STAC JSON or a csv file). Note that the CSV format support less parameters than the JSON format (cf documentation).
          required: false
          schema:
            type: string
            enum: [csv, json]
            default: json
        - $ref: '#/components/parameters/STAC_collections_limit'
        - $ref: '#/components/parameters/STAC_collections_filter'
        - $ref: '#/components/parameters/STAC_bbox'
        - $ref: '#/components/parameters/OGC_sortby'
    responses:
        200:
            description: the Collection listing all sequences associated to given user
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionOfCollection'

                text/csv:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCSVCollections'
    """

    # Expected output format
    format = request.args["format"] if request.args.get("format") in ["csv", "json"] else "json"
    if (
        request.args.get("format") is None
        and request.accept_mimetypes.best_match(["application/json", "text/csv"], "application/json") == "text/csv"
    ):
        format = "csv"

    # Sort-by parameter
    sortBy = parse_collection_sortby(request.args.get("sortby"))
    if not sortBy:
        sortBy = SortBy(fields=[SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.DESC)])

    if not any(s.field == STAC_FIELD_MAPPINGS["created"] for s in sortBy.fields):
        sortBy.fields.append(SortByField(field=STAC_FIELD_MAPPINGS["created"], direction=SQLDirection.ASC))
    if not any(s.field == STAC_FIELD_MAPPINGS["id"] for s in sortBy.fields):
        sortBy.fields.append(SortByField(field=STAC_FIELD_MAPPINGS["id"], direction=SQLDirection.ASC))
    collection_request = CollectionsRequest(sort_by=sortBy, userOwnsAllCollections=userIdMatchesAccount)

    # Filter parameter
    collection_request.user_filter = parse_collection_filter(request.args.get("filter"))

    # Filters added by the pagination
    collection_request.pagination_filter = parse_collection_filter(request.args.get("page"))

    # Limit parameter
    # if not specified, the default with CSV it 1000. if there are more, the paginated API should be used
    arg_limit = request.args.get("limit")
    collection_request.limit = parse_collections_limit(arg_limit)
    collection_request.user_id = userId

    # Bounding box
    bbox = parse_bbox(request.args.get("bbox"))
    if bbox:
        collection_request.bbox = BBox(
            minx=bbox[0],
            miny=bbox[1],
            maxx=bbox[2],
            maxy=bbox[3],
        )

    meta_filter = [
        SQL("{field} IS NOT NULL").format(field=collection_request.sort_by.fields[0].field.sql_filter),
        SQL("s.account_id = %(account)s"),
    ]
    if collection_request.user_filter is not None:
        meta_filter.append(collection_request.user_filter)

    if collection_request.user_filter is None or "status" not in collection_request.user_filter.as_string(None):
        # if the filter does not contains any `status` condition, we want to show only 'ready' collection to the general users, and non deleted one for the owner
        if not userIdMatchesAccount:
            meta_filter.extend([SQL("s.status = 'ready'")])
        else:
            meta_filter.append(SQL("s.status != 'deleted'"))

    # Check user account parameter
    with db.cursor(current_app, row_factory=dict_row) as cursor:
        userName = cursor.execute("SELECT name FROM accounts WHERE id = %s", [userId]).fetchone()

        if not userName:
            raise errors.InvalidAPIUsage(_("Impossible to find user %(u)s", u=userId))
        userName = userName["name"]

        if format == "csv":
            return send_collections_as_csv(collection_request)

        meta_collection = cursor.execute(
            SQL(
                """SELECT
                SUM(s.nb_pictures) AS nbpic,
                COUNT(s.id) AS nbseq,
                MIN(s.min_picture_ts) AS mints,
                MAX(s.max_picture_ts) AS maxts,
                MIN(GREATEST(-180, ST_XMin(s.bbox))) AS minx,
                MIN(GREATEST(-90, ST_YMin(s.bbox))) AS miny,
                MAX(LEAST(180, ST_XMax(s.bbox))) AS maxx,
                MAX(LEAST(90, ST_YMax(s.bbox))) AS maxy,
                MIN(s.inserted_at) AS created,
                MAX(s.updated_at) AS updated,
                ROUND(SUM(ST_Length(s.geom::geography))) / 1000 AS length_km
            FROM sequences s
            WHERE {filter}
            """
            ).format(
                filter=SQL(" AND ").join(meta_filter),
                order_column=collection_request.sort_by.fields[0].field.sql_filter,
            ),
            params={"account": userId},
        ).fetchone()

        if not meta_collection or meta_collection["created"] is None:
            # No data found, trying to give the most meaningful error message
            if collection_request.user_filter is None:
                raise errors.InvalidAPIUsage(_("No data loaded for user %(u)s", u=userId), 404)
            else:
                raise errors.InvalidAPIUsage(_("No matching sequences found"), 404)

        datasetBounds = get_dataset_bounds(
            cursor.connection,
            collection_request.sort_by,
            additional_filters=SQL(" AND ").join(meta_filter),
            additional_filters_params={"account": userId},
        )

    collections = get_collections(collection_request)

    sequences_links = [
        removeNoneInDict(
            {
                "id": s["id"],
                "title": s["name"],
                "rel": "child",
                "href": url_for("stac_collections.getCollection", _external=True, collectionId=s["id"]),
                "stats:items": {"count": s["nbpic"]},
                "created": dbTsToStac(s["created"]),
                "updated": dbTsToStac(s["updated"]),
                "extent": {
                    "temporal": {
                        "interval": [
                            [
                                dbTsToStac(s["mints"]),
                                dbTsToStac(s["maxts"]),
                            ]
                        ]
                    },
                    "spatial": {"bbox": [[s["minx"] or -180.0, s["miny"] or -90.0, s["maxx"] or 180.0, s["maxy"] or 90.0]]},
                },
                "geovisio:status": s["status"] if userIdMatchesAccount else None,
                "geovisio:length_km": s.get("length_km"),
            }
        )
        for s in collections.collections
    ]

    meta_collection.update(
        {
            "id": f"user:{userId}",
            "name": f"{userName}'s sequences",
            "account_name": userName,
            "account_id": userId,
        }
    )
    collection = dbSequenceToStacCollection(meta_collection, description=f"List of all sequences of user {userName}")

    collection["stats:collections"] = removeNoneInDict({"count": meta_collection["nbseq"]})
    additional_filters = None
    if collection_request.user_filter is not None:
        # if some filters were given, we continue to pass them to the pagination
        additional_filters = request.args.get("filter")

    pagination_links = sequences.get_pagination_links(
        route="stac_collections.getUserCollection",
        routeArgs={"userId": str(userId), "limit": collection_request.limit},
        sortBy=sortBy,
        datasetBounds=datasetBounds,
        dataBounds=collections.query_bounds,
        additional_filters=additional_filters,
    )

    # add all sub collections as links
    collection["links"].extend(pagination_links + sequences_links)

    # and we update the self link since it's not a collection mapped directly to a sequence
    self = next(l for l in collection["links"] if l["rel"] == "self")
    self["href"] = url_for("stac_collections.getUserCollection", _external=True, userId=str(userId))

    collection["stac_extensions"].append(
        "https://stac-extensions.github.io/timestamps/v1.1.0/schema.json"
    )  # for `updated`/`created` fields in links

    return (collection, 200, {"Content-Type": "application/json"})
