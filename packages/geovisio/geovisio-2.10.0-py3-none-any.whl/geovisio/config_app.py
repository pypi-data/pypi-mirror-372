import os
import os.path
from urllib.parse import urlparse
import datetime
import logging
from typing import Optional, Dict
import croniter
from pydantic import BaseModel, EmailStr
from pydantic.color import Color
from pydantic.networks import HttpUrl
import json
from flask import Flask, current_app

from geovisio.utils import website
from geovisio.utils.model_query import get_db_params_and_values
from geovisio.utils.website import Website


class ApiSummary(BaseModel):
    name: Dict[str, str] = {"en": "Panoramax"}
    description: Dict[str, str] = {"en": "The open source photo mapping solution"}
    logo: HttpUrl = "https://gitlab.com/panoramax/gitlab-profile/-/raw/main/images/panoramax.svg"
    color: Color = "#5e499c"
    email: EmailStr = "panoramax@panoramax.fr"
    geo_coverage: Dict[str, str] = {"en": "Worldwide\nThe picture can be sent from anywhere in the world."}


class DefaultConfig:
    API_SUMMARY = ApiSummary()
    API_VIEWER_PAGE = "viewer.html"
    API_MAIN_PAGE = "main.html"
    # we default we keep the session cookie 7 days, users would have to renew their login after this
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=7).total_seconds()
    API_FORCE_AUTH_ON_UPLOAD = False
    PICTURE_PROCESS_DERIVATES_STRATEGY = "ON_DEMAND"
    PICTURE_PROCESS_NB_RETRIES = 5
    PICTURE_PROCESS_KEEP_UNBLURRED_PARTS = False
    API_BLUR_URL = None
    PICTURE_PROCESS_THREADS_LIMIT = 1
    DB_CHECK_SCHEMA = True  # If True check the database schema, and do not start the api if not up to date
    API_PICTURES_LICENSE_SPDX_ID = None
    API_PICTURES_LICENSE_URL = None
    DEBUG_PICTURES_SKIP_FS_CHECKS_WITH_PUBLIC_URL = False
    SESSION_COOKIE_HTTPONLY = False
    PICTURE_PROCESS_REFRESH_CRON = (
        "0 2 * * *"  # Background worker will refresh by default some stats at 2 o'clock in the night (local time of the server)
    )
    DB_MIN_CNX = 0
    DB_MAX_CNX = 10
    DB_STATEMENT_TIMEOUT = 5 * 60 * 1000  # default statement timeout in ms (5mn)
    API_ACCEPT_DUPLICATE = False
    API_ENFORCE_TOS_ACCEPTANCE = False  # if True, users won't be able to upload pictures without accepting the terms of service
    API_WEBSITE_URL = (
        website.WEBSITE_UNDER_SAME_HOST
    )  # by default we consider that there is a panoramax website on the same host as the API
    API_REGISTRATION_IS_OPEN = False  # tells that anyone can create an account. Only used for reference in the federation for the moment


def read_config(app, test_config):
    app.config.from_object(DefaultConfig)

    # All env variables prefixed by 'FLASK_' are loaded (and striped from the prefix)
    app.config.from_prefixed_env()

    confFromEnv = [
        # Filesystems parameters
        "FS_URL",
        "FS_TMP_URL",
        "FS_PERMANENT_URL",
        "FS_DERIVATES_URL",
        # Database parameters
        "DB_URL",
        "DB_PORT",
        "DB_HOST",
        "DB_USERNAME",
        "DB_PASSWORD",
        "DB_NAME",
        "DB_CHECK_SCHEMA",
        "DB_MIN_CNX",
        "DB_MAX_CNX",
        "DB_STATEMENT_TIMEOUT",
        # API
        "API_SUMMARY",
        "API_BLUR_URL",
        "API_VIEWER_PAGE",
        "API_MAIN_PAGE",
        "API_LOG_LEVEL",
        "API_FORCE_AUTH_ON_UPLOAD",
        "API_PERMANENT_PICTURES_PUBLIC_URL",
        "API_DERIVATES_PICTURES_PUBLIC_URL",
        "API_PICTURES_LICENSE_SPDX_ID",
        "API_PICTURES_LICENSE_URL",
        "API_ACCEPT_DUPLICATE",
        "API_GIT_VERSION",
        "API_DEFAULT_COLLABORATIVE_METADATA_EDITING",
        "API_ENFORCE_TOS_ACCEPTANCE",
        "API_WEBSITE_URL",
        "API_REGISTRATION_IS_OPEN",
        # Picture process
        "PICTURE_PROCESS_DERIVATES_STRATEGY",
        "PICTURE_PROCESS_THREADS_LIMIT",
        "PICTURE_PROCESS_REFRESH_CRON",
        "PICTURE_PROCESS_NB_RETRIES",
        "PICTURE_PROCESS_KEEP_UNBLURRED_PARTS",
        # OAUTH
        "OAUTH_PROVIDER",
        "OAUTH_OIDC_URL",
        "OAUTH_CLIENT_ID",
        "OAUTH_CLIENT_SECRET",
        # Infrastructure
        "INFRA_NB_PROXIES",
        # sentry configuration
        "SENTRY_DSN",  # SENTRY connection string
        "SENTRY_TRACE_SAMPLE_RATE",  # % of traces to send to sentry
        "SENTRY_PROFIL_SAMPLE_RATE",  # % of profil (performance reports) to send to sentry
        # Debug
        "DEBUG_PICTURES_SKIP_FS_CHECKS_WITH_PUBLIC_URL",
    ]
    for e in confFromEnv:
        if os.environ.get(e):
            app.config[e] = os.environ.get(e)

    legacyVariables = {
        "BLUR_URL": "API_BLUR_URL",
        "VIEWER_PAGE": "API_VIEWER_PAGE",
        "MAIN_PAGE": "API_MAIN_PAGE",
        "LOG_LEVEL": "API_LOG_LEVEL",
        "FORCE_AUTH_ON_UPLOAD": "API_FORCE_AUTH_ON_UPLOAD",
        "DERIVATES_STRATEGY": "PICTURE_PROCESS_DERIVATES_STRATEGY",
        "OIDC_URL": "OAUTH_OIDC_URL",
        "CLIENT_ID": "OAUTH_CLIENT_ID",
        "CLIENT_SECRET": "OAUTH_CLIENT_SECRET",
        "NB_PROXIES": "INFRA_NB_PROXIES",
        "SECRET_KEY": "FLASK_SECRET_KEY",
        "SESSION_COOKIE_DOMAIN": "FLASK_SESSION_COOKIE_DOMAIN",
    }
    for legacyKey, newKey in legacyVariables.items():
        l = os.environ.get(legacyKey)
        if l:
            logging.warn(f"A legacy parameter '{legacyKey}' has been set, this has been replaced with '{newKey}")
            app.config[newKey] = l

    # overriding from test_config
    if test_config is not None:
        app.config.update(test_config)

    if "API_LOG_LEVEL" in app.config:
        logging.getLogger().setLevel(app.config["API_LOG_LEVEL"].upper())

    # Create DB_URL from separated parameters
    if "DB_PORT" in app.config or "DB_HOST" in app.config or "DB_USERNAME" in app.config or "DB_PASSWORD" in app.config:
        username = app.config.get("DB_USERNAME", "")
        passw = app.config.get("DB_PASSWORD", "")
        host = app.config.get("DB_HOST", "")
        port = app.config.get("DB_PORT", "")
        dbname = app.config.get("DB_NAME", "")

        app.config["DB_URL"] = f"postgres://{username}:{passw}@{host}:{port}/{dbname}"

    app.config["DB_CHECK_SCHEMA"] = _read_bool(app.config, "DB_CHECK_SCHEMA")

    if app.config.get("API_BLUR_URL") is not None and len(app.config.get("API_BLUR_URL")) > 0:
        try:
            urlparse(app.config.get("API_BLUR_URL"))
        except:
            raise Exception("Blur API URL is invalid: " + app.config.get("API_BLUR_URL"))
    else:
        app.config["API_BLUR_URL"] = None

    if app.config["PICTURE_PROCESS_DERIVATES_STRATEGY"] not in ["ON_DEMAND", "PREPROCESS"]:
        raise Exception(
            f"Unknown picture derivates strategy: '{app.config['PICTURE_PROCESS_DERIVATES_STRATEGY']}'. Please set to one of ON_DEMAND, PREPROCESS"
        )
    app.config["PICTURE_PROCESS_NB_RETRIES"] = int(app.config["PICTURE_PROCESS_NB_RETRIES"])

    # Parse API summary
    if not isinstance(app.config.get("API_SUMMARY"), ApiSummary):
        try:
            if isinstance(app.config.get("API_SUMMARY"), str):
                app.config["API_SUMMARY"] = ApiSummary(**json.loads(app.config["API_SUMMARY"]))
            elif isinstance(app.config.get("API_SUMMARY"), dict):
                app.config["API_SUMMARY"] = ApiSummary(**app.config["API_SUMMARY"])
            elif app.config.get("API_SUMMARY") is not None:
                raise Exception("Value is not a JSON")
        except Exception as e:
            raise Exception("Parameter API_SUMMARY is not recognized") from e

    app.config["API_REGISTRATION_IS_OPEN"] = _read_bool(app.config, "API_REGISTRATION_IS_OPEN")

    # Checks on front-end related variables
    templateFolder = os.path.join(app.root_path, app.template_folder)
    for pageParam in ["API_MAIN_PAGE", "API_VIEWER_PAGE"]:
        if app.config.get(pageParam) is None or len(app.config[pageParam].strip()) == 0:
            raise Exception(f"{pageParam} environment variable is not defined. It should either be a Flask template name, or a valid URL.")

        if not app.config[pageParam].startswith("http") and not os.path.exists(os.path.join(templateFolder, app.config[pageParam])):
            raise Exception(
                f"{pageParam} variable points to invalid template '{app.config[pageParam]}' (not found in '{templateFolder}' folder)"
            )

    app.config["API_WEBSITE_URL"] = Website(app.config.get("API_WEBSITE_URL"))

    # The default is to use only one only 1 thread to process uploaded pictures
    # if set to 0 no background worker is run, if set to -1 all cpus will be used
    app.config["PICTURE_PROCESS_THREADS_LIMIT"] = _get_threads_limit(app.config["PICTURE_PROCESS_THREADS_LIMIT"])

    # Auth on upload
    app.config["API_FORCE_AUTH_ON_UPLOAD"] = app.config.get("API_FORCE_AUTH_ON_UPLOAD") == "true"

    if app.config.get("WEBP_METHOD") is not None and app.config.get("WEBP_METHOD") != "":
        raise Exception("WEBP_METHOD is deprecated and should not be used")

    if app.config.get("WEBP_CONVERSION_THREADS_LIMIT") is not None and app.config.get("WEBP_CONVERSION_THREADS_LIMIT") != "":
        raise Exception("WEBP_CONVERSION_THREADS_LIMIT is deprecated and should not be used")

    if app.config.get("PICTURE_PROCESS_DERIVATES_STRATEGY") != "PREPROCESS" and app.config.get("API_DERIVATES_PICTURES_PUBLIC_URL"):
        raise Exception(
            "Derivates can be served though another url only if they are all pregenerated, either unset `API_DERIVATES_PICTURES_PUBLIC_URL` or set `PICTURE_PROCESS_DERIVATES_STRATEGY` to `PREPROCESS`"
        )

    if (app.config.get("API_PICTURES_LICENSE_SPDX_ID") is None) + (app.config.get("API_PICTURES_LICENSE_URL") is None) == 1:
        raise Exception(
            "API_PICTURES_LICENSE_SPDX_ID and API_PICTURES_LICENSE_URL should either be both unset (thus the pictures are under a proprietary license) or both set"
        )
    if app.config.get("API_PICTURES_LICENSE_SPDX_ID") is None:
        app.config["API_PICTURES_LICENSE_SPDX_ID"] = "proprietary"

    cron_val = app.config["PICTURE_PROCESS_REFRESH_CRON"]
    if not croniter.croniter.is_valid(cron_val):
        raise Exception(f"PICTURE_PROCESS_REFRESH_CRON should be a valid cron syntax, got '{cron_val}'")

    app.config["PICTURE_PROCESS_KEEP_UNBLURRED_PARTS"] = _read_bool(app.config, "PICTURE_PROCESS_KEEP_UNBLURRED_PARTS")

    app.config["API_ACCEPT_DUPLICATE"] = _read_bool(app.config, "API_ACCEPT_DUPLICATE")
    app.config["API_ENFORCE_TOS_ACCEPTANCE"] = _read_bool(app.config, "API_ENFORCE_TOS_ACCEPTANCE")
    app.config["API_DEFAULT_COLLABORATIVE_METADATA_EDITING"] = _read_bool(app.config, "API_DEFAULT_COLLABORATIVE_METADATA_EDITING")

    app.config["DB_STATEMENT_TIMEOUT"] = int(app.config["DB_STATEMENT_TIMEOUT"])

    #
    # Add generated config vars
    #
    app.url_map.strict_slashes = False

    if app.config.get("API_COMPRESSION", True) is False:
        # Note that this API_COMPRESSION variable is only used in tests
        app.config["COMPRESS_MIMETYPES"] = []
    else:
        app.config["COMPRESS_MIMETYPES"] = [
            "text/html",
            "text/css",
            "text/plain",
            "text/xml",
            "application/x-javascript",
            "application/json",
            "application/rss+xml",
            "application/geo+json",
        ]
    app.config["EXECUTOR_MAX_WORKERS"] = app.config["PICTURE_PROCESS_THREADS_LIMIT"]
    app.config["EXECUTOR_PROPAGATE_EXCEPTIONS"] = True  # propagate the excecutor's exceptions, to be able to trace them


def _read_bool(config, value_name: str) -> Optional[bool]:
    value = config.get(value_name)
    if value is None:
        return value
    if type(value) == bool:
        return value
    if type(value) == str:
        return value.lower() == "true"
    raise Exception(f"Configuration {value_name} should either be a boolean or a string, got '{value}'")


def _get_threads_limit(param: str) -> int:
    """Computes maximum thread limit depending on environment variables and available CPU.

    Value returned is the minimum between the value and the available number of cpus

    Parameters
    ----------
    param : str
        Read value from environment variable. If value is -1, uses default or CPU count instead

    Returns
    -------
    int
        The appropriate max thread value
    """
    p = int(param)

    nb_cpu = os.cpu_count()
    if p == -1:
        if nb_cpu is None:
            logging.warning("Number of cpu is unknown, using only 1 thread")
            return 1
        return nb_cpu
    return min(p, os.cpu_count() or 1)


class DBConfiguration(BaseModel):
    """Configuration persisted in the database.
    Not all configurations are meant to be persisted in the database"""

    collaborative_metadata: Optional[bool] = None


def persist_config(app: Flask):
    """
    Persist the configuration in the database if needed.

    Note that the configuration can only be initialized like this, if the configuration has been changed in the database, it will not be updated using environment variables.
    """
    from geovisio.utils import db
    from psycopg.rows import class_row
    from psycopg.sql import SQL, Literal
    from psycopg.errors import UndefinedTable

    with db.conn(app) as conn, conn.transaction() as tr, conn.cursor(row_factory=class_row(DBConfiguration)) as cur:
        try:
            db_config = cur.execute("SELECT * FROM configurations LIMIT 1").fetchone()
        except UndefinedTable:
            logging.warning("Database schema has not been updated yet, configuration will not be persisted")
            return
        if not db_config:
            raise Exception("Database has not been correctly initialized, there should always be a default")
        config_to_persist = DBConfiguration()

        # add the fields we want to persist here
        collaborative_metadata = app.config["API_DEFAULT_COLLABORATIVE_METADATA_EDITING"]
        if db_config.collaborative_metadata is None:
            config_to_persist.collaborative_metadata = collaborative_metadata
        elif db_config.collaborative_metadata != collaborative_metadata and collaborative_metadata is not None:
            logging.warning(
                "The environment variable `API_DEFAULT_COLLABORATIVE_METADATA_EDITING` has a different value than its value in the database, it will be ignored. Update the `collaborative_metadata` field in the database if you want to change it."
            )

        params_as_dict = get_db_params_and_values(config_to_persist)
        fields = params_as_dict.fields_for_set()
        if not params_as_dict.has_updates():
            return

        logging.info("Persisting configuration to the database from environement variables")
        # Persist all set fields in the database
        cur.execute(
            SQL("UPDATE configurations SET {fields} RETURNING *").format(fields=fields),
            params_as_dict.params_as_dict,
        )
