from typing import List, Optional
from uuid import UUID
import flask
from flask import request, current_app, session, url_for
from flask_babel import gettext as _
from pydantic import BaseModel, ConfigDict, ValidationError, computed_field
from geovisio.utils import auth, db
from geovisio import errors
from psycopg.rows import dict_row, class_row
from psycopg.sql import SQL

from geovisio.utils.link import Link, make_link
from geovisio.utils.model_query import get_db_params_and_values
from geovisio.utils.params import validation_error
from geovisio.web import stac
from geovisio.web.auth import NEXT_URL_KEY
from geovisio.web.utils import get_root_link

bp = flask.Blueprint("user", __name__, url_prefix="/api/users")


class Permissions(BaseModel):
    """Role and permissions of a user"""

    role: auth.AccountRole
    """Role of the user"""
    can_check_reports: bool
    """Is account legitimate to read any report ?"""
    can_edit_excluded_areas: bool
    """Is account legitimate to read and edit excluded areas ?"""
    can_edit_pages: bool
    """Is account legitimate to edit web pages ?"""

    model_config = ConfigDict(use_attribute_docstrings=True, use_enum_values=True)


class UserInfo(BaseModel):
    name: str
    """Name of the user"""
    id: UUID
    """Unique identifier of the user"""
    collaborative_metadata: Optional[bool] = None
    """If true, the user can edit the metadata of all sequences. If unset, default to the instance's default configuration."""

    tos_accepted: Optional[bool] = None
    """True means the user has accepted the terms of service (tos). Can only be seen by the user itself"""

    permissions: Optional[Permissions] = None
    """The user role and permissions. Can only be seen by the user itself"""

    model_config = ConfigDict(use_attribute_docstrings=True)

    @computed_field
    @property
    def links(self) -> List[Link]:
        userMapUrl = (
            flask.url_for("map.getUserTile", userId=self.id, x="11111111", y="22222222", z="33333333", format="mvt", _external=True)
            .replace("11111111", "{x}")
            .replace("22222222", "{y}")
            .replace("33333333", "{z}")
        )
        return [
            make_link(rel="catalog", route="stac.getUserCatalog", userId=self.id),
            make_link(rel="collection", route="stac_collections.getUserCollection", userId=self.id),
            Link(
                rel="user-xyz",
                type="application/vnd.mapbox-vector-tile",
                title="Pictures and sequences vector tiles for a given user",
                href=userMapUrl,
            ),
        ]


def _get_user_info(account: auth.Account):
    user_info = UserInfo(id=account.id, name=account.name, collaborative_metadata=account.collaborative_metadata)
    logged_account = auth.get_current_account()
    if logged_account is not None and account.id == logged_account.id:
        # we show the term of service acceptance only if the user is the logged user and if ToS are mandatory
        if flask.current_app.config["API_ENFORCE_TOS_ACCEPTANCE"]:
            user_info.tos_accepted = account.tos_accepted
        user_info.permissions = Permissions(
            role=account.role,
            can_check_reports=account.can_check_reports(),
            can_edit_excluded_areas=account.can_edit_excluded_areas(),
            can_edit_pages=account.can_edit_pages(),
        )

    return user_info.model_dump(exclude_unset=True), 200, {"Content-Type": "application/json"}


@bp.route("/me")
@auth.login_required_with_redirect()
def getMyUserInfo(account):
    """Get current logged user information
    ---
    tags:
        - Users
    responses:
        200:
            description: Information about the logged in account
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUser'
    """
    return _get_user_info(account)


@bp.route("/<uuid:userId>")
def getUserInfo(userId):
    """Get user information
    ---
    tags:
        - Users
    parameters:
        - name: userId
          in: path
          description: User ID
          required: true
          schema:
            type: string
    responses:
        200:
            description: Information about a user
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUser'
    """
    account = db.fetchone(
        current_app,
        SQL("SELECT name, id::text, collaborative_metadata, role, tos_accepted FROM accounts WHERE id = %s"),
        [userId],
        row_factory=class_row(auth.Account),
    )
    if not account:
        raise errors.InvalidAPIUsage(_("Impossible to find user"), status_code=404)

    return _get_user_info(account)


@bp.route("/me/catalog")
@auth.login_required_with_redirect()
def getMyCatalog(account):
    """Get current logged user catalog.

    Note that this route is deprecated in favor of `/api/users/me/collection`. This new route provides more information and offers more filtering and sorting options.
    ---
    tags:
        - Users
        - Sequences
    deprecated: true
    responses:
        200:
            description: the Catalog listing all sequences associated to given user. Note that it's similar to the user's collection, but with less metadata since a STAC collection is an enhanced STAC catalog.
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCatalog'
    """
    return flask.redirect(
        flask.url_for(
            "stac.getUserCatalog",
            userId=account.id,
            limit=request.args.get("limit"),
            page=request.args.get("page"),
            _external=True,
        )
    )


@bp.route("/me/collection")
@auth.login_required_with_redirect()
def getMyCollection(account):
    """Get current logged user collection

    Note that the result can also be a CSV file, if the "Accept" header is set to "text/csv", or if the "format" query parameter is set to "csv".

    ---
    tags:
        - Users
        - Sequences
    parameters:
        - name: format
          in: query
          description: Expected output format (STAC JSON or a csv file)
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
            description: the Collection listing all sequences associated to given user. Note that it's similar to the user's catalog, but with more metadata since a STAC collection is an enhanced STAC catalog.
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCollectionOfCollection'

                text/csv:
                    schema:
                        $ref: '#/components/schemas/GeoVisioCSVCollections'
    """
    from geovisio.web.collections import getUserCollection

    return getUserCollection(userId=account.id, userIdMatchesAccount=True)


@bp.route("/search")
def searchUser():
    """Search for a user
    ---
    tags:
        - Users
    responses:
        200:
            description: List of matching users
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUserSearch'
    """
    q = request.args.get("q")
    # for the moment, we can only search by string
    if not q:
        raise errors.InvalidAPIUsage(_("No search parameter given, you should provide `q=<pattern>` as query parameter"), status_code=400)

    limit = request.args.get("limit", default=20, type=int)
    query = SQL(
        """
WITH ranked AS (
    SELECT name, id, similarity({q}, name) AS similarity from accounts
)
SELECT * from ranked 
WHERE similarity > 0.1
ORDER BY similarity DESC
LIMIT {limit};
"""
    ).format(limit=limit, q=q)
    res = db.fetchall(current_app, query, row_factory=dict_row)

    return {
        "features": [
            {
                "label": r["name"],
                "id": r["id"],
                "links": [
                    {
                        "rel": "user-info",
                        "type": "application/json",
                        "href": flask.url_for("user.getUserInfo", userId=r["id"], _external=True),
                    },
                    {
                        "rel": "collection",
                        "type": "application/json",
                        "href": flask.url_for("stac_collections.getUserCollection", userId=r["id"], _external=True),
                    },
                ],
            }
            for r in res
        ]
    }


@bp.route("/")
def listUsers():
    """List all users
    ---
    tags:
        - Users
    responses:
        200:
            description: List of users
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUserList'
    """

    # no pagination yet, can be done when needed
    limit = min(request.args.get("limit", default=1000, type=int), 1000)
    query = SQL(
        """SELECT 
a.id, a.name, l.has_seq
FROM accounts a
LEFT OUTER JOIN LATERAL (
   SELECT 1 as has_seq
   FROM sequences s
   WHERE s.account_id = a.id
   LIMIT 1
) l ON true
ORDER BY created_at
LIMIT {limit};"""
    ).format(limit=limit)
    res = db.fetchall(current_app, query, row_factory=dict_row)
    return {
        "stac_version": stac.STAC_VERSION,
        "id": "geovisio:users",
        "title": "users catalog",
        "description": "List of users catalog",
        "type": "Catalog",
        "conformsTo": stac.CONFORMANCE_LIST,
        "users": [
            {
                "name": r["name"],
                "id": r["id"],
                "links": [
                    {
                        "rel": "user-info",
                        "type": "application/json",
                        "href": flask.url_for("user.getUserInfo", userId=r["id"], _external=True),
                    },
                    {
                        "rel": "collection",
                        "type": "application/json",
                        "href": flask.url_for("stac_collections.getUserCollection", userId=r["id"], _external=True),
                    },
                ],
            }
            for r in res
        ],
        "links": [
            {
                "rel": "user-search",
                "type": "application/json",
                "href": flask.url_for("user.searchUser", _external=True),
                "title": "Search users",
            },
            get_root_link(),
        ]
        + [
            {
                "rel": "child",
                "title": f'User "{r["name"]}" sequences',
                "href": url_for("stac_collections.getUserCollection", userId=r["id"], _external=True),
            }
            for r in res
            if r["has_seq"]
        ],
    }


class UserConfiguration(BaseModel):
    collaborative_metadata: Optional[bool] = None
    """If true, all sequences's metadata will be, by default, editable by all users.
    
    If not set, it will default to the instance default collaborative editing policy."""

    def has_override(self) -> bool:
        return bool(self.model_fields_set)


@bp.route("/me", methods=["PATCH"])
@auth.login_required()
def patchUserConfiguration(account):
    """Edit the current user configuration

    ---
    tags:
        - Users
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioUserConfiguration'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the user configuration
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUser'
    """
    metadata = None
    try:
        if request.is_json and request.json:
            metadata = UserConfiguration(**request.json)
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    if not metadata:
        return _get_user_info(account)
    params = get_db_params_and_values(metadata)
    if metadata.has_override():

        fields = params.fields_for_set_list()

        account = db.fetchone(
            current_app,
            SQL("UPDATE accounts SET {fields} WHERE id = %(account_id)s RETURNING *").format(fields=SQL(", ").join(fields)),
            params.params_as_dict | {"account_id": account.id},
            row_factory=class_row(auth.Account),
        )

    return _get_user_info(account)


@bp.route("/me/accept_tos", methods=["POST"])
@auth.login_required()
def accept_tos(account: auth.Account):
    """
    Accept the terms of service for the current user
    ---
    tags:
        - Auth
    responses:
        200:
            description: the user configuration
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUser'
    """
    # Note: accepting twice does not change the accepted_at date
    account = db.fetchone(
        current_app,
        SQL("UPDATE accounts SET tos_accepted_at = COALESCE(tos_accepted_at, NOW()) WHERE id = %(account_id)s RETURNING *"),
        {"account_id": account.id},
        row_factory=class_row(auth.Account),
    )

    # we persist in the cookie the fact that the tos have been accepted
    session[auth.ACCOUNT_KEY] = account.model_dump(exclude_none=True)
    session.permanent = True

    return _get_user_info(account)
