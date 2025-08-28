from urllib.parse import urlencode
import psycopg
import requests
from uuid import UUID
from dateutil import parser
import pytest

import geovisio.utils.tokens
from .conftest import redirect_history, get_keycloak_authenticate_form_url, create_test_app
from geovisio import tokens


def test_list_user_token(server, keycloak, auth_app, dburl):
    """An authenticated user can list his tokens"""
    with requests.session() as s:
        # to simplify the test, we mock the acceptance of the ToS for elysee
        mock_tos_acceptance(dburl)
        # A user attempt to access his tokens list, but since he is not logged yet, he is redirected to the oauth provider (keycloak here)
        tokens_before_oauth = s.get(f"{server}/api/users/me/tokens", allow_redirects=True)
        tokens_before_oauth.raise_for_status()
        assert tokens_before_oauth.status_code == 200

        assert redirect_history(tokens_before_oauth) == [
            "/api/users/me/tokens",
            "/api/auth/login",
            "/realms/geovisio/protocol/openid-connect/auth",
        ]
        # This should ask us for login, and the login has been set as mandatory for upload in the app config
        # Then we authenticate on the keycloak to an already created user (defined in 'keycloak-realm.json')
        url = get_keycloak_authenticate_form_url(tokens_before_oauth)
        tokens = s.post(
            url,
            data={"username": "elysee", "password": "my password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=True,
        )
        tokens.raise_for_status()
        assert redirect_history(tokens) == [
            "/realms/geovisio/login-actions/authenticate",
            "/api/auth/redirect",
            "/api/users/me/tokens",
        ]

        t = tokens.json()
        assert len(t) >= 1
        # id must be a valid uuid
        UUID(t[0]["id"])
        parser.parse(t[0]["generated_at"])
        assert t[0]["description"] == "default token"

        # we should also be able to generate a new token
        new_token = s.post(f"{server}/api/users/me/tokens", json={"description": "new token"})
        assert new_token.status_code == 200
        # id must be a valid uuid
        UUID(new_token.json()["id"])
        parser.parse(new_token.json()["generated_at"])
        assert new_token.json()["description"] == "new token"

        # the token should be in the list of the user's token
        list_tokens_by_cookie = s.get(f"{server}/api/users/me/tokens")
        assert list_tokens_by_cookie.status_code == 200
        assert new_token.json()["id"] in {t["id"] for t in list_tokens_by_cookie.json()}

        # and it should be usable (here we're not using the session, but using the new tokens via headers)
        list_tokens_by_tokens = requests.get(
            f"{server}/api/users/me/tokens", headers={"Authorization": f"Bearer {new_token.json()['jwt_token']}"}
        )
        assert list_tokens_by_tokens.status_code == 200
        assert list_tokens_by_tokens.json() == list_tokens_by_cookie.json()


def test_get_jwt_token(server, keycloak, auth_client, dburl):
    """An authenticated user can get the JWT token associated to a token"""
    # to simplify the test, we mock the acceptance of the ToS for elysee
    with requests.session() as s:
        _login(session=s, server=server, dburl=dburl)

        list_tokens = s.get(f"{server}/api/users/me/tokens/")
        assert list_tokens.status_code == 200
        first_token_id = list_tokens.json()[0]["id"]

        jwt_token = s.get(f"{server}/api/users/me/tokens/{first_token_id}")
        assert jwt_token.status_code == 200

        t = jwt_token.json()
        # id must be a valid uuid
        UUID(t["id"])
        parser.parse(t["generated_at"])
        assert t["description"] == "default token"
        jwt_token = t["jwt_token"]

        associated_account = geovisio.utils.tokens.get_account_from_jwt_token(jwt_token)
        assert associated_account.name == "elysee"

    # outside of the session, we can query the API with this token, and be logged as Elysee Reclus
    user_info = auth_client.get("/api/users/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert user_info.status_code == 200
    assert len(user_info.history) == 0  # no oauth dance should have been needed
    assert "id" in user_info.json
    assert user_info.json["name"] == "elysee"
    assert user_info.json["links"] == [
        {
            "href": f"http://localhost/api/users/{user_info.json['id']}/catalog/",
            "rel": "catalog",
            "type": "application/json",
        },
        {
            "href": f"http://localhost/api/users/{user_info.json['id']}/collection",
            "rel": "collection",
            "type": "application/json",
        },
        {
            "href": f"http://localhost/api/users/{user_info.json['id']}" + "/map/{z}/{x}/{y}.mvt",
            "rel": "user-xyz",
            "title": "Pictures and sequences vector tiles for a given user",
            "type": "application/vnd.mapbox-vector-tile",
        },
    ]


def test_get_unknown_token(server, keycloak, auth_app, dburl):
    """Accessing an unknown token should return in a 404"""
    # to simplify the test, we mock the acceptance of the ToS for elysee
    with requests.session() as s:
        _login(session=s, server=server, dburl=dburl)

        unknown_token = s.get(f"{server}/api/users/me/tokens/00000000-0000-0000-0000-000000000000")
        assert unknown_token.status_code == 404
        assert unknown_token.json() == {
            "message": "Impossible to find token",
            "status_code": 404,
        }


def _login(session: requests.Session, server: str, dburl):
    """Test helper, login as Elysee Reclus in app"""

    # to simplify the test, we mock the acceptance of the ToS for elysee
    mock_tos_acceptance(dburl)
    # A user attempt to access his tokens list, but since he is not logged yet, he is redirected to the oauth provider (keycloak here)
    login_before_oauth = session.get(f"{server}/api/auth/login", allow_redirects=True)
    login_before_oauth.raise_for_status()
    assert login_before_oauth.status_code == 200

    # This should ask us for login, and the login has been set as mandatory for upload in the app config
    # Then we authenticate on the keycloak to an already created user (defined in 'keycloak-realm.json')
    url = get_keycloak_authenticate_form_url(login_before_oauth)
    tokens = session.post(
        url,
        data={"username": "elysee", "password": "my password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        allow_redirects=True,
    )
    tokens.raise_for_status()


def test_invalid_bearer_token(client):
    """
    An invalid bearer token should result in a unauthorized error
    Note: this test does not need a keycloak since no oauth dance should be run
    """
    user_info = client.get("/api/users/me", headers={"Authorization": "Bearer Pouet"})
    assert user_info.status_code == 401
    assert len(user_info.history) == 0  # no oauth dance should have been needed
    assert user_info.json == {
        "details": {"error": "Impossible to decode token"},
        "message": "Token not valid",
        "status_code": 401,
    }


def test_delete_unknown_token(server, keycloak, auth_app, dburl):
    """DELETING an unknown token should return in a 404"""
    with requests.session() as s:
        _login(session=s, server=server, dburl=dburl)

        unknown_token = s.delete(f"{server}/api/users/me/tokens/00000000-0000-0000-0000-000000000000")
        assert unknown_token.status_code == 404
        assert unknown_token.json() == {
            "message": "Impossible to find token",
            "status_code": 404,
        }


def test_invalid_jwt_signature(client):
    """
    An bearer token not correctly signed (not generated with the same secret) should result in a unauthorized error
    Note: this test does not need a keycloak since no oauth dance should be run
    """
    # generate a jwt token with another secret
    from authlib.jose import jwt

    secret = "a very very different secret"
    s = jwt.encode({"alg": "HS256"}, {"some": "pouet", "sub": "plop"}, secret)

    print(s)
    jwt_token = str(s, "utf-8")

    user_info = client.get("/api/users/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert user_info.status_code == 401
    assert len(user_info.history) == 0  # no oauth dance should have been needed
    assert user_info.json == {
        "details": {"error": "JWT token signature does not match"},
        "message": "Token not valid",
        "status_code": 401,
    }


def test_generate_token_no_user(client):
    """It should not be possible to generate a new token without being logged in"""
    user_info = client.post("/api/users/me/tokens")
    assert user_info.status_code == 403


def test_invalid_basic_auth(client):
    """
    Only bearer token are supported, other `Authorization` mode should result to an error
    Note: this test does not need a keycloak since no oauth dance should be run
    """
    user_info = client.get("/api/users/me", headers={"Authorization": "Basic Pouet"})
    assert user_info.status_code == 401
    assert len(user_info.history) == 0  # no oauth dance should have been needed
    assert user_info.json == {
        "details": {"error": "Only Bearer token are supported"},
        "message": "Token not valid",
        "status_code": 401,
    }


@pytest.fixture
def no_secret_key_app(dburl, fsesUrl):
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "SERVER_NAME": "localhost",
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
        }
    ) as app:
        yield app


@pytest.fixture(autouse=True)
def cleanup_db(dburl):
    with psycopg.connect(dburl) as conn:
        conn.execute("UPDATE accounts SET tos_accepted_at = NULL")


def mock_tos_acceptance(dburl):
    with psycopg.connect(dburl) as conn:
        conn.execute("UPDATE accounts SET tos_accepted_at = NOW() WHERE name = 'elysee'")


def test_invalid_token_auth_no_secret_key_defined(no_secret_key_app):
    """
    If SECRET_KEY has not been defined (defined as `FLASK_SECRET_KEY` environment variable), token based oauth should result in an internal error
    """
    with no_secret_key_app.test_client() as client:
        user_info = client.get("/api/users/me", headers={"Authorization": "Bearer Pouet"})
        assert user_info.status_code == 500
        assert len(user_info.history) == 0  # no oauth dance should have been needed
        assert user_info.json == {
            "message": "No SECRET_KEY has been defined for the instance (defined by FLASK_SECRET_KEY environment variable), authentication is not possible. Please contact your instance administrator if this is needed.",
            "status_code": 500,
        }


def test_default_account_jwt_token(client):
    """Test the administrator command to get a JWT token for the default account"""
    jwt_token = geovisio.utils.tokens.get_default_account_jwt_token()

    associated_account = geovisio.utils.tokens.get_account_from_jwt_token(jwt_token)
    assert associated_account.name == "Default account"


def test_default_account_jwt_token_no_secret_key(no_secret_key_app):
    """Test that it's impossible to get a default account JWT token if no SECRET KEY has been defined"""
    with pytest.raises(tokens.NoSecretKeyException):
        geovisio.utils.tokens.get_default_account_jwt_token()


def test_generate_bearer_token_flow(server, keycloak, auth_app):
    """
    Integration test on the whole token generation/claim flow
    """

    token_generation = requests.post(f"{server}/api/auth/tokens/generate?description=some_token")

    token_generation.raise_for_status()
    assert len(token_generation.history) == 0  # no oauth dance should have been needed

    token_generation = token_generation.json()
    token_id = token_generation["id"]
    jwt_token = token_generation["jwt_token"]
    assert token_generation["description"] == "some_token"
    claim_url = next(l["href"] for l in token_generation["links"] if l["rel"] == "claim")

    # using this token directly should result in a 403 forbidden
    user_info = requests.get(f"{server}/api/users/me", headers={"Authorization": f"Bearer {jwt_token}"})
    assert user_info.status_code == 403
    assert user_info.json() == {
        "details": {
            "error": "Token not yet claimed, this token cannot be used yet. Either claim this token or generate a new one",
        },
        "message": "Token not valid",
        "status_code": 403,
    }

    # but after claiming it, we should be able to use it
    # this will trigger an oauth dance, so we use a session to share cookies between calls
    with requests.session() as s:
        claim = s.get(claim_url, allow_redirects=True)
        # this should trigger an oauth dance
        claim.raise_for_status()
        assert claim.status_code == 200

        assert redirect_history(claim)[-1] == "/realms/geovisio/protocol/openid-connect/auth"

        # Then we authenticate on the keycloak as 'elysee'
        url = get_keycloak_authenticate_form_url(claim)
        r = s.post(
            url,
            data={"username": "elysee", "password": "my password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=True,
        )

        # at the end this should redirect to the website to accept the ToS
        assert r.status_code == 404  # 404 since the website does not exist in this test

        # we should be redirected to the ToS validation page, and with a next_url query parameter with the claim url
        assert redirect_history(r) == [
            "/realms/geovisio/login-actions/authenticate",
            "/api/auth/redirect",
            "/tos-validation",
        ]
        args = urlencode({"next_url": claim_url})
        assert r.url == f"{server}/tos-validation?{args}"

        # we accept the ToS
        r = s.post(f"{server}/api/users/me/accept_tos", allow_redirects=True)
        r.raise_for_status()
        # and we claim the token (the website should redirect to the claim url and do this automatically)
        r = s.get(claim_url, allow_redirects=True)
        assert r.status_code == 404  # At the end we are redirected to a nice page on the website, but it does not exist in this test
        assert redirect_history(r) == [f"/api/auth/tokens/{token_id}/claim", "/token-accepted"]

        user_info = requests.get(
            f"{server}/api/users/me",
            headers={"Authorization": f"Bearer {jwt_token}"},  # queries without the session, so no cookies, only bearer token
        )
        user_info.raise_for_status()
        # successfully logged in as 'elysee'
        assert user_info.json()["name"] == "elysee"

        # the token should be in the list of the user's token
        tokens = s.get(f"{server}/api/users/me/tokens")
        assert tokens.status_code == 200
        tokens_id = [t["id"] for t in tokens.json()]
        assert token_id in tokens_id

        # delete the token
        token_deletion = s.delete(f"{server}/api/users/me/tokens/{token_id}")
        assert token_deletion.status_code == 200

        # the token should not be in the user's token anymore
        tokens = s.get(f"{server}/api/users/me/tokens")
        assert tokens.status_code == 200
        tokens_id = [t["id"] for t in tokens.json()]
        assert token_id not in tokens_id

        # If the token is revoked, it should not be usable anymore
        user_info = requests.get(f"{server}/api/users/me", headers={"Authorization": f"Bearer {jwt_token}"})
        assert user_info.status_code == 403  # forbidden


def test_generate_bearer_token_flow_double_claim(server, keycloak, auth_app):
    """
    Claiming a token with a different user should result of a error
    """
    token_generation = requests.post(f"{server}/api/auth/tokens/generate?description=some_token")

    token_generation.raise_for_status()

    token_generation = token_generation.json()
    token_id = token_generation["id"]
    claim_url = next(l["href"] for l in token_generation["links"] if l["rel"] == "claim")

    # but after claiming it, we should be able to use it
    # this will trigger an oauth dance, so we use a session to share cookies between calls
    with requests.session() as s:
        claim = s.get(claim_url, allow_redirects=True)
        # this should trigger an oauth dance
        claim.raise_for_status()
        assert claim.status_code == 200

        assert redirect_history(claim)[-1] == "/realms/geovisio/protocol/openid-connect/auth"

        # Then we authenticate on the keycloak as 'elysee'
        url = get_keycloak_authenticate_form_url(claim)
        r = s.post(
            url,
            data={"username": "elysee", "password": "my password"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=True,
        )

        assert r.status_code == 404  # 404 since the website does not exist in this test and the

        # we should be redirected to the claim url, and at the end to the website to accept the ToS
        assert redirect_history(r) == [
            "/realms/geovisio/login-actions/authenticate",
            "/api/auth/redirect",
            "/tos-validation",
        ]
        args = urlencode({"next_url": claim_url})
        assert r.url == f"{server}/tos-validation?{args}"

        # we accept the ToS
        r = s.post(f"{server}/api/users/me/accept_tos", allow_redirects=True)
        r.raise_for_status()
        # and we claim the token (the website should redirect to the claim url and do this automatically)
        r = s.get(claim_url, allow_redirects=True)
        assert r.status_code == 404  # At the end we are redirected to a nice page on the website, but it does not exist in this test
        assert redirect_history(r) == [f"/api/auth/tokens/{token_id}/claim", "/token-accepted"]

    with requests.session() as another_session:
        # claiming again the token with the same user, should be ok, and should result in a 200 after an oauth dance
        claim = another_session.get(claim_url, allow_redirects=True)
        assert redirect_history(claim) == [
            f"/api/auth/tokens/{token_id}/claim",
            "/api/auth/login",
            "/realms/geovisio/protocol/openid-connect/auth",
        ]
        assert claim.status_code == 200

    # but if the token is claimed by another user, this should trigger a 403 forbidden
    with requests.session() as new_user_session:
        claim = new_user_session.get(claim_url, allow_redirects=True)
        # this should trigger an oauth dance
        claim.raise_for_status()
        assert claim.status_code == 200

        assert redirect_history(claim)[-1] == "/realms/geovisio/protocol/openid-connect/auth"

        # Then we authenticate on the keycloak as 'elie_reclus', elysee's brother
        url = get_keycloak_authenticate_form_url(claim)
        r = new_user_session.post(
            url,
            data={"username": "elie_reclus", "password": "my password"},  # login as elie reclus, the brother of elysee reclus
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            allow_redirects=True,
        )
        assert redirect_history(r) == [
            "/realms/geovisio/login-actions/authenticate",  # <- keycloak authentication is ok
            "/api/auth/redirect",
            "/tos-validation",
        ]
        args = urlencode({"next_url": claim_url})
        assert r.url == f"{server}/tos-validation?{args}"

        # we accept the ToS
        r = new_user_session.post(f"{server}/api/users/me/accept_tos", allow_redirects=True)
        r.raise_for_status()
        # and we claim the token as elie, we should get an error
        r = new_user_session.get(claim_url, allow_redirects=False)

        assert r.status_code == 403
        assert r.json() == {"message": "Token already claimed by another account", "status_code": 403}
