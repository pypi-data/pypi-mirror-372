import pytest
import os
from geovisio import config_app
from tests.conftest import create_test_app
import json


def test_index(client):
    response = client.get("/")
    assert b"Panoramax" in response.data


@pytest.mark.parametrize(
    ("readEnv", "cpu", "expected"),
    (
        ("10", 20, 10),
        ("10", 5, 5),
        ("-1", 10, 10),
    ),
)
def test_get_threads_limit(monkeypatch, readEnv, cpu, expected):
    monkeypatch.setattr(os, "cpu_count", lambda: cpu)
    res = config_app._get_threads_limit(readEnv)
    assert res == expected
    assert res >= 1


@pytest.mark.parametrize(
    ("forceAuth", "oauth", "expected"),
    (
        ("true", True, True),
        ("", True, False),
        ("false", True, False),
        (None, True, False),
        (None, False, False),
        ("true", False, True),
        ("false", False, False),
    ),
)
def test_config_app_forceAuthUpload(dburl, tmp_path, forceAuth, oauth, expected):
    config = {
        "TESTING": True,
        "DB_URL": dburl,
        "FS_URL": str(tmp_path),
        "FS_TMP_URL": None,
        "FS_PERMANENT_URL": None,
        "FS_DERIVATES_URL": None,
        "API_FORCE_AUTH_ON_UPLOAD": forceAuth,
    }

    if oauth:
        config["OAUTH_PROVIDER"] = "oidc"
        config["OAUTH_OIDC_URL"] = "https://bla.net"
        config["OAUTH_CLIENT_ID"] = "bla"
        config["OAUTH_CLIENT_SECRET"] = "bla"

    if expected == "fail":
        with pytest.raises(Exception):
            with create_test_app(config) as app:
                pass
    else:
        with create_test_app(config) as app:
            assert app.config["API_FORCE_AUTH_ON_UPLOAD"] == expected


@pytest.mark.parametrize(
    ("license_spdx_id", "license_url", "expected"),
    (
        ("etalab-2.0", "https://www.etalab.gouv.fr/licence-ouverte-open-licence/", True),
        (None, None, True),
        ("etalab-2.0", None, False),
        (None, "https://www.etalab.gouv.fr/licence-ouverte-open-licence/", False),
    ),
)
def test_config_app_license(dburl, tmp_path, license_spdx_id, license_url, expected):
    config = {
        "TESTING": True,
        "DB_URL": dburl,
        "FS_URL": str(tmp_path),
        "FS_TMP_URL": None,
        "FS_PERMANENT_URL": None,
        "FS_DERIVATES_URL": None,
        "API_PICTURES_LICENSE_SPDX_ID": license_spdx_id,
        "API_PICTURES_LICENSE_URL": license_url,
    }
    if not expected:
        with pytest.raises(Exception):
            with create_test_app(config) as app:
                pass
    else:
        with create_test_app(config) as app:
            if license_url is None:
                assert app.config["API_PICTURES_LICENSE_SPDX_ID"] == "proprietary"


@pytest.mark.parametrize(
    ("main", "viewer", "fails"),
    (
        (None, None, None),
        ("https://panoramax.fr", "https://panoramax.fr", None),
        ("", None, "API_MAIN_PAGE environment variable is not defined"),
        ("main.html", "", "API_VIEWER_PAGE environment variable is not defined"),
        ("prout", None, "API_MAIN_PAGE variable points to invalid template"),
        (None, "prout", "API_VIEWER_PAGE variable points to invalid template"),
    ),
)
def test_config_app_pages(dburl, tmp_path, main, viewer, fails):
    config = {
        "TESTING": True,
        "DB_URL": dburl,
        "FS_URL": str(tmp_path),
        "FS_TMP_URL": None,
        "FS_PERMANENT_URL": None,
        "FS_DERIVATES_URL": None,
    }

    if main is not None:
        config["API_MAIN_PAGE"] = main
    if viewer is not None:
        config["API_VIEWER_PAGE"] = viewer

    if fails is not None:
        with pytest.raises(Exception) as e:
            with create_test_app(config) as app:
                pass

        assert str(e.value).startswith(fails)

    else:
        with create_test_app(config) as app:
            assert app.config["API_MAIN_PAGE"] == main or "main.html"
            assert app.config["API_VIEWER_PAGE"] == viewer or "viewer.html"


@pytest.mark.parametrize(
    ("name", "desc", "logo", "color", "email", "covers", "fails"),
    (
        (None, None, None, None, None, None, False),
        ("Panoramax", "La super plateforme", "https://panoramax.fr/logo.svg", "#ff0000", "toto@plat.form", "Partout\nTrobien", False),
        ("Panoramax", "La super plateforme", None, None, None, None, False),
        (None, None, "not an url", None, None, None, True),
        (None, None, None, "blablabla", None, None, True),
        (None, None, None, None, "not an email", None, True),
    ),
)
def test_config_app_summary(dburl, tmp_path, name, desc, logo, color, email, covers, fails):
    summary = {}
    if name:
        summary["name"] = {"en": name}
    if desc:
        summary["description"] = {"en": desc}
    if logo:
        summary["logo"] = logo
    if color:
        summary["color"] = color
    if email:
        summary["email"] = email
    if covers:
        summary["geo_coverage"] = {"en": covers}

    config = {
        "TESTING": True,
        "DB_URL": dburl,
        "FS_URL": str(tmp_path),
        "FS_TMP_URL": None,
        "FS_PERMANENT_URL": None,
        "FS_DERIVATES_URL": None,
        "API_SUMMARY": json.dumps(summary),
    }

    if fails:
        with pytest.raises(Exception) as e:
            with create_test_app(config) as app:
                pass

        assert str(e.value) == "Parameter API_SUMMARY is not recognized"

    else:
        with create_test_app(config) as app:
            print(app.config["API_SUMMARY"])
            assert app.config["API_SUMMARY"].name == {"en": name or "Panoramax"}
            assert app.config["API_SUMMARY"].description == {"en": desc or "The open source photo mapping solution"}
            assert app.config["API_SUMMARY"].logo == logo or "https://gitlab.com/panoramax/gitlab-profile/-/raw/main/images/panoramax.svg"
            assert app.config["API_SUMMARY"].color == color or "#bf360c"
            assert app.config["API_SUMMARY"].email == email or "panoramax@panoramax.fr"
            assert app.config["API_SUMMARY"].geo_coverage == {
                "en": covers or "Worldwide\nThe picture can be sent from anywhere in the world."
            }
