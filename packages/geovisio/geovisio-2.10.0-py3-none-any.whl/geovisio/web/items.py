from datetime import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Any
from urllib.parse import unquote
from psycopg.types.json import Jsonb
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator, model_validator
from shapely import intersects
from werkzeug.datastructures import MultiDict
from uuid import UUID
from geovisio import errors, utils
from geovisio.utils import auth, db
from geovisio.utils.cql2 import parse_search_filter
from geovisio.utils.params import validation_error
from geovisio.utils.pictures import cleanupExif
from geovisio.utils.semantics import Entity, EntityType, update_tags
from geovisio.utils.items import SortableItemField, SortBy, ItemSortByField
from geovisio.utils.tags import SemanticTagUpdate
from geovisio.utils.auth import Account
from geovisio.web.params import (
    as_latitude,
    as_longitude,
    as_uuid,
    parse_datetime,
    parse_datetime_interval,
    parse_bbox,
    parse_item_sortby,
    parse_list,
    parse_lonlat,
    parse_distance_range,
    parse_picture_heading,
)
from geovisio.utils.fields import Bounds, SQLDirection
import hashlib
from psycopg.rows import dict_row
from psycopg.sql import SQL
from geovisio.web.utils import (
    accountIdOrDefault,
    cleanNoneInList,
    dbTsToStac,
    dbTsToStacTZ,
    get_license_link,
    get_root_link,
    removeNoneInDict,
    STAC_VERSION,
)
from flask import current_app, request, url_for, Blueprint
from flask_babel import gettext as _, get_locale
from geopic_tag_reader.writer import writePictureMetadata, PictureMetadata
import sentry_sdk
import math


bp = Blueprint("stac_items", __name__, url_prefix="/api")


def dbPictureToStacItem(dbPic):
    """Transforms a picture extracted from database into a STAC Item

    Parameters
    ----------
    seqId : uuid
        Associated sequence ID
    dbPic : dict
        A row from pictures table in database (with id, geojson, ts, heading, cols, rows, width, height, prevpic, nextpic, prevpicgeojson, nextpicgeojson, exif fields)

    Returns
    -------
    object
        The equivalent in STAC Item format
    """

    sensorDim = None
    visibleArea = None
    seqId = str(dbPic["seq_id"])
    if dbPic["metadata"].get("crop") is not None:
        sensorDim = [dbPic["metadata"]["crop"].get("fullWidth"), dbPic["metadata"]["crop"].get("fullHeight")]
        visibleArea = [
            dbPic["metadata"]["crop"].get("left"),
            dbPic["metadata"]["crop"].get("top"),
            int(dbPic["metadata"]["crop"].get("fullWidth", "0"))
            - int(dbPic["metadata"]["crop"].get("width", "0"))
            - int(dbPic["metadata"]["crop"].get("left", "0")),
            int(dbPic["metadata"]["crop"].get("fullHeight", "0"))
            - int(dbPic["metadata"]["crop"].get("height", "0"))
            - int(dbPic["metadata"]["crop"].get("top", "0")),
        ]
        if None in sensorDim:
            sensorDim = None
        if None in visibleArea or visibleArea == [0, 0, 0, 0]:
            visibleArea = None
    elif "height" in dbPic["metadata"] and "width" in dbPic["metadata"]:
        sensorDim = [dbPic["metadata"]["width"], dbPic["metadata"]["height"]]

    item = removeNoneInDict(
        {
            "type": "Feature",
            "stac_version": STAC_VERSION,
            "stac_extensions": [
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",  # "view:" fields
                "https://stac-extensions.github.io/perspective-imagery/v1.0.0/schema.json",  # "pers:" fields
            ],
            "id": str(dbPic["id"]),
            "geometry": dbPic["geojson"],
            "bbox": dbPic["geojson"]["coordinates"] + dbPic["geojson"]["coordinates"],
            "providers": cleanNoneInList(
                [
                    {"name": dbPic["account_name"], "roles": ["producer"], "id": str(dbPic["account_id"])},
                    (
                        {"name": dbPic["exif"]["Exif.Image.Artist"], "roles": ["producer"]}
                        if dbPic["exif"].get("Exif.Image.Artist") is not None
                        else None
                    ),
                ]
            ),
            "properties": removeNoneInDict(
                {
                    "datetime": dbTsToStac(dbPic["ts"]),
                    "datetimetz": dbTsToStacTZ(dbPic["ts"], dbPic["metadata"].get("tz")),
                    "created": dbTsToStac(dbPic["inserted_at"]),
                    "updated": dbTsToStac(dbPic["updated_at"]),
                    "license": current_app.config["API_PICTURES_LICENSE_SPDX_ID"],
                    "view:azimuth": dbPic["heading"],
                    "pers:interior_orientation": (
                        removeNoneInDict(
                            {
                                "camera_manufacturer": dbPic["metadata"].get("make"),
                                "camera_model": dbPic["metadata"].get("model"),
                                "focal_length": dbPic["metadata"].get("focal_length"),
                                "field_of_view": dbPic["metadata"].get("field_of_view"),
                                "sensor_array_dimensions": sensorDim,
                                "visible_area": visibleArea,
                            }
                        )
                        if "metadata" in dbPic
                        and any(
                            True
                            for f in dbPic["metadata"]
                            if f in ["make", "model", "focal_length", "field_of_view", "crop", "width", "height"]
                        )
                        else {}
                    ),
                    "pers:pitch": dbPic["metadata"].get("pitch"),
                    "pers:roll": dbPic["metadata"].get("roll"),
                    "geovisio:status": dbPic.get("status"),
                    "geovisio:producer": dbPic["account_name"],
                    "geovisio:rank_in_collection": dbPic["rank"],
                    "original_file:size": dbPic["metadata"].get("originalFileSize"),
                    "original_file:name": dbPic["metadata"].get("originalFileName"),
                    "panoramax:horizontal_pixel_density": dbPic.get("h_pixel_density"),
                    "geovisio:image": _getHDJpgPictureURL(dbPic["id"], dbPic.get("status")),
                    "geovisio:thumbnail": _getThumbJpgPictureURL(dbPic["id"], dbPic.get("status")),
                    "exif": removeNoneInDict(cleanupExif(dbPic["exif"])),
                    "quality:horizontal_accuracy": float("{:.1f}".format(dbPic["gps_accuracy_m"])) if dbPic.get("gps_accuracy_m") else None,
                    "semantics": [s for s in dbPic.get("semantics") or [] if s],
                    "annotations": [a for a in dbPic.get("annotations") or [] if a],
                    "collection": {"semantics": dbPic["sequence_semantics"]} if "sequence_semantics" in dbPic else None,
                }
            ),
            "links": cleanNoneInList(
                [
                    get_root_link(),
                    {
                        "rel": "parent",
                        "type": "application/json",
                        "href": url_for("stac_collections.getCollection", _external=True, collectionId=seqId),
                    },
                    {
                        "rel": "self",
                        "type": "application/geo+json",
                        "href": url_for("stac_items.getCollectionItem", _external=True, collectionId=seqId, itemId=dbPic["id"]),
                    },
                    {
                        "rel": "collection",
                        "type": "application/json",
                        "href": url_for("stac_collections.getCollection", _external=True, collectionId=seqId),
                    },
                    get_license_link(),
                ]
            ),
            "assets": {
                "hd": {
                    "title": "HD picture",
                    "description": "Highest resolution available of this picture",
                    "roles": ["data"],
                    "type": "image/jpeg",
                    "href": _getHDJpgPictureURL(dbPic["id"], status=dbPic.get("status")),
                },
                "sd": {
                    "title": "SD picture",
                    "description": "Picture in standard definition (fixed width of 2048px)",
                    "roles": ["visual"],
                    "type": "image/jpeg",
                    "href": _getSDJpgPictureURL(dbPic["id"], status=dbPic.get("status")),
                },
                "thumb": {
                    "title": "Thumbnail",
                    "description": "Picture in low definition (fixed width of 500px)",
                    "roles": ["thumbnail"],
                    "type": "image/jpeg",
                    "href": _getThumbJpgPictureURL(dbPic["id"], status=dbPic.get("status")),
                },
            },
            "collection": str(seqId),
        }
    )

    # Next / previous links if any
    if "nextpic" in dbPic and dbPic["nextpic"] is not None:
        item["links"].append(
            {
                "rel": "next",
                "type": "application/geo+json",
                "geometry": dbPic["nextpicgeojson"],
                "id": dbPic["nextpic"],
                "href": url_for("stac_items.getCollectionItem", _external=True, collectionId=seqId, itemId=dbPic["nextpic"]),
            }
        )

    if "prevpic" in dbPic and dbPic["prevpic"] is not None:
        item["links"].append(
            {
                "rel": "prev",
                "type": "application/geo+json",
                "geometry": dbPic["prevpicgeojson"],
                "id": dbPic["prevpic"],
                "href": url_for("stac_items.getCollectionItem", _external=True, collectionId=seqId, itemId=dbPic["prevpic"]),
            }
        )

    if dbPic.get("related_pics") is not None:
        for rp in dbPic["related_pics"]:
            repSeq, rpId, rpGeom, rpTs = rp
            item["links"].append(
                {
                    "rel": "related",
                    "type": "application/geo+json",
                    "geometry": json.loads(rpGeom),
                    "datetime": rpTs,
                    "id": rpId,
                    "href": url_for("stac_items.getCollectionItem", _external=True, collectionId=repSeq, itemId=rpId),
                }
            )

    #
    # Picture type-specific properties
    #

    # Equirectangular
    if dbPic["metadata"]["type"] == "equirectangular":
        item["stac_extensions"].append("https://stac-extensions.github.io/tiled-assets/v1.0.0/schema.json")  # "tiles:" fields

        item["properties"]["tiles:tile_matrix_sets"] = {
            "geovisio": {
                "type": "TileMatrixSetType",
                "title": "GeoVisio tile matrix for picture " + str(dbPic["id"]),
                "identifier": "geovisio-" + str(dbPic["id"]),
                "tileMatrix": [
                    {
                        "type": "TileMatrixType",
                        "identifier": "0",
                        "scaleDenominator": 1,
                        "topLeftCorner": [0, 0],
                        "tileWidth": dbPic["metadata"]["width"] / dbPic["metadata"]["cols"],
                        "tileHeight": dbPic["metadata"]["height"] / dbPic["metadata"]["rows"],
                        "matrixWidth": dbPic["metadata"]["cols"],
                        "matrixHeight": dbPic["metadata"]["rows"],
                    }
                ],
            }
        }

        item["asset_templates"] = {
            "tiles": {
                "title": "HD tiled picture",
                "description": "Highest resolution available of this picture, as tiles",
                "roles": ["data"],
                "type": "image/jpeg",
                "href": _getTilesJpgPictureURL(dbPic["id"], status=dbPic.get("status")),
            }
        }

    return item


def get_first_rank_of_page(rankToHave: int, limit: Optional[int]) -> int:
    """if there is a limit, we try to emulate a page, so we'll return the nth page that should contain this picture
    Note: the ranks starts from 1
    >>> get_first_rank_of_page(3, 2)
    3
    >>> get_first_rank_of_page(4, 2)
    3
    >>> get_first_rank_of_page(3, None)
    3
    >>> get_first_rank_of_page(123, 10)
    121
    >>> get_first_rank_of_page(10, 10)
    1
    >>> get_first_rank_of_page(10, 100)
    1
    """
    if not limit:
        return rankToHave

    return int((rankToHave - 1) / limit) * limit + 1


@bp.route("/collections/<uuid:collectionId>/items", methods=["GET"])
def getCollectionItems(collectionId):
    """List items of a single collection
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
        - name: limit
          in: query
          description: Number of items that should be present in response. Unlimited by default.
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 10000
        - name: startAfterRank
          in: query
          description: Position of last received picture in sequence. Response will start with the following picture.
          required: false
          schema:
            type: integer
            minimum: 1
        - name: withPicture
          in: query
          description: Used in the pagination context, if present, the api will return the given picture in the results.
            Can be used in the same time as the `limit` parameter, but not with the `startAfterRank` parameter.
          required: false
          schema:
            type: string
            format: uuid
    responses:
        200:
            description: the items list
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionItems'
    """

    account = auth.get_current_account()

    params = {
        "seq": collectionId,
        # Only the owner of an account can view pictures not 'ready'
        "account": account.id if account is not None else None,
    }

    args = request.args
    limit = args.get("limit")
    startAfterRank = args.get("startAfterRank")
    withPicture = args.get("withPicture")

    filters = [
        SQL("sp.seq_id = %(seq)s"),
        SQL("(p.status = 'ready' OR p.account_id = %(account)s)"),
        SQL("(is_sequence_visible_by_user(s, %(account)s))"),
    ]

    # Check if limit is valid
    sql_limit = SQL("")
    if limit is not None:
        try:
            limit = int(limit)
            if limit < 1 or limit > 10000:
                raise errors.InvalidAPIUsage(_("limit parameter should be an integer between 1 and 10000"), status_code=400)
        except ValueError:
            raise errors.InvalidAPIUsage(_("limit parameter should be a valid, positive integer (between 1 and 10000)"), status_code=400)
        sql_limit = SQL("LIMIT %(limit)s")
        params["limit"] = limit

    if withPicture and startAfterRank:
        raise errors.InvalidAPIUsage(_("`startAfterRank` and `withPicture` are mutually exclusive parameters"))

    # Check if rank is valid
    if startAfterRank is not None:
        try:
            startAfterRank = int(startAfterRank)
            if startAfterRank < 1:
                raise errors.InvalidAPIUsage(_("startAfterRank parameter should be a positive integer (starting from 1)"), status_code=400)
        except ValueError:
            raise errors.InvalidAPIUsage(_("startAfterRank parameter should be a valid, positive integer"), status_code=400)

        filters.append(SQL("rank > %(start_after_rank)s"))
        params["start_after_rank"] = startAfterRank

    paginated = startAfterRank is not None or limit is not None or withPicture is not None

    with current_app.pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # check on sequence
            seqMeta = cursor.execute(
                "SELECT s.id "
                + (", MAX(sp.rank) AS max_rank, MIN(sp.rank) AS min_rank " if paginated else "")
                + "FROM sequences s "
                + ("LEFT JOIN sequences_pictures sp ON sp.seq_id = s.id " if paginated else "")
                + "WHERE s.id = %(seq)s AND (is_sequence_visible_by_user(s, %(account)s)) "
                + ("GROUP BY s.id" if paginated else ""),
                params,
            ).fetchone()

            if seqMeta is None:
                raise errors.InvalidAPIUsage(_("Collection doesn't exist"), status_code=404)

            maxRank = seqMeta.get("max_rank")

            if startAfterRank is not None and startAfterRank >= maxRank:
                raise errors.InvalidAPIUsage(
                    _("No more items in this collection (last available rank is %(r)s)", r=maxRank), status_code=404
                )

            if withPicture is not None:
                withPicture = as_uuid(withPicture, "withPicture should be a valid UUID")
                pic = cursor.execute(
                    "SELECT rank FROM pictures p JOIN sequences_pictures sp ON sp.pic_id = p.id WHERE p.id = %(id)s AND sp.seq_id = %(seq)s",
                    params={"id": withPicture, "seq": collectionId},
                ).fetchone()
                if not pic:
                    raise errors.InvalidAPIUsage(_("Picture with id %(p)s does not exist", p=withPicture))
                rank = get_first_rank_of_page(pic["rank"], limit)

                filters.append(SQL("rank >= %(start_after_rank)s"))
                params["start_after_rank"] = rank

            query = SQL(
                """
                SELECT
                    p.id, p.ts, p.heading, p.metadata, p.inserted_at, p.updated_at, p.status,
                    ST_AsGeoJSON(p.geom)::json AS geojson,
                    a.name AS account_name,
                    p.account_id AS account_id,
                    sp.seq_id, sp.rank, p.exif, p.gps_accuracy_m, p.h_pixel_density,
                    CASE WHEN LAG(p.status) OVER othpics = 'ready' THEN LAG(p.id) OVER othpics END AS prevpic,
                    CASE WHEN LAG(p.status) OVER othpics = 'ready' THEN ST_AsGeoJSON(LAG(p.geom) OVER othpics)::json END AS prevpicgeojson,
                    CASE WHEN LEAD(p.status) OVER othpics = 'ready' THEN LEAD(p.id) OVER othpics END AS nextpic,
                    CASE WHEN LEAD(p.status) OVER othpics = 'ready' THEN ST_AsGeoJSON(LEAD(p.geom) OVER othpics)::json END AS nextpicgeojson,
                    get_picture_semantics(p.id) as semantics,
                    get_picture_annotations(p.id) as annotations
                FROM sequences_pictures sp
                JOIN pictures p ON sp.pic_id = p.id
                JOIN accounts a ON a.id = p.account_id
                JOIN sequences s ON s.id = sp.seq_id
                WHERE
                    {filter}
                WINDOW othpics AS (PARTITION BY sp.seq_id ORDER BY sp.rank)
                ORDER BY rank
                {limit}
                """
            ).format(filter=SQL(" AND ").join(filters), limit=sql_limit)

            records = cursor.execute(query, params)

            items = []
            first_rank, last_rank = None, None
            for dbPic in records:
                if first_rank is None:
                    first_rank = dbPic["rank"]
                last_rank = dbPic["rank"]
                items.append(dbPictureToStacItem(dbPic))
            bounds = Bounds(first=first_rank, last=last_rank) if records else None

            links = [
                get_root_link(),
                {
                    "rel": "parent",
                    "type": "application/json",
                    "href": url_for("stac_collections.getCollection", _external=True, collectionId=collectionId),
                },
                {
                    "rel": "self",
                    "type": "application/geo+json",
                    "href": url_for(
                        "stac_items.getCollectionItems",
                        _external=True,
                        collectionId=collectionId,
                        limit=limit,
                        startAfterRank=startAfterRank,
                    ),
                },
            ]

            if paginated and items and bounds:
                if bounds.first:
                    has_item_before = bounds.first > seqMeta["min_rank"]
                    if has_item_before:
                        links.append(
                            {
                                "rel": "first",
                                "type": "application/geo+json",
                                "href": url_for("stac_items.getCollectionItems", _external=True, collectionId=collectionId, limit=limit),
                            }
                        )
                        # Previous page link
                        #   - If limit is set, rank is current - limit -1
                        #   - If no limit is set, rank is 0 (none)
                        prevRank = bounds.first - limit - 1 if limit is not None else 0
                        if prevRank < 1:
                            prevRank = None
                        links.append(
                            {
                                "rel": "prev",
                                "type": "application/geo+json",
                                "href": url_for(
                                    "stac_items.getCollectionItems",
                                    _external=True,
                                    collectionId=collectionId,
                                    limit=limit,
                                    startAfterRank=prevRank,
                                ),
                            }
                        )

                has_item_after = bounds.last < seqMeta["max_rank"]
                if has_item_after:
                    links.append(
                        {
                            "rel": "next",
                            "type": "application/geo+json",
                            "href": url_for(
                                "stac_items.getCollectionItems",
                                _external=True,
                                collectionId=collectionId,
                                limit=limit,
                                startAfterRank=bounds.last,
                            ),
                        }
                    )

                    # Last page link
                    #   - If this page is the last one, rank equals to rank given by user
                    #   - Otherwise, rank equals max rank - limit

                    lastPageRank = startAfterRank
                    if limit is not None:
                        if seqMeta["max_rank"] > bounds.last:
                            lastPageRank = seqMeta["max_rank"] - limit
                            if lastPageRank < bounds.last:
                                lastPageRank = bounds.last

                    links.append(
                        {
                            "rel": "last",
                            "type": "application/geo+json",
                            "href": url_for(
                                "stac_items.getCollectionItems",
                                _external=True,
                                collectionId=collectionId,
                                limit=limit,
                                startAfterRank=lastPageRank,
                            ),
                        }
                    )

            return (
                {
                    "type": "FeatureCollection",
                    "features": items,
                    "links": links,
                },
                200,
                {"Content-Type": "application/geo+json"},
            )


def _getPictureItemById(itemId: UUID, account: Optional[Account]):
    """Get a picture metadata by its ID"""
    with current_app.pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            # Check if there is a logged user
            account = auth.get_current_account()
            accountId = account.id if account else None

            # Get rank + position of wanted picture
            record = cursor.execute(
                """WITH seq AS (
                    SELECT seq_id FROM sequences_pictures WHERE pic_id = %(pic)s LIMIT 1
                )
                SELECT
                    p.id, sp.seq_id, sp.rank, ST_AsGeoJSON(p.geom)::json AS geojson, p.heading, p.ts, p.metadata,
                    p.inserted_at, p.updated_at, p.status, accounts.name AS account_name,
                    p.account_id AS account_id,
                    spl.prevpic, spl.prevpicgeojson, spl.nextpic, spl.nextpicgeojson, p.exif,
                    relp.related_pics, p.gps_accuracy_m, p.h_pixel_density,
                    get_picture_semantics(p.id) as semantics,
                    get_picture_annotations(p.id) as annotations,
                    COALESCE(seq_sem.semantics, '[]'::json) AS sequence_semantics
                FROM pictures p
                JOIN sequences_pictures sp ON sp.pic_id = p.id
                JOIN accounts ON p.account_id = accounts.id
                JOIN sequences s ON sp.seq_id = s.id
                LEFT JOIN (
                    SELECT
                        p.id,
                        LAG(p.id) OVER othpics AS prevpic,
                        ST_AsGeoJSON(LAG(p.geom) OVER othpics)::json AS prevpicgeojson,
                        LEAD(p.id) OVER othpics AS nextpic,
                        ST_AsGeoJSON(LEAD(p.geom) OVER othpics)::json AS nextpicgeojson
                    FROM pictures p
                    JOIN sequences_pictures sp ON p.id = sp.pic_id
                    WHERE
                        sp.seq_id IN (SELECT seq_id FROM seq)
                        AND (p.account_id = %(acc)s OR p.status != 'hidden')
                    WINDOW othpics AS (PARTITION BY sp.seq_id ORDER BY sp.rank)
                ) spl ON p.id = spl.id
                LEFT JOIN (
                    SELECT array_agg(ARRAY[seq_id::text, id::text, geom, tstxt]) AS related_pics
                    FROM (
                        SELECT DISTINCT ON (relsp.seq_id)
                            relsp.seq_id, relp.id,
                            ST_AsGeoJSON(relp.geom) as geom,
                            to_char(relp.ts at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS tstxt
                        FROM
                            pictures relp,
                            pictures p,
                            sequences_pictures relsp
                        WHERE
                            -- Related pictures are retrieved based on:
                            --   > Proximity (15m)
                            --   > Status (publicly available or from current user)
                            --   > Sequence (only one per sequence, the nearest one)
                            --   > Pic ID (not the current picture)
                            --   > Heading (either 360° or in less than 100° of diff with current picture)
                            p.id = %(pic)s
                            AND ST_Intersects(ST_Buffer(p.geom::geography, 15)::geometry, relp.geom)
                            AND (relp.account_id = %(acc)s OR relp.status = 'ready')
                            AND relp.status != 'waiting-for-delete'
                            AND relp.id != p.id
                            AND relsp.pic_id = relp.id
                            AND relsp.seq_id NOT IN (SELECT seq_id FROM seq)
                            AND (
                                p.metadata->>'type' = 'equirectangular'
                                OR (relp.heading IS NULL OR p.heading IS NULL)
                                OR (
                                    relp.heading IS NOT NULL
                                    AND p.heading IS NOT NULL
                                    AND ABS(relp.heading - p.heading) <= 100
                                )
                            )
                        ORDER BY relsp.seq_id, p.geom <-> relp.geom
                    ) a
                ) relp ON TRUE
                LEFT JOIN (
                    SELECT sequence_id, json_agg(json_strip_nulls(json_build_object(
                        'key', key,
                        'value', value
                    )) ORDER BY key, value) AS semantics
                    FROM sequences_semantics
                    GROUP BY sequence_id
                ) seq_sem ON seq_sem.sequence_id = s.id
                WHERE sp.seq_id IN (SELECT seq_id FROM seq)
                    AND p.id = %(pic)s
                    AND (p.account_id = %(acc)s OR p.status != 'hidden')
                    AND (s.status != 'hidden' OR s.account_id = %(acc)s)
                    AND s.status != 'deleted'
                """,
                {"pic": itemId, "acc": accountId},
            ).fetchone()

            if record is None:
                return None

            return dbPictureToStacItem(record)


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>")
def getCollectionItem(collectionId, itemId):
    """Get a single item from a collection
    ---
    tags:
        - Pictures
    parameters:
        - name: collectionId
          in: path
          description: ID of collection to retrieve
          required: true
          schema:
            type: string
        - name: itemId
          in: path
          description: ID of item to retrieve
          required: true
          schema:
            type: string
    responses:
        102:
            description: the item (which is still under process)
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
        200:
            description: the wanted item
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
    """
    account = auth.get_current_account()

    stacItem = _getPictureItemById(itemId, account)
    if stacItem is None:
        raise errors.InvalidAPIUsage(_("Item doesn't exist"), status_code=404)

    picStatusToHttpCode = {
        "waiting-for-process": 102,
        "ready": 200,
        "hidden": 200 if account else 404,
        "broken": 500,
    }
    return stacItem, picStatusToHttpCode[stacItem["properties"]["geovisio:status"]], {"Content-Type": "application/geo+json"}


@bp.route("/search", methods=["GET", "POST"])
def searchItems():
    """Search through all available items

    Note: when searching with a bounding box or a geometry, the items will be sorted by proximity of the center of this bounding box / geometry
    Else the items will not be sorted.
    ---
    tags:
        - Pictures
    get:
        parameters:
            - $ref: '#/components/parameters/STAC_bbox'
            - $ref: '#/components/parameters/STAC_intersects'
            - $ref: '#/components/parameters/STAC_datetime'
            - $ref: '#/components/parameters/STAC_limit'
            - $ref: '#/components/parameters/STAC_ids'
            - $ref: '#/components/parameters/STAC_collectionsArray'
            - $ref: '#/components/parameters/GeoVisio_place_position'
            - $ref: '#/components/parameters/GeoVisio_place_distance'
            - $ref: '#/components/parameters/GeoVisio_place_fov_tolerance'
            - $ref: '#/components/parameters/searchCQL2_filter'
            - $ref: '#/components/parameters/GeoVisioSearchSortedBy'
    post:
        requestBody:
            required: true
            content:
              application/json:
                schema:
                  $ref: '#/components/schemas/GeoVisioItemSearchBody'
    responses:
        200:
            description: The search results
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionItems'
    """

    account = auth.get_current_account()
    accountId = account.id if account is not None else None
    sqlWhere = [SQL("(p.status = 'ready' OR p.account_id = %(account)s)"), SQL("(is_sequence_visible_by_user(s, %(account)s))")]
    sqlParams: Dict[str, Any] = {"account": accountId}
    sqlSubQueryWhere = [SQL("(p.status = 'ready' OR p.account_id = %(account)s)")]

    #
    # Parameters parsing and verification
    #

    # Method + content-type
    args: MultiDict[str, str]
    if request.method == "POST":
        if request.headers.get("Content-Type") != "application/json":
            raise errors.InvalidAPIUsage(_("Search using POST method should have a JSON body"), status_code=400)
        args = MultiDict(request.json)
    else:
        args = request.args

    # Limit
    limit = args.get("limit") or 10
    try:
        limit = int(limit)
        if limit < 1 or limit > 10000:
            raise ValueError()
    except ValueError:
        raise errors.InvalidAPIUsage(_("Parameter limit must be either empty or a number between 1 and 10000"), status_code=400)
    sqlParams["limit"] = limit

    sort_by = parse_item_sortby(args.get("sortby"))

    # Bounding box
    bboxarg = parse_bbox(args.getlist("bbox"))
    if bboxarg is not None:
        sqlWhere.append(SQL("p.geom && ST_MakeEnvelope(%(minx)s, %(miny)s, %(maxx)s, %(maxy)s, 4326)"))
        sqlParams["minx"] = bboxarg[0]
        sqlParams["miny"] = bboxarg[1]
        sqlParams["maxx"] = bboxarg[2]
        sqlParams["maxy"] = bboxarg[3]
        # if we search by bbox, we'll give first the items near the center of the bounding box
        if not sort_by:
            sort_by = SortBy(
                fields=[
                    ItemSortByField(
                        field=SortableItemField.distance_to,
                        direction=SQLDirection.ASC,
                        obj_to_compare=SQL("ST_Centroid(ST_MakeEnvelope(%(minx)s, %(miny)s, %(maxx)s, %(maxy)s, 4326))"),
                    ),
                ]
            )

    # Datetime
    min_dt, max_dt = parse_datetime_interval(args.get("datetime"))
    if min_dt is not None:
        sqlWhere.append(SQL("p.ts >= %(mints)s::timestamp with time zone"))
        sqlParams["mints"] = min_dt

    if max_dt is not None:
        sqlWhere.append(SQL("p.ts <= %(maxts)s::timestamp with time zone"))
        sqlParams["maxts"] = max_dt

    # Place position & distance
    place_pos = parse_lonlat(args.getlist("place_position"), "place_position")
    if place_pos is not None:
        sqlParams["placex"] = place_pos[0]
        sqlParams["placey"] = place_pos[1]

        # Filter to keep pictures in acceptable distance range to POI
        place_dist = parse_distance_range(args.get("place_distance"), "place_distance") or [3, 15]
        sqlParams["placedmin"] = place_dist[0]
        sqlParams["placedmax"] = place_dist[1]

        sqlWhere.append(
            SQL(
                """
                ST_Intersects(
                    p.geom,
                    ST_Difference(
                    ST_Buffer(ST_Point(%(placex)s, %(placey)s)::geography, %(placedmax)s)::geometry,
                        ST_Buffer(ST_Point(%(placex)s, %(placey)s)::geography, %(placedmin)s)::geometry
                    )
                )
                """
            )
        )

        # Compute acceptable field of view
        place_fov_tolerance = args.get("place_fov_tolerance", type=int, default=30)
        if place_fov_tolerance < 2 or place_fov_tolerance > 180:
            raise errors.InvalidAPIUsage(
                _("Parameter place_fov_tolerance must be either empty or a number between 2 and 180"), status_code=400
            )
        else:
            sqlParams["placefov"] = place_fov_tolerance / 2

        sqlWhere.append(
            SQL(
                """(
                p.metadata->>'type' = 'equirectangular'
                OR ST_Azimuth(p.geom, ST_Point(%(placex)s, %(placey)s, 4326)) BETWEEN radians(p.heading - %(placefov)s) AND radians(p.heading + %(placefov)s)
            )"""
            )
        )

        # Sort pictures by nearest to POI
        if not sort_by:
            sort_by = SortBy(
                fields=[
                    ItemSortByField(
                        field=SortableItemField.distance_to,
                        direction=SQLDirection.ASC,
                        obj_to_compare=SQL("ST_Point(%(placex)s, %(placey)s, 4326)"),
                    ),
                ]
            )

    # Intersects
    if args.get("intersects") is not None:
        try:
            intersects = json.loads(args["intersects"])
        except:
            raise errors.InvalidAPIUsage(_("Parameter intersects should contain a valid GeoJSON Geometry (not a Feature)"), status_code=400)
        if intersects["type"] == "Point":
            sqlWhere.append(SQL("p.geom && ST_Expand(ST_GeomFromGeoJSON(%(geom)s), 0.000001)"))
        else:
            sqlWhere.append(SQL("p.geom && ST_GeomFromGeoJSON(%(geom)s)"))
            sqlWhere.append(SQL("ST_Intersects(p.geom, ST_GeomFromGeoJSON(%(geom)s))"))
        sqlParams["geom"] = Jsonb(intersects)
        # if we search by bbox, we'll give first the items near the center of the bounding box
        if not sort_by:
            sort_by = SortBy(
                fields=[
                    ItemSortByField(
                        field=SortableItemField.distance_to,
                        direction=SQLDirection.ASC,
                        obj_to_compare=SQL("ST_Centroid(ST_GeomFromGeoJSON(%(geom)s))"),
                    ),
                ]
            )

    # Ids
    if args.get("ids") is not None:
        sqlWhere.append(SQL("p.id = ANY(%(ids)s)"))
        try:
            sqlParams["ids"] = [UUID(j) for j in parse_list(args.get("ids"), paramName="ids")]
        except:
            raise errors.InvalidAPIUsage(_("Parameter ids should be a JSON array of strings"), status_code=400)

    # Collections
    if args.get("collections") is not None:
        sqlWhere.append(SQL("sp.seq_id = ANY(%(collections)s)"))

        # custom subquery filtering to help PG query plan
        sqlSubQueryWhere.append(SQL("sp.seq_id = ANY(%(collections)s)"))

        try:
            sqlParams["collections"] = [UUID(j) for j in parse_list(args["collections"], paramName="collections")]
        except:
            raise errors.InvalidAPIUsage(_("Parameter collections should be a JSON array of strings"), status_code=400)

    # To speed up search, if it's a search by id and on only one id, we use the same code as /collections/:cid/items/:id
    if args.get("ids") is not None:
        ids = parse_list(args.get("ids"), paramName="ids")
        if ids and len(ids) == 1:
            picture_id = ids[0]

            with current_app.pool.connection() as conn, conn.cursor() as cursor:
                item = _getPictureItemById(UUID(picture_id), account)
                features = [item] if item else []
                return (
                    {"type": "FeatureCollection", "features": features, "links": [get_root_link()]},
                    200,
                    {"Content-Type": "application/geo+json"},
                )
    filter_param = args.get("filter")
    if filter_param is not None:
        cql_filter = parse_search_filter(filter_param)
        if cql_filter is not None:
            sqlWhere.append(cql_filter)

    if not sort_by:
        # by default we sort by last updated (and id in case of equalities)
        sort_by = SortBy(
            fields=[
                ItemSortByField(field=SortableItemField.updated, direction=SQLDirection.DESC),
                ItemSortByField(field=SortableItemField.id, direction=SQLDirection.ASC),
            ]
        )

    order_by = sort_by.to_sql()

    #
    # Database query
    #
    with db.cursor(current_app, timeout=30000, row_factory=dict_row) as cursor:
        query = SQL(
            """
SELECT * FROM (
    SELECT
        p.id, p.ts, p.heading, p.metadata, p.inserted_at, p.updated_at,
        ST_AsGeoJSON(p.geom)::json AS geojson,
        sp.seq_id, sp.rank AS rank,
        accounts.name AS account_name, 
        p.account_id AS account_id,
        p.exif, p.gps_accuracy_m, p.h_pixel_density,
        get_picture_semantics(p.id) as semantics,
        get_picture_annotations(p.id) as annotations,
        COALESCE(seq_sem.semantics, '[]'::json) AS sequence_semantics
    FROM pictures p
    LEFT JOIN sequences_pictures sp ON p.id = sp.pic_id
    LEFT JOIN sequences s ON s.id = sp.seq_id
    LEFT JOIN accounts ON p.account_id = accounts.id
    LEFT JOIN (
        SELECT sequence_id, json_agg(json_strip_nulls(json_build_object(
            'key', key,
            'value', value
        )) ORDER BY key, value) AS semantics
        FROM sequences_semantics
        GROUP BY sequence_id
    ) seq_sem ON seq_sem.sequence_id = s.id
    WHERE {sqlWhere}
    {orderBy}
    LIMIT %(limit)s
) pic
LEFT JOIN LATERAL (
    SELECT
    p.id AS prevpic, ST_AsGeoJSON(p.geom)::json AS prevpicgeojson
    FROM sequences_pictures sp
    JOIN pictures p ON sp.pic_id = p.id
    WHERE pic.seq_id = sp.seq_id AND {sqlSubQueryWhere} AND sp.rank < pic.rank 
    ORDER BY sp.rank DESC 
    LIMIT 1
) prev on true
LEFT JOIN LATERAL (
    SELECT
    p.id AS nextpic, ST_AsGeoJSON(p.geom)::json AS nextpicgeojson
    FROM sequences_pictures sp
    JOIN pictures p ON sp.pic_id = p.id
    WHERE pic.seq_id = sp.seq_id AND {sqlSubQueryWhere} AND sp.rank > pic.rank 
    ORDER BY sp.rank ASC 
    LIMIT 1
) next on true

;
        """
        ).format(sqlWhere=SQL(" AND ").join(sqlWhere), sqlSubQueryWhere=SQL(" AND ").join(sqlSubQueryWhere), orderBy=order_by)

        records = cursor.execute(query, sqlParams)

        items = [dbPictureToStacItem(dbPic) for dbPic in records]

        return (
            {
                "type": "FeatureCollection",
                "features": items,
                "links": [
                    get_root_link(),
                ],
            },
            200,
            {"Content-Type": "application/geo+json"},
        )


@bp.route("/collections/<uuid:collectionId>/items", methods=["POST"])
@auth.login_required_by_setting("API_FORCE_AUTH_ON_UPLOAD")
def postCollectionItem(collectionId, account=None):
    """Add a new picture in a given sequence.

    Note that this is the legacy API, upload should be done using the [UploadSet](#UploadSet) endpoints if possible.
    ---
    tags:
        - Upload
    parameters:
        - name: collectionId
          in: path
          description: ID of sequence to add this picture into
          required: true
          schema:
            type: string
    requestBody:
        content:
            multipart/form-data:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostItem'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        202:
            description: the added picture metadata
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
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
            description: Error if you're not authorized to add picture to this collection
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        404:
            description: Error if the collection doesn't exist
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioError'
        409:
            description: Error if a picture (named `item` in the API) has already been added in the same index (named `position` in the API) in this collection
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

    if not request.headers.get("Content-Type", "").startswith("multipart/form-data"):
        raise errors.InvalidAPIUsage(_("Content type should be multipart/form-data"), status_code=415)

    # Check if position was given
    if request.form.get("position") is None:
        raise errors.InvalidAPIUsage(_('Missing "position" parameter'), status_code=400)
    else:
        try:
            position = int(request.form["position"])
            if position <= 0:
                raise ValueError()
        except ValueError:
            raise errors.InvalidAPIUsage(_("Position in sequence should be a positive integer"), status_code=400)

    # Check if datetime was given
    ext_mtd = PictureMetadata()
    if request.form.get("override_capture_time") is not None:
        ext_mtd.capture_time = parse_datetime(
            request.form.get("override_capture_time"),
            error="Parameter `override_capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z').",
        )

    # Check if lat/lon were given
    lon, lat = request.form.get("override_longitude"), request.form.get("override_latitude")
    if lon is not None or lat is not None:
        if lat is None:
            raise errors.InvalidAPIUsage(_("Longitude cannot be overridden alone, override_latitude also needs to be set"))
        if lon is None:
            raise errors.InvalidAPIUsage(_("Latitude cannot be overridden alone, override_longitude also needs to be set"))
        lon = as_longitude(lon, error=_("For parameter `override_longitude`, `%(v)s` is not a valid longitude", v=lon))
        lat = as_latitude(lat, error=_("For parameter `override_latitude`, `%(v)s` is not a valid latitude", v=lat))
        ext_mtd.longitude = lon
        ext_mtd.latitude = lat

    # Check if others override elements were given
    override_elmts = {}
    for k, v in request.form.to_dict().items():
        if not (k.startswith("override_Exif.") or k.startswith("override_Xmp.")):
            continue
        exif_tag = k.replace("override_", "")
        override_elmts[exif_tag] = v

    if override_elmts:
        ext_mtd.additional_exif = override_elmts

    # Check if picture blurring status is valid
    if request.form.get("isBlurred") is None or request.form.get("isBlurred") in ["true", "false"]:
        isBlurred = request.form.get("isBlurred") == "true"
    else:
        raise errors.InvalidAPIUsage(_("Picture blur status should be either unset, true or false"), status_code=400)

    # Check if a picture file was given
    if "picture" not in request.files:
        raise errors.InvalidAPIUsage(_("No picture file was sent"), status_code=400)
    else:
        picture = request.files["picture"]

        # Check file validity
        if not (picture.filename != "" and "." in picture.filename and picture.filename.rsplit(".", 1)[1].lower() in ["jpg", "jpeg"]):
            raise errors.InvalidAPIUsage(_("Picture file is either missing or in an unsupported format (should be jpg)"), status_code=400)

    with db.conn(current_app) as conn:
        with conn.transaction(), conn.cursor() as cursor:
            # Check if sequence exists
            seq = cursor.execute("SELECT account_id, status FROM sequences WHERE id = %s", [collectionId]).fetchone()
            if not seq:
                raise errors.InvalidAPIUsage(_("Collection %(s)s wasn't found in database", s=collectionId), status_code=404)

            # Account associated to picture doesn't match current user
            if account is not None and account.id != str(seq[0]):
                raise errors.InvalidAPIUsage(_("You're not authorized to add picture to this collection"), status_code=403)

            # Check if sequence has not been deleted
            status = seq[1]
            if status == "deleted":
                raise errors.InvalidAPIUsage(_("The collection has been deleted, impossible to add pictures to it"), status_code=404)

            # Compute various metadata
            accountId = accountIdOrDefault(account)
            raw_pic = picture.read()
            filesize = len(raw_pic)

            with sentry_sdk.start_span(description="computing md5"):
                # we save the content hash md5 as uuid since md5 is 128bit and uuid are efficiently handled in postgres
                md5 = hashlib.md5(raw_pic).digest()
                md5 = UUID(bytes=md5)

            additionalMetadata = {
                "blurredByAuthor": isBlurred,
                "originalFileName": os.path.basename(picture.filename),
                "originalFileSize": filesize,
                "originalContentMd5": md5,
            }

            # Update picture metadata if needed
            with sentry_sdk.start_span(description="overwriting metadata"):
                updated_picture = writePictureMetadata(raw_pic, ext_mtd)

            # Insert picture into database
            with sentry_sdk.start_span(description="Insert picture in db"):
                try:
                    picId = utils.pictures.insertNewPictureInDatabase(
                        conn, collectionId, position, updated_picture, accountId, additionalMetadata, lang=get_locale().language
                    )
                except utils.pictures.PicturePositionConflict:
                    raise errors.InvalidAPIUsage(_("There is already a picture with the same index in the sequence"), status_code=409)
                except utils.pictures.MetadataReadingError as e:
                    raise errors.InvalidAPIUsage(_("Impossible to parse picture metadata"), payload={"details": {"error": e.details}})
                except utils.pictures.InvalidMetadataValue as e:
                    raise errors.InvalidAPIUsage(_("Picture has invalid metadata"), payload={"details": {"error": e.details}})

            # Save file into appropriate filesystem
            with sentry_sdk.start_span(description="Saving picture"):
                try:
                    utils.pictures.saveRawPicture(picId, updated_picture, isBlurred)
                except:
                    logging.exception("Picture wasn't correctly saved in filesystem")
                    raise errors.InvalidAPIUsage(_("Picture wasn't correctly saved in filesystem"), status_code=500)

    current_app.background_processor.process_pictures()

    # Return picture metadata
    return (
        getCollectionItem(collectionId, picId)[0],
        202,
        {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",  # Needed for allowing web browsers access Location header
            "Location": url_for("stac_items.getCollectionItem", _external=True, collectionId=collectionId, itemId=picId),
        },
    )


class PatchItemParameter(BaseModel):
    """Parameters used to add an item to an UploadSet"""

    heading: Optional[int] = None
    """Heading of the picture. The new heading will not be persisted in the picture's exif tags for the moment."""
    visible: Optional[bool] = None
    """Should the picture be publicly visible ?"""

    capture_time: Optional[datetime] = None
    """Capture time of the picture. The new capture time will not be persisted in the picture's exif tags for the moment."""
    longitude: Optional[float] = None
    """Longitude of the picture. The new longitude will not be persisted in the picture's exif tags for the moment."""
    latitude: Optional[float] = None
    """Latitude of the picture. The new latitude will not be persisted in the picture's exif tags for the moment."""

    semantics: Optional[List[SemanticTagUpdate]] = None
    """Tags to update on the picture. By default each tag will be added to the picture's tags, but you can change this behavior by setting the `action` parameter to `delete`.

    If you want to replace a tag, you need to first delete it, then add it again.

    Like:
[
    {"key": "some_key", "value": "some_value", "action": "delete"},
    {"key": "some_key", "value": "some_new_value"}
]

    
    Note that updating tags is only possible with JSON data, not with form-data."""

    def has_override(self) -> bool:
        return self.model_fields_set

    @field_validator("heading", mode="before")
    @classmethod
    def parse_heading(cls, value):
        if value is None:
            return None
        return parse_picture_heading(value)

    @field_validator("visible", mode="before")
    @classmethod
    def parse_visible(cls, value):
        if value not in ["true", "false"]:
            raise errors.InvalidAPIUsage(_("Picture visibility parameter (visible) should be either unset, true or false"), status_code=400)
        return value == "true"

    @field_validator("capture_time", mode="before")
    @classmethod
    def parse_capture_time(cls, value):
        if value is None:
            return None
        return parse_datetime(
            value,
            error=_(
                "Parameter `capture_time` is not a valid datetime, it should be an iso formated datetime (like '2017-07-21T17:32:28Z')."
            ),
        )

    @field_validator("longitude")
    @classmethod
    def parse_longitude(cls, value):
        return as_longitude(value, error=_("For parameter `longitude`, `%(v)s` is not a valid longitude", v=value))

    @field_validator("latitude")
    @classmethod
    def parse_latitude(cls, value):
        return as_latitude(value, error=_("For parameter `latitude`, `%(v)s` is not a valid latitude", v=value))

    @model_validator(mode="after")
    def validate(self):
        if self.latitude is None and self.longitude is not None:
            raise errors.InvalidAPIUsage(_("Longitude cannot be overridden alone, latitude also needs to be set"))
        if self.longitude is None and self.latitude is not None:
            raise errors.InvalidAPIUsage(_("Latitude cannot be overridden alone, longitude also needs to be set"))
        return self

    def has_only_semantics_updates(self):
        return self.model_fields_set == {"semantics"}


def update_picture(itemId: UUID, account: Optional[Account]):
    # Parse received parameters
    metadata = None
    content_type = (request.headers.get("Content-Type") or "").split(";")[0]

    try:
        if request.is_json and request.json:
            metadata = PatchItemParameter(**request.json)
        elif content_type in ["multipart/form-data", "application/x-www-form-urlencoded"]:
            metadata = PatchItemParameter(**request.form)
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    # If no parameter is set
    if metadata is None or not metadata.has_override():
        return (_getPictureItemById(itemId, account), 304)

    # Check if picture exists and if given account is authorized to edit
    with db.conn(current_app) as conn:
        with conn.transaction(), conn.cursor(row_factory=dict_row) as cursor:
            pic = cursor.execute("SELECT status, account_id FROM pictures WHERE id = %s", [itemId]).fetchone()

            # Picture not found
            if not pic:
                raise errors.InvalidAPIUsage(_("Picture %(p)s wasn't found in database", p=itemId), status_code=404)

            if account is not None and account.id != str(pic["account_id"]):
                # Account associated to picture doesn't match current user
                # and we limit the status change to only the owner.
                if metadata.visible is not None:
                    raise errors.InvalidAPIUsage(
                        _("You're not authorized to edit the visibility of this picture. Only the owner can change this."), status_code=403
                    )

                # for core metadata editing (all appart the semantic tags), we check if the user has allowed it
                if not metadata.has_only_semantics_updates():
                    if not auth.account_allow_collaborative_editing(pic["account_id"]):
                        raise errors.InvalidAPIUsage(
                            _("You're not authorized to edit this picture, collaborative editing is not allowed"),
                            status_code=403,
                        )
            sqlUpdates = []
            sqlParams = {"id": itemId, "account": account.id}

            # Let's edit this picture
            oldStatus = pic["status"]
            if oldStatus not in ["ready", "hidden"]:
                # Picture is in a preparing/broken/... state so no edit possible
                raise errors.InvalidAPIUsage(
                    _(
                        "Picture %(p)s is in %(s)s state, its visibility can't be changed for now",
                        p=itemId,
                        s=oldStatus,
                    ),
                    status_code=400,
                )

            newStatus = None
            if metadata.visible is not None:
                newStatus = "ready" if metadata.visible is True else "hidden"
                if newStatus != oldStatus:
                    sqlUpdates.append(SQL("status = %(status)s"))
                    sqlParams["status"] = newStatus

            if metadata.heading is not None:
                sqlUpdates.extend([SQL("heading = %(heading)s"), SQL("heading_computed = false")])
                sqlParams["heading"] = metadata.heading

            if metadata.capture_time is not None:
                sqlUpdates.extend([SQL("ts = %(capture_time)s")])
                sqlParams["capture_time"] = metadata.capture_time

            if metadata.longitude is not None and metadata.latitude is not None:
                sqlUpdates.extend([SQL("geom = ST_SetSRID(ST_MakePoint(%(longitude)s, %(latitude)s), 4326)")])
                sqlParams["longitude"] = metadata.longitude
                sqlParams["latitude"] = metadata.latitude

            if metadata.semantics is not None:
                # semantic tags are managed separately
                update_tags(cursor, Entity(type=EntityType.pic, id=itemId), metadata.semantics, account=account.id)

            if sqlUpdates:
                # Note: we set the field `last_account_to_edit` to track who changed the collection last
                # setting this field will trigger the history tracking of the collection (using postgres trigger)
                sqlUpdates.append(SQL("last_account_to_edit = %(account)s"))

                cursor.execute(
                    SQL(
                        """UPDATE pictures
SET {updates}
WHERE id = %(id)s"""
                    ).format(updates=SQL(", ").join(sqlUpdates)),
                    sqlParams,
                )

    # Redirect response to a classic GET
    return (_getPictureItemById(itemId, account), 200)


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>", methods=["PATCH"])
@auth.login_required()
def patchCollectionItem(collectionId, itemId, account):
    """Edits properties of an existing picture

    Note that tags cannot be added as form-data for the moment, only as JSON.

    Note that there are rules on the editing of a picture's metadata:

    - Only the owner of a picture can change its visibility
    - For core metadata (heading, capture_time, position, longitude, latitude), the owner can restrict their change by other accounts (see `collaborative_metadata` field in `/api/users/me`) and if not explicitly defined by the user, the instance's default value is used.
    - Everyone can add/edit/delete semantics tags.
    ---
    tags:
        - Editing
        - Semantics
    parameters:
        - name: collectionId
          in: path
          description: ID of sequence the picture belongs to
          required: true
          schema:
            type: string
        - name: itemId
          in: path
          description: ID of picture to edit
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchItem'
            application/x-www-form-urlencoded:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchItem'
            multipart/form-data:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchItem'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the wanted item
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
    """
    return update_picture(itemId, account)


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>", methods=["DELETE"])
@auth.login_required()
def deleteCollectionItem(collectionId, itemId, account):
    """Delete an existing picture
    ---
    tags:
        - Editing
    parameters:
        - name: collectionId
          in: path
          description: ID of sequence the picture belongs to
          required: true
          schema:
            type: string
        - name: itemId
          in: path
          description: ID of picture to edit
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        204:
            description: The object has been correctly deleted
    """

    # Check if picture exists and if given account is authorized to edit
    with db.conn(current_app) as conn:
        with conn.transaction(), conn.cursor() as cursor:
            pic = cursor.execute("SELECT status, account_id FROM pictures WHERE id = %s", [itemId]).fetchone()

            # Picture not found
            if not pic:
                raise errors.InvalidAPIUsage(_("Picture %(p)s wasn't found in database", p=itemId), status_code=404)

            # Account associated to picture doesn't match current user
            if account is not None and account.id != str(pic[1]):
                raise errors.InvalidAPIUsage(_("You're not authorized to edit this picture"), status_code=403)

            cursor.execute("DELETE FROM pictures WHERE id = %s", [itemId])

    # let the picture be removed from the filesystem by the asynchronous workers
    current_app.background_processor.process_pictures()

    return "", 204


def _getHDJpgPictureURL(picId: str, status: Optional[str]):
    external_url = utils.pictures.getPublicHDPictureExternalUrl(picId, format="jpg")
    if external_url and status == "ready":  # we always serve non ready pictures through the API to be able to check permission:
        return external_url
    return url_for("pictures.getPictureHD", _external=True, pictureId=picId, format="jpg")


def _getSDJpgPictureURL(picId: str, status: Optional[str]):
    external_url = utils.pictures.getPublicDerivatePictureExternalUrl(picId, format="jpg", derivateFileName="sd.jpg")
    if external_url and status == "ready":  # we always serve non ready pictures through the API to be able to check permission:
        return external_url
    return url_for("pictures.getPictureSD", _external=True, pictureId=picId, format="jpg")


def _getThumbJpgPictureURL(picId: str, status: Optional[str]):
    external_url = utils.pictures.getPublicDerivatePictureExternalUrl(picId, format="jpg", derivateFileName="thumb.jpg")
    if external_url and status == "ready":  # we always serve non ready pictures through the API to be able to check permission
        return external_url
    return url_for("pictures.getPictureThumb", _external=True, pictureId=picId, format="jpg")


def _getTilesJpgPictureURL(picId: str, status: Optional[str]):
    external_url = utils.pictures.getPublicDerivatePictureExternalUrl(picId, format="jpg", derivateFileName="tiles/{TileCol}_{TileRow}.jpg")
    if external_url and status == "ready":  # we always serve non ready pictures through the API to be able to check permission:
        return external_url
    return unquote(url_for("pictures.getPictureTile", _external=True, pictureId=picId, format="jpg", col="{TileCol}", row="{TileRow}"))
