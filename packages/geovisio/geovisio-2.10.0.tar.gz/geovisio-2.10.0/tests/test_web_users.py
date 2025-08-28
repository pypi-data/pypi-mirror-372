from flask import current_app
import pytest

from geovisio.utils import db
from . import conftest


def test_unlogged_user_retrieval_without_oauth(client):
    """it should be impossible to access current user info if the instance has no oauth"""
    response = client.get("/api/users/me")
    assert response.status_code == 403


@pytest.fixture
def client_app_with_lots_of_users(dburl, client):
    import psycopg

    users = [
        "bobette",
        "bobito",
        "onésime",
        "elie",
        "elise",
        "eloïse",
        "armand",
        "paul",
        "zeline",
        "Loïs",
        "Buenaventura",
        "Mohamed",
        "He-Yin",
    ]
    with psycopg.connect(dburl) as conn, conn.cursor() as cursor:
        for u in users:
            accountID = cursor.execute("SELECT id from accounts WHERE name = %s", [u]).fetchone()
            if accountID:
                continue
            cursor.execute("INSERT INTO accounts (name) VALUES  (%s)", [u])
            conn.commit()

        yield client
        for u in users:
            cursor.execute("DELETE FROM accounts where name = %s", [u])
            conn.commit()


@pytest.mark.parametrize(
    ("query"),
    (
        [
            ("b"),
            ("ob"),
            ("bob"),
        ]
    ),
)
def test_user_search_bob(client, bobAccountID, query):
    r = client.get(f"/api/users/search?q={query}")

    assert r.status_code == 200
    assert r.json == {
        "features": [
            {
                "id": str(bobAccountID),
                "label": "bob",
                "links": [
                    {
                        "href": f"http://localhost:5000/api/users/{bobAccountID}",
                        "rel": "user-info",
                        "type": "application/json",
                    },
                    {
                        "href": f"http://localhost:5000/api/users/{bobAccountID}/collection",
                        "rel": "collection",
                        "type": "application/json",
                    },
                ],
            }
        ],
    }


def test_user_search_limit(client_app_with_lots_of_users, bobAccountID, dburl):
    r = client_app_with_lots_of_users.get("/api/users/search?q=el")

    assert len(set((f["label"] for f in r.json["features"]))) > 2
    r = client_app_with_lots_of_users.get("/api/users/search?q=el&limit=2")

    assert len([f["label"] for f in r.json["features"]]) == 2


def test_unknonw_user_search(client_app_with_lots_of_users, bobAccountID):
    r = client_app_with_lots_of_users.get("/api/users/search?q=some_unknown_user_name")
    assert r.status_code == 200
    assert r.json == {"features": []}


@pytest.mark.parametrize(
    ("query"),
    (
        [
            (""),
            ("?q="),
        ]
    ),
)
def test_bad_user_search(client_app_with_lots_of_users, query):
    r = client_app_with_lots_of_users.get(f"/api/users/search{query}")
    assert r.json == {"message": "No search parameter given, you should provide `q=<pattern>` as query parameter", "status_code": 400}
    assert r.status_code == 400


def test_user_info(client_app_with_lots_of_users, bobAccountID, cleanup_config):
    r = client_app_with_lots_of_users.get(f"/api/users/{bobAccountID}")
    assert r.status_code == 200
    assert r.json == {
        "id": str(bobAccountID),
        "name": "bob",
        "collaborative_metadata": None,
        "links": [
            {"href": f"http://localhost:5000/api/users/{bobAccountID}/catalog/", "rel": "catalog", "type": "application/json"},
            {"href": f"http://localhost:5000/api/users/{bobAccountID}/collection", "rel": "collection", "type": "application/json"},
            {
                "href": f"http://localhost:5000/api/users/{bobAccountID}" + "/map/{z}/{x}/{y}.mvt",
                "rel": "user-xyz",
                "title": "Pictures and sequences vector tiles for a given user",
                "type": "application/vnd.mapbox-vector-tile",
            },
        ],
    }


def test_unknown_user_info(client_app_with_lots_of_users):
    r = client_app_with_lots_of_users.get("/api/users/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404
    assert r.json == {"message": "Impossible to find user", "status_code": 404}


def test_user_list(client_app_with_lots_of_users, bobAccountID, bobAccountToken, defaultAccountToken, defaultAccountID):
    # add some pictures for bob and the default account since the stac link are only for users with pictures
    import pathlib

    datadir = pathlib.Path(conftest.FIXTURE_DIR)
    conftest.uploadSequenceFromPics(
        test_client=client_app_with_lots_of_users,
        title="bob's sequence",
        wait=True,
        jwtToken=bobAccountToken(),
        pics=[
            datadir / "1.jpg",
            datadir / "2.jpg",
            datadir / "3.jpg",
        ],
    )
    conftest.uploadSequenceFromPics(
        test_client=client_app_with_lots_of_users,
        title="default account sequence",
        wait=True,
        jwtToken=defaultAccountToken(),
        pics=[
            datadir / "4.jpg",
            datadir / "5.jpg",
        ],
    )

    r = client_app_with_lots_of_users.get("/api/users")
    assert r.status_code == 200

    users = r.json["users"]
    users_by_name = {
        r["name"]: r
        for r in users
        if r["name"]
        not in ("camille", "elysee", "elie_reclus")  # those name are added by another test, we don't want them to interfere with this one
    }
    assert set(users_by_name.keys()) == {
        "Default account",
        "bob",
        "bobette",
        "bobito",
        "onésime",
        "elie",
        "elise",
        "eloïse",
        "armand",
        "paul",
        "zeline",
        "Loïs",
        "Buenaventura",
        "Mohamed",
        "He-Yin",
    }

    # we should also have stac link for the default account and bob since they have some pictures (and only for them)

    assert r.json["links"] == [
        {"href": "http://localhost:5000/api/users/search", "rel": "user-search", "title": "Search users", "type": "application/json"},
        {
            "href": "http://localhost:5000/api/",
            "rel": "root",
            "title": "Instance catalog",
            "type": "application/json",
        },
        {
            "href": f"http://localhost:5000/api/users/{str(defaultAccountID)}/collection",
            "rel": "child",
            "title": 'User "Default account" sequences',
        },
        {
            "href": f"http://localhost:5000/api/users/{str(bobAccountID)}/collection",
            "rel": "child",
            "title": 'User "bob" sequences',
        },
    ]

    # test one users
    assert users_by_name["bob"] == {
        "id": str(bobAccountID),
        "name": "bob",
        "links": [
            {
                "href": f"http://localhost:5000/api/users/{str(bobAccountID)}",
                "rel": "user-info",
                "type": "application/json",
            },
            {
                "href": f"http://localhost:5000/api/users/{str(bobAccountID)}/collection",
                "rel": "collection",
                "type": "application/json",
            },
        ],
    }


def test_get_unknown_user_config(client_app_with_lots_of_users):
    """Since the user is retreived from the token, we cannot edit the configuration of a wrong user"""

    r = client_app_with_lots_of_users.get("/api/users/me", headers={"Authorization": f"Bearer pouet"})
    assert r.status_code == 401
    assert r.json == {
        "details": {
            "error": "Impossible to decode token",
        },
        "message": "Token not valid",
        "status_code": 401,
    }


@pytest.fixture()
def cleanup_config(dburl, bobAccountID):
    """Reset the accounts's configuration"""
    import psycopg

    with psycopg.connect(dburl) as conn:
        conn.execute("UPDATE accounts SET collaborative_metadata = null, tos_accepted_at = null where id = %s", [bobAccountID])
        conn.execute("UPDATE configurations SET collaborative_metadata = null")

    yield

    with psycopg.connect(dburl) as conn:
        conn.execute("UPDATE accounts SET collaborative_metadata = null where id = %s", [bobAccountID])


def test_patch_user_config(client_app_with_lots_of_users, bobAccountToken, cleanup_config):
    """Test the user configuration endpoint"""
    # we can patch it
    r = client_app_with_lots_of_users.patch(
        "/api/users/me", headers={"Authorization": f"Bearer {bobAccountToken()}"}, json={"collaborative_metadata": True}
    )
    assert r.status_code == 200, r.text
    assert r.json["collaborative_metadata"] == True
    # and it should be persisted
    r = client_app_with_lots_of_users.get("/api/users/me", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 200
    assert r.json["collaborative_metadata"] == True

    r = client_app_with_lots_of_users.patch(
        "/api/users/me", headers={"Authorization": f"Bearer {bobAccountToken()}"}, json={"collaborative_metadata": False}
    )
    assert r.status_code == 200
    assert r.json["collaborative_metadata"] == False


def test_accept_tos(fsesUrl, dburl, bobAccountToken, cleanup_config, bobAccountID):

    with (
        conftest.create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": None,
                "FS_TMP_URL": fsesUrl.tmp,
                "FS_PERMANENT_URL": fsesUrl.permanent,
                "FS_DERIVATES_URL": fsesUrl.derivates,
                "SERVER_NAME": "localhost:5000",
                "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
                "SECRET_KEY": "a very secret key",
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_ENFORCE_TOS_ACCEPTANCE": "true",
            }
        ) as app,
        app.test_client() as client,
    ):
        # we cannot see if another user has accepted the tos
        r = client.get(f"/api/users/{bobAccountID}")
        assert r.status_code == 200
        assert "tos_accepted" not in r.json

        # but we can see if the logged used has accepted the tos
        r = client.get("/api/users/me", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert r.json["tos_accepted"] is False  # and in this case, he did not accept the tos yet

        # we can also see it when querying by id instead of `/me`
        r = client.get(f"/api/users/{bobAccountID}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert r.json["tos_accepted"] is False

        # and if the user has not accepted the tos, collections/upload_sets cannot be created
        r = client.post("/api/collections", headers={"Authorization": f"Bearer {bobAccountToken()}"}, json={"title": "some title"})
        assert r.status_code == 401
        assert r.json == {
            "message": "You need to accept the terms of service before uploading any pictures. You can do so by validating them here: http://localhost:5000/tos-validation",
            "details": {
                "validation_page": "http://localhost:5000/tos-validation",
            },
            "status_code": 401,
        }
        r = client.post("/api/upload_sets", headers={"Authorization": f"Bearer {bobAccountToken()}"}, json={"title": "some title"})
        assert r.status_code == 401
        assert r.json == {
            "message": "You need to accept the terms of service before uploading any pictures. You can do so by validating them here: http://localhost:5000/tos-validation",
            "details": {
                "validation_page": "http://localhost:5000/tos-validation",
            },
            "status_code": 401,
        }

        # we make bob accept the tos
        r = client.post("/api/users/me/accept_tos", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200, r.text
        assert r.json == {
            "collaborative_metadata": None,
            "tos_accepted": True,
            "id": str(bobAccountID),
            "name": "bob",
            "links": r.json["links"],  # we don't care about links here, we don't compare them
            "permissions": {
                "role": "user",
                "can_check_reports": False,
                "can_edit_excluded_areas": False,
                "can_edit_pages": False,
            },
        }
        # in the cookie, we get the new accepted status
        cookies = r.headers.getlist("Set-Cookie")
        assert cookies
        session_cookie = next((c for c in cookies if c.startswith("session=")))
        assert session_cookie
        session_cookie = session_cookie.split("=")[1].split(";")[0]
        session = conftest.decode_session_cookie(session_cookie)
        assert session["account"]["tos_accepted"] is True

        # and in database, we also store the acceptance date
        tos_accepted_at = db.fetchone(current_app, "SELECT tos_accepted_at FROM accounts WHERE id = %s", [bobAccountID])
        assert tos_accepted_at is not None

        # and it should be persisted
        r = client.get("/api/users/me", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200
        assert r.json["tos_accepted"] is True

        # and even if we accept it again, it does not change the date
        r = client.post("/api/users/me/accept_tos", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert r.status_code == 200, r.text
        assert r.json == {
            "collaborative_metadata": None,
            "tos_accepted": True,
            "id": str(bobAccountID),
            "name": "bob",
            "links": r.json["links"],
            "permissions": {
                "role": "user",
                "can_check_reports": False,
                "can_edit_excluded_areas": False,
                "can_edit_pages": False,
            },
        }
        tos_accepted_at_2 = db.fetchone(current_app, "SELECT tos_accepted_at FROM accounts WHERE id = %s", [bobAccountID])
        assert tos_accepted_at == tos_accepted_at_2


def test_accept_tos_not_mandatory(client_app_with_lots_of_users, bobAccountToken, cleanup_config, bobAccountID):
    """If the settings API_ENFORCE_TOS_ACCEPTANCE has not been set, it's not mandatory to accept the tos to upload stuff"""
    # bob has not accepted the tos
    r = client_app_with_lots_of_users.get(f"/api/users/{bobAccountID}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert r.status_code == 200
    assert "tos_accepted" not in r.json

    conftest.createSequence(client_app_with_lots_of_users, "some title", jwtToken=bobAccountToken())
    conftest.create_upload_set(client_app_with_lots_of_users, jwtToken=bobAccountToken(), title="some title")
