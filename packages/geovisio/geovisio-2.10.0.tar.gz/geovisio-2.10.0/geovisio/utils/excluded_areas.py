from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict
from geojson_pydantic import MultiPolygon, FeatureCollection, Feature
from geovisio.utils import db
from geovisio.errors import InvalidAPIUsage
from flask import current_app
from flask_babel import gettext as _
from psycopg.sql import SQL, Literal
from psycopg.rows import class_row


class ExcludedArea(BaseModel):
    """An excluded area is a geographical boundary where pictures should not be accepted."""

    id: UUID
    label: Optional[str] = None
    is_public: bool = False
    account_id: Optional[UUID] = None

    model_config = ConfigDict()


ExcludedAreaFeature = Feature[MultiPolygon, ExcludedArea]
ExcludedAreaFeatureCollection = FeatureCollection[ExcludedAreaFeature]


def get_excluded_area(id: UUID) -> Optional[ExcludedAreaFeature]:
    """Get the excluded area corresponding to the ID"""
    return db.fetchone(
        current_app,
        SQL(
            """SELECT id, label, is_public, account_id, ST_AsGeoJSON(geom) AS geometry
FROM excluded_area
WHERE id = %(id)s"""
        ),
        {"id": id},
        row_factory=class_row(ExcludedAreaFeature),
    )


def list_excluded_areas(is_public: Optional[bool] = None, account_id: Optional[UUID] = None) -> ExcludedAreaFeatureCollection:
    where = [Literal(True)]
    if is_public is not None:
        where.append(SQL("is_public IS {}").format(Literal(is_public)))
    if account_id:
        where.append(SQL("account_id = {}").format(Literal(account_id)))

    areas = db.fetchall(
        current_app,
        SQL(
            """SELECT
    'Feature' as type,
    json_build_object(
        'id', id,
        'label', label,
        'is_public', is_public,
        'account_id', account_id
    ) as properties,
    ST_AsGeoJSON(geom)::json as geometry
FROM excluded_areas
WHERE {}"""
        ).format(SQL(" AND ").join(where)),
        row_factory=class_row(ExcludedAreaFeature),
    )

    return ExcludedAreaFeatureCollection(type="FeatureCollection", features=areas)


def delete_excluded_area(areaId: UUID, accountId: Optional[UUID] = None):
    where = [SQL("id = {}").format(Literal(areaId))]
    if accountId is not None:
        where.append(SQL("account_id = {}").format(accountId))

    with db.execute(
        current_app,
        SQL("DELETE FROM excluded_areas WHERE {}").format(SQL(" AND ").join(where)),
    ) as res:
        area_deleted = res.rowcount

        if not area_deleted:
            raise InvalidAPIUsage(_("Impossible to find excluded area"), status_code=404)
        return "", 204
