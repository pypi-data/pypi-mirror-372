import flask
from typing import Dict, Any
from flask import jsonify, current_app
from flask_babel import get_locale
from geovisio.web.utils import get_api_version
from geovisio.utils import db
from psycopg.rows import class_row
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer
import datetime

bp = flask.Blueprint("configuration", __name__, url_prefix="/api")


@bp.route("/configuration")
def configuration():
    """Return instance configuration information
    ---
    tags:
        - Metadata
    responses:
        200:
            description: Information about the instance configuration
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioConfiguration'
    """

    apiSum = flask.current_app.config["API_SUMMARY"]
    userLang = get_locale().language
    return jsonify(
        {
            "name": _get_translated(apiSum.name, userLang),
            "description": _get_translated(apiSum.description, userLang),
            "geo_coverage": _get_translated(apiSum.geo_coverage, userLang),
            "logo": str(apiSum.logo),
            "color": str(apiSum.color),
            "email": apiSum.email,
            "auth": _auth_configuration(),
            "license": _license_configuration(),
            "version": get_api_version(),
            "pages": _get_pages(),
            "defaults": _get_default_values(),
        }
    )


def _get_translated(prop: Dict[str, str], userLang) -> Dict[str, Any]:
    return {"label": prop.get(userLang, prop.get("en")), "langs": prop}


def _auth_configuration():
    from geovisio.utils import auth

    if auth.oauth_provider is None:
        return {"enabled": False}
    else:
        return {
            "enabled": True,
            "user_profile": {"url": auth.oauth_provider.user_profile_page_url()},
            "registration_is_open": flask.current_app.config["API_REGISTRATION_IS_OPEN"],
            "enforce_tos_acceptance": flask.current_app.config["API_ENFORCE_TOS_ACCEPTANCE"],
        }


def _license_configuration():
    l = {"id": flask.current_app.config["API_PICTURES_LICENSE_SPDX_ID"]}
    u = flask.current_app.config.get("API_PICTURES_LICENSE_URL")
    if u:
        l["url"] = u
    return l


def _get_pages():

    pages = db.fetchall(current_app, "SELECT distinct(name) FROM pages")

    return [p[0] for p in pages]


class Config(BaseModel):
    collaborative_metadata: Optional[bool]
    split_distance: Optional[int] = Field(validation_alias="default_split_distance")
    split_time: Optional[datetime.timedelta] = Field(validation_alias="default_split_time")
    duplicate_distance: Optional[float] = Field(validation_alias="default_duplicate_distance")
    duplicate_rotation: Optional[int] = Field(validation_alias="default_duplicate_rotation")

    @field_serializer("split_time")
    def split_time_to_s(self, s: datetime.timedelta, _):
        return s.total_seconds()


def _get_default_values():
    return db.fetchone(current_app, "SELECT * FROM configurations", row_factory=class_row(Config)).model_dump()
