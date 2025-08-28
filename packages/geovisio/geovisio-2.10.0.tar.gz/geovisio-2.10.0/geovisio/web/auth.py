import flask
from flask import current_app, url_for, session, redirect, request, jsonify
from flask_babel import gettext as _
from urllib.parse import quote
from geovisio import utils, errors
from geovisio.utils import db
from geovisio.utils.auth import Account, ACCOUNT_KEY
from authlib.integrations.base_client.errors import MismatchingStateError

bp = flask.Blueprint("auth", __name__, url_prefix="/api/auth")

NEXT_URL_KEY = "next-url"  # Key in flask's session with url to be redirected after the oauth dance


@bp.route("/login")
def login():
    """Log in geovisio

    Will log in the provided identity provider
    ---
    tags:
        - Auth
    responses:
        302:
            description: Identity provider login page
    """

    next_url = request.args.get("next_url")
    if next_url:
        # we store the next_url in the session, to be able to redirect the users to this url after the oauth dance
        session[NEXT_URL_KEY] = next_url
    return utils.auth.oauth_provider.client.authorize_redirect(url_for("auth.auth", _external=True, _scheme=request.scheme))


@bp.route("/redirect")
def auth():
    """Redirect endpoint after log in the identity provider

    This endpoint should be called by the identity provider after a sucessful login
    ---
    tags:
        - Auth
    responses:
        200:
            description: Information about the logged account
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioUserAuth'
            headers:
                Set-Cookie:
                    description: 2 cookies are set, `user_id` and `user-name`
                    schema:
                        type: string
    """
    try:
        tokenResponse = utils.auth.oauth_provider.client.authorize_access_token()
    except MismatchingStateError as e:
        raise errors.InternalError(
            _("Impossible to finish authentication flow"),
            payload={
                "details": {
                    "error": str(e),
                    "tips": _("You can try to clear your cookies and retry. If the problem persists, contact your instance administrator."),
                }
            },
            status_code=403,
        )

    oauth_info = utils.auth.oauth_provider.get_user_oauth_info(tokenResponse)
    with db.cursor(current_app) as cursor:
        res = cursor.execute(
            "INSERT INTO accounts (name, oauth_provider, oauth_id) VALUES (%(name)s, %(provider)s, %(id)s) ON CONFLICT (oauth_provider, oauth_id) DO UPDATE SET name = %(name)s RETURNING id, name, tos_accepted",
            {
                "provider": utils.auth.oauth_provider.name,
                "id": oauth_info.id,
                "name": oauth_info.name,
            },
        ).fetchone()
        if res is None:
            raise Exception("Impossible to insert user in database")
        id, name, tos_accepted = res
        account = Account(
            id=str(id),  # convert uuid to string for serialization
            name=name,
            oauth_provider=utils.auth.oauth_provider.name,
            oauth_id=oauth_info.id,
            tos_accepted=tos_accepted,
        )
        session[ACCOUNT_KEY] = account.model_dump(exclude_none=True)
        session.permanent = True

        next_url = session.pop(NEXT_URL_KEY, None)
        if not tos_accepted and current_app.config["API_ENFORCE_TOS_ACCEPTANCE"]:
            args = {"next_url": next_url} if next_url else None
            next_url = current_app.config["API_WEBSITE_URL"].tos_validation_page(args)

        if next_url is None:
            next_url = "/"

        response = flask.make_response(redirect(next_url))

        # also store id/name in cookies for the front end to use those
        max_age = current_app.config["PERMANENT_SESSION_LIFETIME"]
        _set_cookie(response, "user_id", str(id), max_age=max_age)
        _set_cookie(response, "user_name", quote(name), max_age=max_age)

        return response


@bp.route("/logout")
def logout():
    """Log out from geovisio
    * If the OAuth Provider is keycloak, this will redirect to a keycloak confirmation page,
            and upon confirmation keycloak will call post_logout_redirect that will invalidate the session
    * If the OAuth Provider is not keycloak, this will invalidate the session
    ---
    tags:
        - Auth
    parameters:
        - name: next_url
          in: query
          description: uri to redirect after logout. If none, no redirect is done and a 202 is returned
          schema:
            type: string
    responses:
        302:
            description: Either redirection to the oauth provider logout page for a confirmation or directly to the uri defined in the `next_url` query parameter after log out
        202:
            description: If the oauth provider has no logout page, and no `next_url` parameter is defined
    """
    logout_url = utils.auth.oauth_provider.logout_url()
    session[NEXT_URL_KEY] = request.args.get("next_url")
    if logout_url:
        logout_url = f"{logout_url}&post_logout_redirect_uri={quote(url_for('auth.post_logout_redirect', _external=True), safe='')}"
        return redirect(logout_url)
    else:
        return _log_out_response()


@bp.route("/post_logout_redirect")
def post_logout_redirect():
    """Log out endpoint called by OIDC server after logout on their part
    ---
    tags:
        - Auth
    responses:
        302:
            description: User logged out and redirected to another page
        202:
            description: User logged out
    """
    return _log_out_response()


def _log_out_response():
    session.pop(ACCOUNT_KEY, None)

    next_url = session.pop(NEXT_URL_KEY, None)

    if next_url:
        r = flask.make_response(redirect(next_url))
    else:
        r = flask.make_response("Logged out", 202)
    # also unset id/name in cookies
    _set_cookie(r, "user_id", "", max_age=0)
    _set_cookie(r, "user_name", "", max_age=0)

    return r


def _set_cookie(response: flask.Response, key: str, value: str, **kwargs):
    secure = current_app.config["SESSION_COOKIE_SECURE"]
    domain = current_app.config["SESSION_COOKIE_DOMAIN"]
    if not domain:
        domain = None
    response.set_cookie(key, value, domain=domain, secure=secure, path="/", **kwargs)


def disabled_auth_bp():
    """
    return blueprint if auth is disabled.

    All auth routes should return 501 (Not Implemented) we an error message.
    """
    disabled_bp = flask.Blueprint("auth", __name__, url_prefix="/api/auth")
    utils.auth.oauth_provider = None

    def not_implemented():
        return jsonify({"message": "authentication is not activated on this instance"}), 501

    @disabled_bp.route("/redirect")
    def redirect():
        return not_implemented()

    @disabled_bp.route("/login")
    def login():
        return not_implemented()

    @disabled_bp.route("/logout")
    def logout():
        return not_implemented()

    @disabled_bp.route("/post_logout_redirect")
    def post_logout_redirect():
        return not_implemented()

    return disabled_bp
