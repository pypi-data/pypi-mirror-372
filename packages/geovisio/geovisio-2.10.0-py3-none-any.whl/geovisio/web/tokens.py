import flask
from flask import current_app, url_for, request
from flask_babel import gettext as _
from dateutil import tz
from psycopg.rows import dict_row
from authlib.jose import jwt
from authlib.jose.errors import DecodeError
import logging
import uuid
from geovisio.utils import auth, db, website
from geovisio import errors, utils


bp = flask.Blueprint("tokens", __name__, url_prefix="/api")


@bp.route("/users/me/tokens", methods=["GET"])
@auth.login_required_with_redirect()
def list_tokens(account):
    """
    List the tokens of a authenticated user

    The list of tokens will not contain their JWT counterpart (the JWT is the real token used in authentication).

    The JWT counterpart can be retrieved by providing the token's id to the endpoint [/users/me/tokens/{token_id}](#/Auth/get_api_users_me_tokens__token_id_).
    ---
    tags:
        - Auth
        - Users
    responses:
        200:
            description: The list of tokens, without their JWT counterpart.
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioTokens'
    """

    records = db.fetchall(
        current_app,
        "SELECT id, description, generated_at FROM tokens WHERE account_id = %(account)s",
        {"account": account.id},
        row_factory=dict_row,
    )

    tokens = [
        {
            "id": r["id"],
            "description": r["description"],
            "generated_at": r["generated_at"].astimezone(tz.gettz("UTC")).isoformat(),
            "links": [
                {
                    "rel": "self",
                    "type": "application/json",
                    "href": url_for("tokens.get_jwt_token", token_id=r["id"], _external=True),
                }
            ],
        }
        for r in records
    ]
    return flask.jsonify(tokens)


@bp.route("/users/me/tokens/<uuid:token_id>", methods=["GET"])
@auth.login_required_with_redirect()
def get_jwt_token(token_id: uuid.UUID, account: auth.Account):
    """
    Get the JWT token corresponding to a token id.

    This JWT token will be needed to authenticate others api calls
    ---
    tags:
        - Auth
        - Users
    parameters:
        - name: token_id
          in: path
          description: ID of the token
          required: true
          schema:
            type: string
    responses:
        200:
            description: The token, with it's JWT counterpart.
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioEncodedToken'
    """

    token = db.fetchone(
        current_app,
        "SELECT id, description, generated_at FROM tokens WHERE account_id = %(account)s AND id = %(token)s",
        {"account": account.id, "token": token_id},
        row_factory=dict_row,
    )

    # check token existence
    if not token:
        raise errors.InvalidAPIUsage(_("Impossible to find token"), status_code=404)

    jwt_token = _generate_jwt_token(token["id"])
    return flask.jsonify(
        {
            "jwt_token": jwt_token,
            "id": token["id"],
            "description": token["description"],
            "generated_at": token["generated_at"].astimezone(tz.gettz("UTC")).isoformat(),
        }
    )


@bp.route("/users/me/tokens/<uuid:token_id>", methods=["DELETE"])
@auth.login_required_with_redirect()
def revoke_token(token_id: uuid.UUID, account: auth.Account):
    """
    Delete a token corresponding to a token id.

    This token will not be usable anymore
    ---
    tags:
        - Auth
    parameters:
        - name: token_id
          in: path
          description: ID of the token
          required: true
          schema:
            type: string
    responses:
        200:
            description: The token has been correctly deleted
    """

    with db.execute(
        current_app,
        "DELETE FROM tokens WHERE account_id = %(account)s AND id = %(token)s",
        {"account": account.id, "token": token_id},
    ) as res:
        token_deleted = res.rowcount

        if not token_deleted:
            raise errors.InvalidAPIUsage(_("Impossible to find token"), status_code=404)
        return flask.jsonify({"message": "token revoked"}), 200


@bp.route("/auth/tokens/generate", methods=["POST"])
def generate_non_associated_token():
    """
    Generate a new token, not associated to any user

    The response contains the JWT token, and this token can be saved, but won't be usable until someone claims it with /auth/tokens/claims/:id

    The response contains the claim route as a link with `rel`=`claim`.
    ---
    tags:
        - Auth
    parameters:
        - name: description
          in: query
          description: optional description of the token
          schema:
            type: string
    responses:
        200:
            description: The newly generated token
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/JWTokenClaimable'
    """
    description = request.args.get("description", "")

    token = db.fetchone(
        current_app,
        "INSERT INTO tokens (description) VALUES (%(description)s) RETURNING *",
        {"description": description},
        row_factory=dict_row,
    )
    if not token:
        raise errors.InternalError(_("Impossible to generate a new token"))

    jwt_token = _generate_jwt_token(token["id"])
    token = {
        "id": token["id"],
        "jwt_token": jwt_token,
        "description": token["description"],
        "generated_at": token["generated_at"].astimezone(tz.gettz("UTC")).isoformat(),
        "links": [
            {
                "rel": "claim",
                "type": "application/json",
                "href": url_for("tokens.claim_non_associated_token", token_id=token["id"], _external=True),
            }
        ],
    }
    return flask.jsonify(token)


@bp.route("/auth/tokens/<uuid:token_id>/claim", methods=["GET"])
@auth.login_required_with_redirect()
def claim_non_associated_token(token_id, account):
    """
    Claim a non associated token

    The token will now be associated to the logged user.

    Only one user can claim a token
    ---
    tags:
        - Auth
    parameters:
        - name: token_id
          in: path
          description: Token ID
          required: true
          schema:
            type: string
    responses:
        200:
            description: The token has been correctly associated to the account
    """
    with db.cursor(current_app, row_factory=dict_row) as cursor:
        token = cursor.execute(
            "SELECT account_id FROM tokens WHERE id = %(token)s",
            {"token": token_id},
        ).fetchone()
        if not token:
            raise errors.InvalidAPIUsage(_("Impossible to find token"), status_code=404)

        associated_account = token["account_id"]
        if associated_account:
            if associated_account != account.id:
                raise errors.InvalidAPIUsage(_("Token already claimed by another account"), status_code=403)
            else:
                return flask.jsonify({"message": "token already associated to account"}), 200

        cursor.execute(
            "UPDATE tokens SET account_id = %(account)s WHERE id = %(token)s",
            {"account": account.id, "token": token_id},
        )

        next_url = None
        if account.tos_accepted is False and current_app.config["API_ENFORCE_TOS_ACCEPTANCE"]:
            # if the tos have not been accepted, we redirect to the website page to accept it (with a redirect afterward to the token associated page)
            next_url = current_app.config["API_WEBSITE_URL"].tos_validation_page({"next_url": "/token-accepted"})
        else:
            next_url = current_app.config["API_WEBSITE_URL"].cli_token_accepted_page()

        if next_url:
            # if there is an associated website, we redirect with a nice page explaining the token association
            return flask.redirect(next_url)
        # else we return a simple text to explain it
        return "You are now logged in the CLI, you can upload your pictures", 200


@bp.route("/users/me/tokens", methods=["POST"])
@auth.login_required_with_redirect()
def generate_associated_token(account: auth.Account):
    """
    Generate a new token associated to the current user

    The response contains the JWT token and is directly usable (unlike tokens created by `/auth/tokens/generate` that are not associated to a user by default). This token does not need to be claimed.
    ---
    tags:
        - Auth
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeovisioPostToken'
    responses:
        200:
            description: The newly generated token
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioEncodedToken'
    """
    if request.is_json:
        description = request.json.get("description", "")
    else:
        description = None

    token = db.fetchone(
        current_app,
        "INSERT INTO tokens (description, account_id) VALUES (%(description)s, %(account_id)s) RETURNING *",
        {"account_id": account.id, "description": description},
        row_factory=dict_row,
    )
    if not token:
        raise errors.InternalError(_("Impossible to generate a new token"))

    jwt_token = _generate_jwt_token(token["id"])
    return flask.jsonify(
        {
            "jwt_token": jwt_token,
            "id": token["id"],
            "description": token["description"],
            "generated_at": token["generated_at"].astimezone(tz.gettz("UTC")).isoformat(),
        }
    )


def _generate_jwt_token(token_id: uuid.UUID) -> str:
    """
    Generate a JWT token from a token's id.

    The JWT token will be signed but not encrypted.

    This will makes the jwt token openly readable, but only a geovisio instance can issue validly signed tokens
    """
    header = {"alg": "HS256"}
    payload = {
        "iss": "geovisio",  # Issuer is optional and not used, but it just tell who issued this token
        "sub": str(token_id),
    }
    secret = current_app.config["SECRET_KEY"]

    if not secret:
        raise NoSecretKeyException()

    s = jwt.encode(header, payload, secret)

    return str(s, "utf-8")


def _decode_jwt_token(jwt_token: str) -> dict:
    """
    Decode a JWT token
    """
    secret = current_app.config["SECRET_KEY"]
    if not secret:
        raise NoSecretKeyException()
    try:
        return jwt.decode(jwt_token, secret)
    except DecodeError as e:
        logging.error(f"Impossible to decode token: {e}")
        raise utils.tokens.InvalidTokenException("Impossible to decode token")


class NoSecretKeyException(errors.InternalError):
    def __init__(self):
        msg = "No SECRET_KEY has been defined for the instance (defined by FLASK_SECRET_KEY environment variable), authentication is not possible. Please contact your instance administrator if this is needed."
        super().__init__(msg)
