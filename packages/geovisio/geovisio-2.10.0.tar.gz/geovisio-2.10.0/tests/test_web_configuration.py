import psycopg
from tests import conftest
from geovisio.web.utils import get_api_version
from geovisio.utils import db
import re


def test_configuration(dburl, tmp_path):
    with (
        conftest.create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "OAUTH_PROVIDER": None,
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_SUMMARY": {"color": "#abcdef", "name": {"en": "My server"}},
            }
        ) as app,
        app.test_client() as client,
    ):
        with psycopg.connect(dburl, autocommit=True) as db:
            db.execute("UPDATE configurations SET collaborative_metadata = false")
        r = client.get("/api/configuration")
        assert r.status_code == 200
        assert r.json == {
            "color": "#abcdef",
            "description": {"label": "The open source photo mapping solution", "langs": {"en": "The open source photo mapping solution"}},
            "logo": "https://gitlab.com/panoramax/gitlab-profile/-/raw/main/images/panoramax.svg",
            "name": {"label": "My server", "langs": {"en": "My server"}},
            "auth": {"enabled": False},
            "license": {
                "id": "etalab-2.0",
                "url": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
            },
            "defaults": {
                "collaborative_metadata": False,
                "duplicate_distance": 1.0,
                "duplicate_rotation": 60,
                "split_distance": 100,
                "split_time": 300.0,
            },
            "email": "panoramax@panoramax.fr",
            "geo_coverage": {
                "label": "Worldwide\nThe picture can be sent from anywhere in the world.",
                "langs": {"en": "Worldwide\nThe picture can be sent from anywhere in the world."},
            },
            "version": get_api_version(),
            "pages": [],
        }
        assert re.match(r"^\d+\.\d+\.\d+(-\d+-[a-zA-Z0-9]+)?$", r.json["version"])


def test_configuration_i18n(dburl, tmp_path):
    with (
        conftest.create_test_app(
            {
                "TESTING": True,
                "DB_URL": dburl,
                "FS_URL": str(tmp_path),
                "OAUTH_PROVIDER": None,
                "FS_TMP_URL": None,
                "FS_PERMANENT_URL": None,
                "FS_DERIVATES_URL": None,
                "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
                "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
                "API_SUMMARY": {
                    "color": "#abcdef",
                    "email": "toto@tata.com",
                    "logo": "https://my-logo.org",
                    "name": {"en": "My server", "fr": "Mon petit serveur des familles"},
                    "geo_coverage": {"en": "Anywhere you like", "fr": "Partout où le vent vous portera"},
                },
            }
        ) as app,
        app.test_client() as client,
    ):
        # for this test, we also add pages
        with psycopg.connect(dburl, autocommit=True) as db:
            db.execute(
                "INSERT INTO pages(name, lang, content) VALUES ('legal-mentions', 'en', 'bla'), ('legal-mentions', 'fr', 'blablabla')"
            )
            db.execute("UPDATE configurations SET collaborative_metadata = true")

        # With user defined language
        r = client.get("/api/configuration", headers={"Accept-Language": "fr_FR,fr,en"})
        assert r.status_code == 200
        assert r.json == {
            "color": "#abcdef",
            "description": {"label": "The open source photo mapping solution", "langs": {"en": "The open source photo mapping solution"}},
            "geo_coverage": {
                "label": "Partout où le vent vous portera",
                "langs": {"en": "Anywhere you like", "fr": "Partout où le vent vous portera"},
            },
            "logo": "https://my-logo.org/",
            "name": {"label": "Mon petit serveur des familles", "langs": {"en": "My server", "fr": "Mon petit serveur des familles"}},
            "auth": {"enabled": False},
            "license": {
                "id": "etalab-2.0",
                "url": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
            },
            "email": "toto@tata.com",
            "version": get_api_version(),
            "pages": ["legal-mentions"],
            "defaults": {
                "collaborative_metadata": True,
                "duplicate_distance": 1.0,
                "duplicate_rotation": 60,
                "split_distance": 100,
                "split_time": 300.0,
            },
        }
