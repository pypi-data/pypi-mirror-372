from typing import List, Optional
from uuid import UUID
from flask import current_app
import psycopg
from pydantic import BaseModel, Field, field_validator
from psycopg.sql import SQL
from psycopg.rows import class_row, dict_row

from geovisio import errors
from geovisio.utils import db, model_query
from geovisio.utils import semantics
from geovisio.utils.pic_shape import InputAnnotationShape, Geometry, get_coords_from_shape, shape_as_geometry
from geovisio.utils.tags import SemanticTag, SemanticTagUpdate


class Annotation(BaseModel):
    id: UUID
    """ID of the annotation"""
    picture_id: UUID
    """ID of the picture to which the annotation is linked to"""
    shape: Geometry
    """Polygon defining the annotation"""
    semantics: List[SemanticTag] = Field(default_factory=list)
    """Semantic tags associated to the annotation"""

    @field_validator("semantics", mode="before")
    @classmethod
    def parse_semantics(cls, value):
        return value or []

    @field_validator("shape", mode="before")
    def validate_shape(cls, value):
        # if its a bounding box, transform it to a polygon
        return shape_as_geometry(value)


class AnnotationCreationRow(BaseModel):
    picture_id: UUID
    """ID of the picture to which the annotation is linked to"""
    shape: Geometry
    """shape defining the annotation"""


class AnnotationCreationParameter(BaseModel):
    account_id: UUID
    """ID of the account that created the annotation"""
    picture_id: UUID
    """ID of the picture to which the annotation is linked to"""
    shape: InputAnnotationShape
    """Shape defining the annotation.
The annotation shape is either a full geojson geometry or only a bounding box (4 floats).

The coordinates should be given in pixel, starting from the bottom left of the picture.

Note that the API will always output geometry as geojson geometry (thus will transform the bbox into a polygon).
"""

    semantics: List[SemanticTagUpdate] = Field(default_factory=list)
    """Semantic tags associated to the annotation"""

    def shape_as_geometry(self) -> Geometry:
        return shape_as_geometry(self.shape)


def creation_annotation(params: AnnotationCreationParameter, conn: psycopg.Connection) -> Annotation:
    """Create an annotation in the database.
    Note, this should be called from an autocommit connection"""

    model = model_query.get_db_params_and_values(
        AnnotationCreationRow(picture_id=params.picture_id, shape=params.shape_as_geometry()), jsonb_fields={"shape"}
    )

    with conn.transaction(), conn.cursor(row_factory=class_row(Annotation)) as cursor:
        # we check that the shape is valid
        check_shape(conn, params)

        annotation = cursor.execute(
            "SELECT * FROM annotations WHERE picture_id = %(picture_id)s AND shape = %(shape)s", model.params_as_dict
        ).fetchone()
        if annotation is None:
            annotation = cursor.execute(
                """INSERT INTO annotations (picture_id, shape)
        VALUES (%(picture_id)s, %(shape)s)
        RETURNING *""",
                model.params_as_dict,
            ).fetchone()

        if annotation is None:
            raise Exception("Impossible to insert annotation in database")

        semantics.update_tags(
            cursor=cursor,
            entity=semantics.Entity(semantics.EntityType.annotation, annotation.id),
            actions=params.semantics,
            account=params.account_id,
            annotation=annotation,
        )

        return get_annotation(conn, annotation.id)


def check_shape(conn: psycopg.Connection, params: AnnotationCreationParameter):
    """Check that the shape is valid"""
    with conn.cursor(row_factory=dict_row) as cursor:
        picture_size = cursor.execute(
            SQL("SELECT (metadata->>'width')::int AS width, (metadata->>'height')::int AS height FROM pictures WHERE id = %(pic)s"),
            {"pic": params.picture_id},
        ).fetchone()

        for x, y in get_coords_from_shape(params.shape):
            if x < 0 or x > picture_size["width"] or y < 0 or y > picture_size["height"]:
                raise errors.InvalidAPIUsage(
                    message="Annotation shape is outside the range of the picture",
                    payload={
                        "details": f"Annotation shape's coordinates should be in pixel, between [0, 0] and [{picture_size['width']}, {picture_size['height']}]",
                        "value": {"x": x, "y": y},
                    },
                )


def get_annotation(conn: psycopg.Connection, id: UUID) -> Optional[Annotation]:
    """Get an annotation in the database"""
    with conn.cursor(row_factory=class_row(Annotation)) as cursor:
        return cursor.execute(
            SQL(
                """SELECT 
    id, 
    shape,
    picture_id,
    t.semantics
    FROM annotations a
    LEFT JOIN (
        SELECT annotation_id, json_agg(json_strip_nulls(json_build_object(
            'key', key,
            'value', value
        )) ORDER BY key, value) AS semantics
        FROM annotations_semantics
        GROUP BY annotation_id
    ) t ON t.annotation_id = a.id
    WHERE a.id = %(id)s"""
            ),
            {"id": id},
        ).fetchone()


def get_picture_annotations(conn: psycopg.Connection, picture_id: UUID) -> List[Annotation]:
    """Get all annotations linked to a picture"""
    with conn.cursor() as cursor:
        json_annotations = cursor.execute(
            SQL("SELECT get_picture_annotations(p.id) FROM pictures p WHERE p.id = %(pic)s"),
            {"pic": picture_id},
        ).fetchone()
        if not json_annotations or not json_annotations[0]:
            return []
        return [Annotation(**a, picture_id=picture_id) for a in json_annotations[0]]


def update_annotation(annotation: Annotation, tag_updates: List[SemanticTagUpdate], account_id: UUID) -> Optional[Annotation]:
    """update an annotation in the database.
    If the annotation has no semantic tags anymore after the update, it will be deleted
    """
    with db.conn(current_app) as conn, conn.transaction(), conn.cursor(row_factory=class_row(Annotation)) as cursor:

        semantics.update_tags(
            cursor=cursor,
            entity=semantics.Entity(semantics.EntityType.annotation, annotation.id),
            actions=tag_updates,
            account=account_id,
            annotation=annotation,
        )

        a = get_annotation(conn, annotation.id)

        if a and len(a.semantics) == 0:
            # the annotation will be deleted by a trigger if its empty
            return None
        return a


def delete_annotation(conn: psycopg.Connection, annotation_id: UUID) -> None:
    """Delete an annotation from the database"""
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM annotations WHERE id = %(id)s", {"id": annotation_id})
