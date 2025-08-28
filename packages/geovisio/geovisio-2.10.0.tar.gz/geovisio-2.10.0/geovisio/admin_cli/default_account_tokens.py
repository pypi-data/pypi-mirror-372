from flask import Blueprint
from flask.cli import with_appcontext
from geovisio.utils import tokens

bp = Blueprint("default-account-token", __name__)


@bp.cli.command("get")
@with_appcontext
def get_default():
    """
    Get JWT default account token

    Note: Be sure to not share this JWT token!
    """
    try:
        print(tokens.get_default_account_jwt_token())
    except Exception as e:
        print(f"Impossible to get default account's JWT token: {e}")
