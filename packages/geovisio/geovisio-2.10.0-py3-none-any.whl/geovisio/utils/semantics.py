from ast import Dict
from collections import defaultdict
from dataclasses import dataclass
import re
from uuid import UUID
from psycopg import Connection, Cursor
from psycopg.sql import SQL, Identifier, Placeholder
from psycopg.types.json import Jsonb
from psycopg.errors import UniqueViolation
from psycopg.rows import dict_row
from typing import Generator, List, Optional
from enum import Enum

from geovisio import errors
from geovisio.utils.annotations import Annotation, get_picture_annotations
from geovisio.utils.pic_shape import Geometry
from geovisio.utils.tags import SemanticTag, SemanticTagUpdate, TagAction


class EntityType(Enum):

    pic = "picture_id"
    seq = "sequence_id"
    annotation = "annotation_id"
    upload_set = "upload_set_id"


@dataclass
class Entity:
    type: EntityType
    id: UUID

    def get_table(self) -> Identifier:
        match self.type:
            case EntityType.pic:
                return Identifier("pictures_semantics")
            case EntityType.seq:
                return Identifier("sequences_semantics")
            case EntityType.annotation:
                return Identifier("annotations_semantics")
            case EntityType.upload_set:
                return Identifier("upload_sets_semantics")
            case _:
                raise ValueError(f"Unknown entity type: {self.type}")

    def get_history_table(self) -> Optional[Identifier]:
        match self.type:
            case EntityType.pic:
                return Identifier("pictures_semantics_history")
            case EntityType.seq:
                return Identifier("sequences_semantics_history")
            case EntityType.annotation:
                return Identifier("pictures_semantics_history")
            case EntityType.upload_set:
                return None
            case _:
                raise ValueError(f"Unknown entity type: {self.type}")


def update_tags(cursor: Cursor, entity: Entity, actions: List[SemanticTagUpdate], account: UUID, annotation=None):
    """Update tags for an entity
    Note: this should be done inside an autocommit transaction
    """
    table_name = entity.get_table()
    tag_to_add = [t for t in actions if t.action == TagAction.add]
    tag_to_delete = [t for t in actions if t.action == TagAction.delete]
    try:
        if tag_to_delete:
            filter_query = []
            params = [entity.id]
            for tag in tag_to_delete:
                filter_query.append(SQL("(key = %s AND value = %s)"))
                params.append(tag.key)
                params.append(tag.value)

            cursor.execute(
                SQL(
                    """DELETE FROM {table}
WHERE {entity_id} = %s 
AND ({filter})"""
                ).format(table=table_name, entity_id=Identifier(entity.type.value), filter=SQL(" OR ").join(filter_query)),
                params,
            )
        if tag_to_add:
            fields = [Identifier(entity.type.value), Identifier("key"), Identifier("value")]
            if entity.type == EntityType.upload_set:
                # upload_set semantics have no history, the account is directly stored in the table
                fields.append(Identifier("account_id"))

            with cursor.copy(
                SQL("COPY {table} ({fields}) FROM STDIN").format(
                    table=table_name,
                    fields=SQL(",").join(fields),
                )
            ) as copy:
                for tag in tag_to_add:
                    row = [entity.id, tag.key, tag.value]
                    if entity.type == EntityType.upload_set:
                        row.append(account)
                    copy.write_row(row)
        if tag_to_delete and entity.type == EntityType.annotation and not tag_to_add:
            # if tags have been deleted, we check if some annotations are now empty and need to be deleted
            cursor.execute(
                """DELETE FROM annotations
WHERE id  = %(annotation_id)s AND 
(
    SELECT count(*) AS nb_semantics 
    FROM annotations_semantics 
    WHERE annotation_id = %(annotation_id)s
) = 0""",
                {"annotation_id": entity.id},
            )
        if tag_to_add or tag_to_delete:
            # we track the history changes of the semantic tags
            track_semantic_history(cursor, entity, actions, account, annotation)
    except UniqueViolation as e:
        # if the tag already exists, we don't want to add it again
        raise errors.InvalidAPIUsage(
            "Impossible to add semantic tags because of duplicates", payload={"details": {"duplicate": e.diag.message_detail}}
        )


class SemanticTagUpdateOnAnnotation(SemanticTagUpdate):
    annotation_shape: Geometry


def track_semantic_history(cursor: Cursor, entity: Entity, actions: List[SemanticTagUpdate], account: UUID, annotation):
    history_table = entity.get_history_table()
    if history_table is None:
        # no history for upload_set semantics
        return
    params = {
        "account_id": account,
    }
    if annotation is not None:
        # the annotations are historized in the pictures_semantics_history table
        # and additional information about the annotation.
        # This makes it easier to track annotations deletions
        params["picture_id"] = annotation.picture_id

        params["updates"] = Jsonb(
            [
                SemanticTagUpdateOnAnnotation(action=t.action, key=t.key, value=t.value, annotation_shape=annotation.shape).model_dump()
                for t in actions
            ]
        )
    else:
        params[entity.type.value] = entity.id
        params["updates"] = Jsonb([t.model_dump() for t in actions])

    sql = SQL("INSERT INTO {history_table} ({fields}) VALUES ({values})").format(
        history_table=entity.get_history_table(),
        fields=SQL(", ").join([Identifier(k) for k in params.keys()]),
        values=SQL(", ").join([Placeholder(k) for k in params.keys()]),
    )
    cursor.execute(sql, params)


def delete_annotation_tags_from_service(conn: Connection, picture_id: UUID, service_name: str, account: UUID) -> List[Dict]:
    """Delete all tags from a blurring service on a given picture"""
    annotations_tags = list(get_annotation_tags_from_service(conn, picture_id, service_name))

    with conn.transaction(), conn.cursor(row_factory=dict_row) as cursor:
        for a in annotations_tags:
            actions = [SemanticTagUpdate(action=TagAction.delete, key=t.key, value=t.value) for t in a.semantics]
            entity = Entity(id=a.id, type=EntityType.annotation)
            update_tags(cursor, entity, actions, account, annotation=a)

    return annotations_tags


QUALIFIER_REGEXP = re.compile(r"^(?P<qualifier>[^\[]*)\[(?P<key>[^=]+)(=(?P<value>.*))?\]$")


@dataclass
class QualifierSemantic:
    qualifier: str
    associated_key: str
    associated_value: Optional[str]
    raw_tag: SemanticTag

    def qualifies(self, semantic_tag: SemanticTag) -> bool:
        """Check if a semantic tag is qualified by the qualifier"""
        if semantic_tag.key != self.associated_key:
            return False
        if self.associated_value is None or self.associated_value == "*":
            return True
        return semantic_tag.value == self.associated_value


def as_qualifier(s: SemanticTag) -> Optional[QualifierSemantic]:
    """Try to convert a semantic tag into a qualifier"""
    m = QUALIFIER_REGEXP.search(s.key)
    if m:
        return QualifierSemantic(
            qualifier=m.group("qualifier"),
            associated_key=m.group("key"),
            associated_value=m.group("value"),
            raw_tag=s,
        )


def get_qualifiers(semantics: List[SemanticTag]) -> List[QualifierSemantic]:
    """Find all qualifiers in a list of semantic tags"""
    res = []
    for s in semantics:
        q = as_qualifier(s)
        if q is not None:
            res.append(q)
    return res


def find_detection_model_tags(qualifiers: List[QualifierSemantic], service_name: str) -> List[QualifierSemantic]:
    """Find all detection models associated to a picture, from a given service"""
    res = []
    for q in qualifiers:
        if not q.raw_tag.value.startswith(f"{service_name}-"):
            continue
        if q.qualifier != "detection_model":
            continue
        res.append(q)
    return res


def find_semantics_from_service(annotation, service_name: str) -> Generator[SemanticTag, None, None]:
    """Find all semantics tags related from a given bluring service

    The blurring service will add a `detection_model` qualifier with a value starting by its name (like `SGBlur-yolo11n/0.1.0` for `SGBlur`)

    This method will return all linked semantics tags, and all their qualifiers.
    """
    qualifiers = get_qualifiers(annotation.semantics)
    detection_model_tags = find_detection_model_tags(qualifiers, service_name)
    qualified_tags = []
    for s in annotation.semantics:
        for qualifier_tag in detection_model_tags:
            if qualifier_tag.qualifies(s):
                qualified_tags.append(s)
                break

    # we then have to get all qualifiers on those tags
    related_qualifiers = []
    for q in qualifiers:
        for t in qualified_tags:
            if q.qualifies(t):
                related_qualifiers.append(q.raw_tag)
                break

    return qualified_tags + related_qualifiers


def get_annotation_tags_from_service(conn: Connection, picture_id: UUID, service_name: str) -> Generator[Annotation, None, None]:
    """Get all annotations semantics from a blurring service"""

    annotations = get_picture_annotations(conn, picture_id)

    for a in annotations:
        semantics = [s for s in find_semantics_from_service(a, service_name)]
        yield Annotation(id=a.id, picture_id=a.picture_id, shape=a.shape, semantics=semantics)
