from uuid import UUID
from flask import Blueprint, current_app, request
from flask_babel import gettext as _
from typing import Optional, Union
from psycopg.rows import class_row
from psycopg.sql import SQL, Literal, Identifier
from geovisio.utils import db, auth
from geovisio.utils.excluded_areas import (
    list_excluded_areas,
    delete_excluded_area,
    ExcludedAreaFeature,
)
from geovisio.utils.params import validation_error
from geovisio.errors import InvalidAPIUsage, InternalError
from pydantic import BaseModel, ConfigDict, ValidationError
from geojson_pydantic import FeatureCollection, Feature, Polygon, MultiPolygon

bp = Blueprint("excluded_areas", __name__, url_prefix="/api")


class ExcludedAreaCreateParameters(BaseModel):
    """An excluded area is a geographical boundary where pictures should not be accepted."""

    label: Optional[str] = None
    is_public: bool = False

    model_config = ConfigDict()


ExcludedAreaCreateFeature = Feature[Union[Polygon, MultiPolygon], ExcludedAreaCreateParameters]
ExcludedAreaCreateCollection = FeatureCollection[ExcludedAreaCreateFeature]


def create_excluded_area(params: ExcludedAreaCreateFeature, accountId: Optional[UUID] = None) -> ExcludedAreaFeature:
    params_as_dict = params.properties.model_dump(exclude_none=True)
    if accountId:
        params_as_dict["account_id"] = accountId

    fields = [Identifier(f) for f in params_as_dict.keys()]
    values = [Literal(v) for v in params_as_dict.values()]

    # Handle geometry
    fields.append(Identifier("geom"))
    values.append(SQL("ST_Multi(ST_GeomFromText({}))").format(Literal(params.geometry.wkt)))

    return db.fetchone(
        current_app,
        SQL(
            """INSERT INTO excluded_areas({fields}) VALUES({values})
RETURNING
    'Feature' as type,
    json_build_object(
        'id', id,
        'label', label,
        'is_public', is_public,
        'account_id', account_id
    ) as properties,
    ST_AsGeoJSON(geom)::json as geometry"""
        ).format(fields=SQL(", ").join(fields), values=SQL(", ").join(values)),
        row_factory=class_row(ExcludedAreaFeature),
    )


def replace_excluded_areas(params: ExcludedAreaCreateCollection, invert: bool = False):
    with db.conn(current_app) as conn, conn.transaction(), conn.cursor(row_factory=class_row(ExcludedAreaFeature)) as cursor:
        # Remove all general areas
        cursor.execute("DROP INDEX excluded_areas_geom_idx")
        cursor.execute("DELETE FROM excluded_areas WHERE account_id IS NULL")

        # Append new ones
        # Invert given geometries if necessary
        if invert:
            # Insert geometries into a tmp table
            cursor.execute("CREATE TEMPORARY TABLE allowed_areas(geom GEOMETRY(MultiPolygon, 4326))")
            with cursor.copy("COPY allowed_areas(geom) FROM STDIN") as copy:
                for f in params.features:
                    copy.write_row([f.geometry.wkt])

            # Compute excluded areas and save in final table
            cursor.execute(
                """INSERT INTO excluded_areas(is_public, geom)
SELECT true, ST_Subdivide(
    ST_Difference(
        ST_SetSRID(ST_MakeEnvelope(-180, -90, 180, 90), 4326),
        ST_Union(geom)
    ),
    500
) AS geom
FROM allowed_areas"""
            )

        # Send areas as is if no invert required
        else:
            with cursor.copy("COPY excluded_areas(label, is_public, geom) FROM STDIN") as copy:
                for f in params.features:
                    copy.write_row(
                        (f.properties.label, f.properties.is_public if f.properties.is_public is not None else True, f.geometry.wkt)
                    )

        # Restore index
        cursor.execute("CREATE INDEX excluded_areas_geom_idx ON excluded_areas USING GIST(geom)")


@bp.route("/configuration/excluded_areas")
def getExcludedAreas():
    """List excluded areas
    ---
    tags:
            - Excluded Areas
            - Metadata
    parameters:
            - name: all
              in: query
              description: To fetch all areas, including not public ones. all=true needs admin rights for access.
              required: false
              schema:
                    type: boolean
    responses:
            200:
                    description: the list of excluded areas, as GeoJSON
                    content:
                            application/geo+json:
                                    schema:
                                            $ref: '#/components/schemas/GeoVisioExcludedAreas'
    """

    allAreas = request.args.get("all", "false").lower() == "true"
    account = auth.get_current_account()

    # Check access rights for listing all excluded areas
    if allAreas:
        if not account:
            raise InvalidAPIUsage(_("You must be logged-in as admin to access all excluded areas"), status_code=401)
        elif not account.can_edit_excluded_areas():
            raise InvalidAPIUsage(_("You're not authorized to access all excluded areas"), status_code=403)

    # Send result
    areas = list_excluded_areas(is_public=None if allAreas else True)
    return areas.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/geo+json"}


@bp.route("/configuration/excluded_areas", methods=["POST"])
@auth.login_required_with_redirect()
def postExcludedArea(account):
    """Add a new general excluded area.

    This call is only available for account with admin role.
    ---
    tags:
        - Excluded Areas
    requestBody:
        content:
            application/geo+json:
                schema:
                    $ref: '#/components/schemas/GeoVisioExcludedAreaCreateFeature'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the list of excluded areas, as GeoJSON
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioExcludedArea'
    """

    if request.is_json and request.json is not None:
        try:
            params = ExcludedAreaCreateFeature(**request.json)
        except ValidationError as ve:
            raise InvalidAPIUsage(_("Impossible to create an Excluded Area"), payload=validation_error(ve))
    else:
        raise InvalidAPIUsage(_("Parameter for creating an Excluded Area should be a valid JSON"), status_code=415)

    if not account.can_edit_excluded_areas():
        raise InvalidAPIUsage(_("You must be logged-in as admin to edit excluded areas"), 403)

    try:
        area = create_excluded_area(params)
    except Exception as e:
        raise InternalError(_("Impossible to create an Excluded Area"), status_code=500, payload={"details": str(e)})

    return (
        area.model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/geo+json",
        },
    )


@bp.route("/configuration/excluded_areas", methods=["PUT"])
@auth.login_required_with_redirect()
def replaceExcludedAreas(account):
    """Replace the whole set of general excluded areas with given ones.

    This call is only available for account with admin role.
    ---
    tags:
        - Excluded Areas
    parameters:
    - name: invert
      in: query
      description: Set to true if you want to send allowed areas instead of excluded ones. Note that using this parameter will make all generated excluded areas as publicly visible.
      required: false
      schema:
        type: boolean
    requestBody:
        content:
            application/geo+json:
                schema:
                    $ref: '#/components/schemas/GeoVisioExcludedAreaCreateCollection'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the list of excluded areas, as GeoJSON
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioExcludedAreas'
    """

    if request.is_json and request.json is not None:
        try:
            params = ExcludedAreaCreateCollection(**request.json)
        except ValidationError as ve:
            raise InvalidAPIUsage(_("Impossible to replace all Excluded Areas"), payload=validation_error(ve))
    else:
        raise InvalidAPIUsage(_("Parameter for replacing all Excluded Areas should be a valid JSON"), status_code=415)

    if not account.can_edit_excluded_areas():
        raise InvalidAPIUsage(_("You must be logged-in as admin to edit excluded areas"), 403)

    invert = request.args.get("invert", "false").lower() == "true"

    try:
        replace_excluded_areas(params, invert)
    except Exception as e:
        raise InternalError(_("Impossible to replace all Excluded Areas"), status_code=500, payload={"details": str(e)})

    # Send result
    areas = list_excluded_areas(is_public=None)
    return areas.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/geo+json"}


@bp.route("/configuration/excluded_areas/<uuid:areaId>", methods=["DELETE"])
@auth.login_required_with_redirect()
def deleteExcludedArea(areaId, account):
    """Delete an existing excluded area
    ---
    tags:
        - Excluded Areas
    parameters:
        - name: areaId
          in: path
          description: ID of excluded area to delete
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

    if not account.can_edit_excluded_areas():
        raise InvalidAPIUsage(_("You must be logged-in as admin to delete excluded areas"), 403)

    return delete_excluded_area(areaId)


@bp.route("/users/me/excluded_areas", methods=["GET"])
@auth.login_required_with_redirect()
def getUserExcludedAreas(account):
    """List excluded areas for current user.

    This only includes user-specific areas. For general excluded areas, see /api/configuration/excluded_areas.
    ---
    tags:
        - Excluded Areas
        - Users
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the list of user-specific excluded areas, as GeoJSON
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioExcludedAreas'
    """

    # Send result
    areas = list_excluded_areas(account_id=account.id)
    return areas.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/geo+json"}


@bp.route("/users/me/excluded_areas", methods=["POST"])
@auth.login_required_with_redirect()
def postUserExcludedArea(account):
    """Add a new excluded area for a specific user.

    Note that this excluded area will only apply to pictures uploaded by given user.
    For general excluded areas, use POST/PUT /api/configuration/excluded_areas instead.
    ---
    tags:
        - Excluded Areas
        - Users
    requestBody:
        content:
            application/geo+json:
                schema:
                    $ref: '#/components/schemas/GeoVisioExcludedAreaCreateFeature'
    security:
            - bearerToken: []
            - cookieAuth: []
    responses:
            200:
                description: the added excluded area
                content:
                    application/geo+json:
                        schema:
                            $ref: '#/components/schemas/GeoVisioExcludedArea'
    """

    if request.is_json and request.json is not None:
        try:
            params = ExcludedAreaCreateFeature(**request.json)
        except ValidationError as ve:
            raise InvalidAPIUsage(_("Impossible to create an Excluded Area"), payload=validation_error(ve))
    else:
        raise InvalidAPIUsage(_("Parameter for creating an Excluded Area should be a valid JSON"), status_code=415)

    try:
        area = create_excluded_area(params, UUID(account.id))
    except Exception as e:
        raise InternalError(_("Impossible to create an Excluded Area"), status_code=500, payload={"details": str(e)})

    return (
        area.model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/geo+json",
        },
    )


@bp.route("/users/me/excluded_areas/<uuid:areaId>", methods=["DELETE"])
@auth.login_required_with_redirect()
def deleteUserExcludedArea(areaId, account):
    """Delete an existing excluded area for current user
    ---
    tags:
        - Excluded Areas
        - Users
    parameters:
        - name: areaId
          in: path
          description: ID of excluded area to delete
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

    return delete_excluded_area(areaId, accountId=UUID(account.id))
