from ast import Dict
from uuid import UUID
from click import Option
import flask
from flask import current_app, url_for, session, redirect, request
from flask_babel import gettext as _
from functools import wraps
from authlib.integrations.flask_client import OAuth
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import Any
from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator
import sentry_sdk
from psycopg.rows import dict_row
from geovisio import errors
from geovisio.utils import db


ACCOUNT_KEY = "account"  # Key in flask's session with the account's information

oauth = OAuth()
oauth_provider = None


@dataclass
class OAuthUserAccount(object):
    id: str
    name: str


class OAuthProvider(ABC):
    """Base class for oauth provider. Need to specify how to get user's info"""

    name: str
    client: Any

    def __init__(self, name, **kwargs) -> None:
        super(OAuthProvider, self).__init__()
        self.name = name
        self.client = oauth.register(name=name, **kwargs)

    @abstractmethod
    def get_user_oauth_info(self, tokenResponse) -> OAuthUserAccount:
        pass

    def logout_url(self):
        return None

    def user_profile_page_url(self):
        """
        URL to a user settings page.
        This URL should point to a web page where user can edit its password or email address,
        if that makes sense regarding your GeoVisio instance.

        This is useful if your instance has its own specific identity provider. It may not be used if you rely on third-party auth provider.
        """
        return None


class OIDCProvider(OAuthProvider):
    def __init__(self, *args, **kwargs) -> None:
        super(OIDCProvider, self).__init__(*args, **kwargs)

    def get_user_oauth_info(self, tokenResponse) -> OAuthUserAccount:
        # user info is alway provided by oidc provider, nothing to do
        # we only need the 'sub' (subject) claim
        oidc_userinfo = tokenResponse["userinfo"]
        return OAuthUserAccount(id=oidc_userinfo["sub"], name=oidc_userinfo["preferred_username"])


class KeycloakProvider(OIDCProvider):
    def __init__(self, keycloack_realm_user, client_id, client_secret) -> None:
        super().__init__(
            name="keycloak",
            client_id=client_id,
            client_secret=client_secret,
            server_metadata_url=f"{keycloack_realm_user}/.well-known/openid-configuration",
            client_kwargs={
                "scope": "openid",
                "code_challenge_method": "S256",  # enable PKCE
            },
        )
        self._logout_url = f"{keycloack_realm_user}/protocol/openid-connect/logout?client_id={client_id}"
        self._user_profile_page_url = f"{keycloack_realm_user}/account/#/personal-info"

    def logout_url(self):
        return self._logout_url

    def user_profile_page_url(self):
        return self._user_profile_page_url


class OSMOAuthProvider(OAuthProvider):
    def __init__(self, oauth_key, oauth_secret) -> None:
        super().__init__(
            name="osm",
            client_id=oauth_key,
            client_secret=oauth_secret,
            api_base_url="https://api.openstreetmap.org/api/0.6/",
            authorize_url="https://www.openstreetmap.org/oauth2/authorize",
            access_token_url="https://www.openstreetmap.org/oauth2/token",
            client_kwargs={
                "scope": "read_prefs",
            },
        )

    def get_user_oauth_info(self, tokenResponse) -> OAuthUserAccount:
        """Get the id/name of the logged user from osm's API
        cf. https://wiki.openstreetmap.org/wiki/API_v0.6
        Args:
                        tokenResponse: access token to the OSM api, will be automatically used to query the OSM API

        Returns:
                        OAuthUserAccount: id and name of the account
        """
        details = self.client.get("user/details.json")
        details.raise_for_status()
        details = details.json()
        return OAuthUserAccount(id=str(details["user"]["id"]), name=details["user"]["display_name"])


def make_auth(app):
    def ensure(*app_config_key):
        missing = [k for k in app_config_key if k not in app.config]
        if missing:
            raise Exception(f"To setup an oauth provider, you need to provide {missing} in configuration")

    global oauth_provider, oauth
    oauth = OAuth()
    if app.config.get("OAUTH_PROVIDER") == "oidc":
        ensure("OAUTH_OIDC_URL", "OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET")

        oauth_provider = KeycloakProvider(
            app.config["OAUTH_OIDC_URL"],
            app.config["OAUTH_CLIENT_ID"],
            app.config["OAUTH_CLIENT_SECRET"],
        )
    elif app.config.get("OAUTH_PROVIDER") == "osm":
        ensure("OAUTH_CLIENT_ID", "OAUTH_CLIENT_SECRET")

        oauth_provider = OSMOAuthProvider(
            app.config["OAUTH_CLIENT_ID"],
            app.config["OAUTH_CLIENT_SECRET"],
        )
    else:
        raise Exception(
            "Unsupported OAUTH_PROVIDER, should be either 'oidc' or 'osm'. If you want another provider to be supported, add a subclass to OAuthProvider"
        )
    oauth.init_app(app)

    return oauth


class AccountRole(Enum):
    user = "user"
    admin = "admin"


class Account(BaseModel):
    id: str
    name: str
    oauth_provider: Optional[str] = None
    oauth_id: Optional[str] = None
    tos_accepted: Optional[bool] = None

    def __init__(self, role: Optional[AccountRole] = None, **kwargs) -> None:
        # Note: since it's a valid state for the collaborative_metadata to be None,
        # we need to only set it if provided, this way we can check the `model_fields_set` to know if the collaborative_metadata is set
        collaborative_metadata_set = "collaborative_metadata" in kwargs
        collaborative_metadata = kwargs.pop("collaborative_metadata", None)
        super().__init__(**kwargs)
        self.role = role
        if collaborative_metadata_set:
            self.collaborative_metadata = collaborative_metadata

    # Note: those fields are excluded since we do not want to persist it in the cookie. It will be fetched from the database if needed
    role_: Optional[AccountRole] = Field(default=None, exclude=True)
    collaborative_metadata_: Optional[bool] = Field(default=None, exclude=True)

    @field_validator("id", mode="before")
    @classmethod
    def check_id(cls, value) -> str:
        if isinstance(value, UUID):
            return str(value)
        if isinstance(value, str):
            return value
        raise ValidationError("Invalid account id type")

    def can_check_reports(self):
        """Is account legitimate to read any report ?"""
        return self.role == AccountRole.admin

    def can_edit_excluded_areas(self):
        """Is account legitimate to read and edit excluded areas ?"""
        return self.role == AccountRole.admin

    def can_edit_pages(self):
        """Is account legitimate to edit web pages ?"""
        return self.role == AccountRole.admin

    @property
    def role(self) -> AccountRole:
        if self.role_ is None:
            self._fetch_database_info()
        return self.role_

    @role.setter
    def role(self, r: AccountRole | str) -> None:
        if isinstance(r, str):
            r = AccountRole(r)
        self.role_ = r

    @property
    def collaborative_metadata(self) -> Optional[bool]:
        if "collaborative_metadata_" not in self.model_fields_set:
            self._fetch_database_info()
        return self.collaborative_metadata_

    @collaborative_metadata.setter
    def collaborative_metadata(self, b: Optional[bool]) -> None:
        self.collaborative_metadata_ = b

    def _fetch_database_info(self):
        """Fetch the missing database metadata for this account"""
        r = db.fetchone(
            current_app,
            "SELECT role, collaborative_metadata FROM accounts WHERE id = %s",
            (self.id,),
            row_factory=dict_row,
        )
        self.role = AccountRole(r["role"])
        self.collaborative_metadata = r["collaborative_metadata"]


def account_allow_collaborative_editing(account_id: str | UUID):
    """An account allows collaborative editing it if has been allowed at the account level else we check the instance configuration"""
    r = db.fetchone(
        current_app,
        """SELECT COALESCE(accounts.collaborative_metadata, configurations.collaborative_metadata, true) AS collaborative_metadata
FROM accounts
JOIN configurations ON TRUE
WHERE accounts.id = %s""",
        [account_id],
        row_factory=dict_row,
    )
    return r["collaborative_metadata"]


def login_required():
    """Check that the user is logged in, and abort if it's not the case"""

    def actual_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            if "account" not in kwargs:
                account = get_current_account()
                if not account:
                    return flask.abort(flask.make_response(flask.jsonify(message=_("Authentication is mandatory")), 401))
                kwargs["account"] = account

            return f(*args, **kwargs)

        return decorator

    return actual_decorator


def login_required_by_setting(mandatory_login_param):
    """Check that the user is logged in, and abort if it's not the case

    Args:
            mandatory_login_param (str): name of the configuration parameter used to decide if the login is mandatory or not
    """

    def actual_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            account = get_current_account()
            if not account and current_app.config[mandatory_login_param]:
                return flask.abort(flask.make_response(flask.jsonify(message="Authentication is mandatory"), 401))
            if account and account.tos_accepted is False and current_app.config["API_ENFORCE_TOS_ACCEPTANCE"]:
                tos_acceptance_page = current_app.config["API_WEBSITE_URL"].tos_validation_page()
                raise errors.InvalidAPIUsage(
                    message=_(
                        "You need to accept the terms of service before uploading any pictures. You can do so by validating them here: %(url)s",
                        url=tos_acceptance_page,
                    ),
                    status_code=401,
                    payload={
                        "details": {
                            "validation_page": tos_acceptance_page,
                        }
                    },
                )
            kwargs["account"] = account

            return f(*args, **kwargs)

        return decorator

    return actual_decorator


def login_required_with_redirect():
    """Check that the user is logged in, and redirect if it's not the case"""

    def actual_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            account = get_current_account()
            if not account:
                if "OAUTH_PROVIDER" not in current_app.config:
                    return flask.abort(
                        flask.make_response(
                            flask.jsonify(message="Authentication has not been activated in this instance, impossible to log in."), 403
                        )
                    )
                return redirect(url_for("auth.login", next_url=request.url))
            kwargs["account"] = account

            return f(*args, **kwargs)

        return decorator

    return actual_decorator


def isUserIdMatchingCurrentAccount():
    """Check if given user ID matches the currently logged-in account"""

    def actual_decorator(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            account = get_current_account()
            userId = kwargs.get("userId")
            kwargs["userIdMatchesAccount"] = account is not None and userId is not None and account.id == str(userId)
            return f(*args, **kwargs)

        return decorator

    return actual_decorator


class UnknowAccountException(Exception):
    status_code = 401

    def __init__(self):
        msg = "No account with this oauth id is known, you should login first"
        super().__init__(msg)


class LoginRequiredException(Exception):
    status_code = 401

    def __init__(self):
        msg = "You should login to request this API"
        super().__init__(msg)


def get_current_account() -> Optional[Account]:
    """Get the authenticated account information.

    This account is either stored in the flask's session or retrieved with the Bearer token passed with an `Authorization` header.

    The flask session is usually used by browser, whereas the bearer token is handy for non interactive uses, like curls or CLI usage.

    Returns:
                    Account: the current logged account, None if nobody is logged
    """
    if ACCOUNT_KEY in session:
        a = session[ACCOUNT_KEY]
        session_account = Account(**a)

        sentry_sdk.set_user(session_account.model_dump(exclude_none=True))
        return session_account

    bearer_token = _get_bearer_token()
    if bearer_token:
        from geovisio.utils import tokens

        a = tokens.get_account_from_jwt_token(bearer_token)
        sentry_sdk.set_user(a.model_dump(exclude_none=True))
        return a

    return None


def _get_bearer_token() -> Optional[str]:
    """
    Get the associated bearer token from the `Authorization` header

    Raises:
            tokens.InvalidTokenException: if the token is not a bearer token
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    if not auth_header.startswith("Bearer "):
        from geovisio.utils.tokens import InvalidTokenException

        raise InvalidTokenException(_("Only Bearer token are supported"))
    return auth_header.split(" ")[1]
