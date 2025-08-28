from sentry_sdk.integrations import Integration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.boto3 import Boto3Integration
from sentry_sdk import Hub
from sentry_sdk.consts import OP
import psycopg
from sentry_sdk.tracing_utils import record_sql_queries
import sentry_sdk


def init(app):
    """
    Initialize an [Sentry](https://sentry.io/) exporter.

    If is used to send server side metric/errors to an sentry server, to be able to monitor GeoVisio.

    Note: Sentry should be able to send [Opentelemetry](https://opentelemetry.io/) metric (instead of their custom metrics),
    but it does not seems to work for the moment. At a latter point, maybe we'll be able to replace all sentry's traces, with more generic Opentelemetry ones.
    """
    # by default sentry look for an `SENTRY_DSN`, and if its not there, sentry is not activated
    sentry_sdk.init(
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        traces_sample_rate=float(app.config.get("SENTRY_TRACE_SAMPLE_RATE", 0.1)),
        profiles_sample_rate=float(app.config.get("SENTRY_PROFIL_SAMPLE_RATE", 0.1)),
        release=_get_version(),
        integrations=[FlaskIntegration(), Boto3Integration(), PsycoPGIntegration(), FileSystemIntegration()],
    )


def _get_version():
    import geovisio

    # TODO: maybe we can later add the commit sha there
    return geovisio.__version__


class PsycoPGIntegration(Integration):
    """Add metrics around all calls to pyscopg cursor.execute"""

    identifier = "psycopg"

    @staticmethod
    def setup_once():
        # psycopg.Connection.connect = _wrap_conn_connect(psycopg.Connection.connect) # Note: maybe later it will be handy to trace also connection requests
        psycopg.Cursor.execute = _wrap_cursor_execute(psycopg.Cursor.execute)


def _wrap_cursor_execute(f):
    def _inner(
        self,
        query,
        params=None,
        *,
        prepare=None,
        binary=None,
    ):
        hub = Hub.current
        if hub.get_integration(PsycoPGIntegration) is None:
            return f(self, query, params, prepare=prepare, binary=binary)

        with record_sql_queries(
            cursor=self,
            query=query,
            params_list=params,
            paramstyle="format",
            executemany=False,
        ):
            res = f(self, query, params, prepare=prepare, binary=binary)
        return res

    return _inner


class FileSystemIntegration(Integration):
    """Add metrics to the 2 most useful filesystem, the 'os file' filesystem and the s3 filesystem"""

    identifier = "filesystem"

    @staticmethod
    def setup_once():
        from fs.osfs import OSFS
        from fs_s3fs import S3FS

        S3FS.openbin = FileSystemIntegration._wrap(S3FS.openbin, "openbin")
        S3FS.writefile = FileSystemIntegration._wrap(S3FS.writefile, "writefile")
        S3FS.writebytes = FileSystemIntegration._wrap(S3FS.writebytes, "writebytes")

        OSFS.openbin = FileSystemIntegration._wrap(OSFS.openbin, "openbin")
        OSFS.writefile = FileSystemIntegration._wrap(OSFS.writefile, "writefile")
        OSFS.writebytes = FileSystemIntegration._wrap(OSFS.writebytes, "writebytes")

    @staticmethod
    def _wrap(f, name):
        def _inner(self, path, *args, **kwargs):
            hub = Hub.current
            if hub.get_integration(FileSystemIntegration) is None:
                return f(self, path, *args, **kwargs)

            with hub.start_span(op=OP.FUNCTION, description=name) as span:
                span.set_data("file_path", path)
                res = f(self, path, *args, **kwargs)
            return res

        return _inner
