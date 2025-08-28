import pytest
import requests
import stac_api_validator.validations
from tests import conftest
from tests.conftest import create_test_app, prepare_fs
import stac_api_validator


@pytest.fixture(scope="module")
def app(dburl, tmp_path_factory):
    fs = prepare_fs(tmp_path_factory.mktemp("api_conformance"))
    with create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fs.tmp,
            "FS_PERMANENT_URL": fs.permanent,
            "FS_DERIVATES_URL": fs.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
            "SERVER_NAME": "localhost:5055",
            "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
            "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
            "API_COMPRESSION": False,  # disable compression since stac api validator do not support it yet
        }
    ) as app:
        yield app


@pytest.fixture(scope="module")
def server(app_data):
    """start a real server, listening to a port
    Used to be able to receive queries from api-stac-validator
    """
    import threading
    from werkzeug.serving import make_server

    port = 5055
    s = make_server("localhost", port, app_data, threaded=True)
    t = threading.Thread(target=s.serve_forever)

    t.start()
    yield f"http://localhost:{port}"
    s.shutdown()


@pytest.fixture(scope="module")
def app_data(app):
    """
    Fixture returning an app's client with many sequences loaded.
    Data shouldn't be modified by tests as it will be shared by several tests
    """
    import pathlib

    datadir = pathlib.Path(conftest.FIXTURE_DIR)
    seqs = {
        "seq1": [
            datadir / "1.jpg",
            datadir / "2.jpg",
            datadir / "3.jpg",
            datadir / "4.jpg",
            datadir / "5.jpg",
        ],
        "seq2": [
            datadir / "e1.jpg",
            datadir / "e2.jpg",
        ],
    }
    with app.app_context():
        conftest.app_with_data(app=app, sequences=seqs)
    return app


def test_open_api(server, app_data):
    r = requests.get(f"{server}/api/docs/specs.json")
    assert r.status_code == 200
    schema = r.json()

    from openapi_spec_validator import validate

    validate(schema)


def test_stac_conformance(server, app_data):
    r = requests.get(f"{server}/api/collections")
    assert r.status_code == 200
    cols = r.json()["collections"]
    assert len(cols) > 0
    first_col = cols[0]["id"]
    geom = '{"type": "Polygon", "coordinates": [[[-4.04,51.30],[-4.04,42.05],[9.19,42.05],[9.19,51.30],[-4.04,51.30]]]}'

    warnings, errors = stac_api_validator.validations.validate_api(
        root_url=f"{server}/api",
        ccs_to_validate=["core", "collections", "browseable", "filter"],
        collection=first_col,
        geometry=geom,
        auth_bearer_token=None,
        auth_query_parameter=None,
        fields_nested_property=None,
        validate_pagination=True,
        query_config=stac_api_validator.validations.QueryConfig(
            query_comparison_field=None,
            query_eq_value=None,
            query_neq_value=None,
            query_lt_value=None,
            query_lte_value=None,
            query_gt_value=None,
            query_gte_value=None,
            query_substring_field=None,
            query_starts_with_value=None,
            query_ends_with_value=None,
            query_contains_value=None,
            query_in_field=None,
            query_in_values=None,
        ),
        transaction_collection=None,
        headers={},
    )

    assert not errors
    assert not warnings
