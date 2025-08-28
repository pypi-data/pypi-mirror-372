import pytest
import psycopg
from flask import current_app


def create_page(client, token, lang, content):
    response = client.post(
        f"/api/pages/terms-of-service/{lang}",
        data=content,
        headers={
            "Authorization": f"Bearer {token()}",
            "Content-Type": "text/html",
        },
    )
    return response


def test_get_page_languages_invalid(client):
    response = client.get("/api/pages/not-a-valid-page")
    assert response.status_code == 400
    assert response.json["message"] == "Page name is not recognized"


def test_get_page_languages_empty(client):
    response = client.get("/api/pages/end-user-license-agreement")
    assert response.status_code == 200
    assert response.json["name"] == "end-user-license-agreement"
    assert response.json["languages"] == []


def test_get_page_languages_indb(client, dburl):
    with psycopg.connect(dburl, autocommit=True) as db:
        db.execute(
            "INSERT INTO pages(name, lang, content) VALUES ('end-user-license-agreement', 'en', 'bla'), ('end-user-license-agreement', 'fr', 'blablabla')"
        )

    response = client.get("/api/pages/end-user-license-agreement")
    assert response.status_code == 200
    assert response.json["name"] == "end-user-license-agreement"
    assert response.json["languages"] == [
        {
            "language": "en",
            "links": [{"rel": "self", "type": "application/json", "href": "http://localhost:5000/api/pages/end-user-license-agreement/en"}],
        },
        {
            "language": "fr",
            "links": [{"rel": "self", "type": "application/json", "href": "http://localhost:5000/api/pages/end-user-license-agreement/fr"}],
        },
    ]


def test_get_page_content_invalid(client):
    response = client.get("/api/pages/not-a-valid-page/fr")
    assert response.status_code == 400
    assert response.json["message"] == "Page name is not recognized"


def test_get_page_content_unavailable_lang(client):
    response = client.get("/api/pages/terms-of-service/fr")
    assert response.status_code == 404
    assert response.json["message"] == "Page not available in language fr"


def test_get_page_content_available(client, dburl):
    with psycopg.connect(dburl, autocommit=True) as db:
        db.execute(
            "INSERT INTO pages(name, lang, content) VALUES ('end-user-license-agreement', 'en', '<p>hello</p>'), ('end-user-license-agreement', 'fr', '<p>coucou</p>')"
        )

    response = client.get("/api/pages/end-user-license-agreement/en")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/html"
    assert response.text == "<p>hello</p>"

    response = client.get("/api/pages/end-user-license-agreement/fr")
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "text/html"
    assert response.text == "<p>coucou</p>"


def test_post_page_unauthenticated(client, bobAccountToken):
    # Not logged at all
    response = client.post("/api/pages/terms-of-service/fr", data="<p>coucou</p>")
    assert response.status_code == 401

    # Logged as non-admin
    response = create_page(client, bobAccountToken, "fr", "<p>coucou</p>")
    assert response.status_code == 403
    assert response.json["message"] == "You must be logged-in as admin to edit pages"


def test_post_page_invalid_content(client, defaultAccountToken):
    response = client.post(
        "/api/pages/terms-of-service/fr",
        json={"not": "html"},
        headers={
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )
    assert response.status_code == 400
    assert response.json["message"] == "Page content must be HTML (with " "Content-Type: text/html" " header set)"


def test_post_page_valid(client, defaultAccountToken):
    response = create_page(client, defaultAccountToken, "fr", "<p>coucou</p>")
    assert response.status_code == 200

    # Check if content has been stored
    response = client.get("/api/pages/terms-of-service/fr")
    assert response.status_code == 200
    assert response.text == "<p>coucou</p>"

    # Update content
    response = create_page(client, defaultAccountToken, "fr", "<p>hey coucou</p>")
    assert response.status_code == 200

    # Check if content has been stored
    response = client.get("/api/pages/terms-of-service/fr")
    assert response.status_code == 200
    assert response.text == "<p>hey coucou</p>"


def test_delete_page_unauthenticated(client, defaultAccountToken, bobAccountToken):
    response = create_page(client, defaultAccountToken, "fr", "<p>coucou</p>")

    # Not logged at all
    response = client.delete("/api/pages/terms-of-service/fr")
    assert response.status_code == 401

    # Logged as non-admin
    response = client.delete(
        "/api/pages/terms-of-service/fr",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 403
    assert response.json["message"] == "You must be logged-in as admin to edit pages"


def test_delete_page_missing(client, defaultAccountToken):
    response = client.delete(
        "/api/pages/terms-of-service/fr",
        headers={
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )
    assert response.status_code == 404


def test_delete_page_valid(client, defaultAccountToken):
    response = create_page(client, defaultAccountToken, "fr", "<p>coucou</p>")
    assert response.status_code == 200

    # Check if content has been stored
    response = client.delete(
        "/api/pages/terms-of-service/fr",
        headers={
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )
    assert response.status_code == 200
