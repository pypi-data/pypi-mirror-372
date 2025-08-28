"""GeoVisio API - Main"""

__version__ = "2.10.0"

import os
from flask import Flask, jsonify, stream_template, send_from_directory, redirect, request, url_for
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_compress import Compress
from flask_babel import Babel
from flasgger import Swagger
import logging
from logging.config import dictConfig

from geovisio import db_migrations, config_app, admin_cli, errors, utils
from geovisio.utils import db, filesystems, sentry
from geovisio.web import (
    auth,
    docs,
    pictures,
    stac,
    map,
    users,
    configuration,
    tokens,
    collections,
    items,
    upload_set,
    reports,
    excluded_areas,
    prepare,
    pages,
    annotations,
)
from geovisio.workers import runner_pictures


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"simple": {"format": "%(asctime)s [%(threadName)s][%(levelname)s] %(name)s: %(message)s"}},
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
    },
    "loggers": {
        "PIL": {"handlers": ["stdout", "stderr"], "level": "WARN", "propagate": False},  # lower PIL loggers to only have warnings
        "watchdog": {
            "handlers": ["stdout", "stderr"],
            "level": "WARN",
            "propagate": False,
        },  # lower watchdog loggers too (used by flask hot reload)
    },
    "root": {"level": "INFO", "handlers": ["stderr", "stdout"]},
}
dictConfig(LOGGING_CONFIG)


# Init i18n
def get_locale():
    try:
        return request.accept_languages.best_match(["de", "fr", "en", "es", "hu"]) or "en"
    except:
        return "en"


def create_app(test_config=None, app=None):
    """API launcher method"""
    #
    # Create and setup Flask App
    #
    if app is None:
        app = Flask(__name__, instance_relative_config=True)
    CORS(app, supports_credentials=True)

    config_app.read_config(app, test_config)
    sentry.init(app)
    db.create_db_pool(app)
    Babel(app, locale_selector=get_locale)
    Compress(app)

    # Prepare filesystem
    createDirNoFailure(app.instance_path)
    app.config["FILESYSTEMS"] = filesystems.openFilesystemsFromConfig(app.config)

    # Check database connection and update its schema if needed
    if app.config.get("DB_CHECK_SCHEMA"):
        db_migrations.update_db_schema(app.config["DB_URL"])

    config_app.persist_config(app)

    if app.config.get("OAUTH_PROVIDER"):
        utils.auth.make_auth(app)
        app.register_blueprint(auth.bp)
    else:
        app.register_blueprint(auth.disabled_auth_bp())

    nb_proxies = app.config.get("INFRA_NB_PROXIES")
    if nb_proxies:
        nb_proxies = int(nb_proxies)
        # tell flask that it runs behind NB_PROXIES proxies so that it can trust the `X-Forwarded-` headers
        # https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
        from werkzeug.middleware.proxy_fix import ProxyFix

        app.wsgi_app = ProxyFix(
            app.wsgi_app, x_for=nb_proxies, x_proto=nb_proxies, x_host=nb_proxies, x_prefix=nb_proxies, x_port=nb_proxies
        )

    # store the background processor in the app context
    app.background_processor = runner_pictures.PictureBackgroundProcessor(app)

    #
    # List available routes/blueprints
    #

    app.register_blueprint(pictures.bp)
    app.register_blueprint(stac.bp)
    app.register_blueprint(collections.bp)
    app.register_blueprint(items.bp)
    app.register_blueprint(map.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(configuration.bp)
    app.register_blueprint(tokens.bp)
    app.register_blueprint(upload_set.bp)
    app.register_blueprint(reports.bp)
    app.register_blueprint(excluded_areas.bp)
    app.register_blueprint(prepare.bp)
    app.register_blueprint(pages.bp)
    app.register_blueprint(annotations.bp)

    # Register CLI comands
    app.register_blueprint(admin_cli.bp, cli_group=None)

    @app.cli.command("picture-worker")
    @with_appcontext
    def run_picture_worker():
        """Run a worker to process pictures after upload. Each worker use one thread, and several workers can be run in parallel"""
        logging.info("Running picture worker")
        worker = runner_pictures.PictureProcessor(app=app, stop=False)
        worker.process_jobs()

    #
    # API documentation
    #
    Swagger(app, config=docs.API_CONFIG, merge=True, template=docs.getApiDocs())

    #
    # Add generic routes
    #

    template_vars = {"API_VERSION_MAJOR_MINOR": ".".join(__version__.split(".")[0:2])}

    # Main page
    @app.route("/")
    def index():
        if app.config["API_MAIN_PAGE"].startswith("http"):
            return redirect(app.config["API_MAIN_PAGE"], 301)
        else:
            return stream_template(app.config["API_MAIN_PAGE"], **template_vars)

    # Viewer
    @app.route("/viewer")
    def viewer():
        if app.config["API_VIEWER_PAGE"].startswith("http"):
            return redirect(app.config["API_VIEWER_PAGE"], 301)
        else:
            return stream_template(app.config["API_VIEWER_PAGE"], **template_vars)

    @app.route("/apidocs")
    @app.route("/apidocs/")
    def apidocsRedirects():
        return redirect(docs.API_CONFIG["specs_route"], 301)

    @app.route("/apispec_1.json")
    def apispecRedirects():
        return redirect(docs.API_CONFIG["specs"][0]["route"], 301)

    @app.route("/static/img/<path:path>")
    def viewer_img(path):
        return send_from_directory(os.path.join(os.path.dirname(__file__), "../images"), path)

    @app.route("/favicon.ico")
    def favicon():
        return redirect("/static/img/favicon.ico")

    @app.route("/api/debug_headers")
    def debug_headers():
        """Endpoint handy when setting a new instance to check if all the headers are set correctly,
        and especially the X-Forwarded-* header that needs to be set by the proxies in order for the API to correctly build internal urls.

        The headers are only printed to the console, so it's only for the instance administrator that has access to those logs.
        """
        logging.info(request.headers)

        return jsonify({"test_url": url_for("index", _external=True)}), 200

    # Errors
    @app.errorhandler(errors.InvalidAPIUsage)
    def invalid_api_usage(e):
        return jsonify(e.to_dict()), e.status_code

    @app.errorhandler(errors.InternalError)
    def internal_error(e):
        return jsonify(e.to_dict()), e.status_code

    @app.after_request
    def after_request_func(response):
        from flask import g

        user_dependant_response = getattr(g, "user_dependant_response", True)
        # tell a shared proxy not to cache any logged response that can contain user specific information
        from geovisio.utils.auth import get_current_account

        is_logged = False
        try:
            # we don't care if the get_current_account function raises an error here
            is_logged = get_current_account() is not None
        except:
            pass
        if user_dependant_response is False or not is_logged:
            response.cache_control.public = True
        else:
            response.cache_control.private = True

        # disable no_cache that can be set by flask.send_file, since we want to control the cache behavior
        response.cache_control.no_cache = None
        return response

    return app


def createDirNoFailure(directory):
    """Creates a directory on disk if not already existing

    Parameters
    ----------
    directory : str
            Path of the directory to create
    """

    try:
        os.makedirs(directory)
    except OSError:
        pass
