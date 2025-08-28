import pytest
import os
import time
from testcontainers import compose
from tests.conftest import create_test_app
from urllib.parse import urlparse
import re


@pytest.fixture
def auth_app(dburl, keycloak, fsesUrl):
    """Configure an app with keycloak auth"""

    with create_test_app(
        {
            "TESTING": True,
            "DEBUG": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fsesUrl.tmp,
            "FS_PERMANENT_URL": fsesUrl.permanent,
            "FS_DERIVATES_URL": fsesUrl.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "OAUTH_PROVIDER": "oidc",
            "SECRET_KEY": "plop",
            "OAUTH_OIDC_URL": f"{keycloak}/realms/geovisio",
            "OAUTH_CLIENT_ID": "geovisio",
            "OAUTH_CLIENT_SECRET": "what_a_secret",
            "API_FORCE_AUTH_ON_UPLOAD": "true",
            "API_ENFORCE_TOS_ACCEPTANCE": "true",
        }
    ) as app:
        yield app


@pytest.fixture
def auth_client(auth_app):
    with auth_app.app_context():
        with auth_app.test_client() as client:
            yield client


@pytest.fixture
def server(auth_app):
    """start a real server, listening to a port
    Used to be able to receive queries from keycloak
    """
    import threading
    from werkzeug.serving import make_server

    port = 5005
    s = make_server("localhost", port, auth_app, threaded=True)
    t = threading.Thread(target=s.serve_forever)

    t.start()
    yield f"http://localhost:{port}"
    s.shutdown()


@pytest.fixture(scope="module")
def keycloak():
    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../..")
    override_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "docker-compose-auth-test.yml")
    with compose.DockerCompose(
        root_dir,
        compose_file_name=[os.path.join(root_dir, "docker", "docker-compose-keycloak.yml"), override_file],
        pull=True,
    ) as dco:
        host = dco.get_service_host("auth", 8080)
        port = dco.get_service_port("auth", 8080)
        keycloak_url = f"http://{host}:{port}"
        keycloak_realm_url = f"{keycloak_url}/realms/geovisio"
        dco.wait_for(keycloak_realm_url)
        time.sleep(1)

        yield keycloak_url
        stdout, stderr = dco.get_logs()
        if stderr:
            print("Errors\n:{}".format(stderr))


class RetryException(Exception):
    pass


@pytest.fixture(scope="module")
def minio():
    root_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../..")
    with compose.DockerCompose(
        root_dir,
        compose_file_name=[os.path.join(root_dir, "docker", "docker-compose-minio.yml")],
        pull=True,
        wait=False,
    ) as dco:
        host = dco.get_service_host("minio", 9000)
        port = dco.get_service_port("minio", 9000)
        minio_url = f"http://{host}:{port}"

        from testcontainers.core.waiting_utils import wait_container_is_ready

        @wait_container_is_ready(RetryException)
        def wait_for_minio():
            if "minio-ready" not in (c.Service for c in dco.get_containers()):
                raise RetryException("minio-ready not ready")
            return True

        wait_for_minio()

        yield minio_url
        stdout, stderr = dco.get_logs()
        if stderr:
            print("Errors\n:{}".format(stderr))


@pytest.fixture(scope="function", autouse=True)
def cleanup_minio(minio):
    """Cleanup all data in minio between tests"""
    import boto3

    s3 = boto3.resource(
        "s3",
        aws_access_key_id="geovisio",
        aws_secret_access_key="SOME_VERY_SECRET_KEY",
        endpoint_url=minio,
    )
    for b in ["panoramax-public", "panoramax-private"]:
        bucket = s3.Bucket(b)
        if bucket.creation_date:
            # Only delete if bucket exists
            bucket.object_versions.delete()

    yield


def redirect_history(r):
    return [urlparse(h.url).path for h in (r.history + [r])]


def get_keycloak_authenticate_form_url(response):
    """Little hack to parse keycloak HTML to get the url to the authenticate form"""
    url = re.search('action="(.*login-actions/authenticate[^"]*)"', response.text)
    assert url
    url = url.group(1).replace("&amp;", "&")
    return url


def get_keycloak_logout_form_url(response):
    """Little hack to parse keycloak HTML to get the url to the logout form"""
    url = re.search('action="(.*logout/logout-confirm[^"]*)"', response.text)
    assert url
    url = url.group(1).replace("&amp;", "&")

    session_code = re.search('name="session_code" value="([^"]*)"', response.text)
    assert session_code
    session_code = session_code.group(1)

    return url, session_code


def pytest_collection_modifyitems(items):
    """
    Hack to mark all test depending on minio or keycloak as `docker` to be able to skip them in CI

    Note: it does not seems like a cleaner way to do this is possible, cf https://github.com/pytest-dev/pytest/issues/1368
    """
    for item in items:
        fixtures = getattr(item, "fixturenames", ())
        if "keycloak" in fixtures or "minio" in fixtures:
            item.add_marker("docker")
            item.add_marker("skipci")
