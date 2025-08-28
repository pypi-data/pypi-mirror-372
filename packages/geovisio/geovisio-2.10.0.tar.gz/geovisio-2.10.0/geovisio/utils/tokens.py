from geovisio import errors
from geovisio.utils import auth, db
from geovisio.web.tokens import _decode_jwt_token, _generate_jwt_token
from authlib.jose.errors import BadSignatureError
from flask import current_app
from flask_babel import gettext as _
from psycopg.rows import dict_row


import logging


class InvalidTokenException(errors.InvalidAPIUsage):
    def __init__(self, details, status_code=401):
        msg = "Token not valid"
        super().__init__(msg, status_code=status_code, payload={"details": {"error": details}})


def get_account_from_jwt_token(jwt_token: str) -> auth.Account:
    """
    Get the account corresponding to a JWT token.

    Parameters
    ----------
    jwt_token : str
            JWT token

    Returns
    -------
    auth.Account
            Corresponding Account

    Raises
    ------
    InvalidTokenException
            If the token is not correctly signed, or if the token is not valid anymore
    """
    try:
        decoded = _decode_jwt_token(jwt_token)
    except BadSignatureError:
        logging.exception("invalid signature of jwt token")
        raise InvalidTokenException(_("JWT token signature does not match"))
    token_id = decoded["sub"]

    with db.cursor(current_app, row_factory=dict_row) as cursor:
        # check token existence
        records = cursor.execute(
            """SELECT
    t.account_id AS id, a.name, a.oauth_provider, a.oauth_id, a.role, a.collaborative_metadata, a.tos_accepted
FROM tokens t
LEFT OUTER JOIN accounts a ON t.account_id = a.id
WHERE t.id = %(token)s""",
            {"token": token_id},
        ).fetchone()
        if not records:
            raise InvalidTokenException(_("Token does not exist anymore"), status_code=403)

        if not records["id"]:
            raise InvalidTokenException(
                _("Token not yet claimed, this token cannot be used yet. Either claim this token or generate a new one"), status_code=403
            )

        return auth.Account(
            id=records["id"],
            name=records["name"],
            oauth_provider=records["oauth_provider"],
            oauth_id=records["oauth_id"],
            role=auth.AccountRole(records["role"]),
            collaborative_metadata=records["collaborative_metadata"],
            tos_accepted=records["tos_accepted"],
        )


def get_default_account_jwt_token() -> str:
    """
    Get the default account JWT token.

    Note: do not expose this method externally, only an instance administrator should be able to get the default account JWT token!
    """

    with db.cursor(current_app, row_factory=dict_row) as cursor:
        # check token existence
        records = cursor.execute(
            """
                SELECT t.id AS id
                FROM tokens t
                JOIN accounts a ON t.account_id = a.id
                WHERE a.is_default
            """
        ).fetchone()
        if not records:
            raise Exception("Default account has no associated token")

        return _generate_jwt_token(records["id"])
