from operator import not_
from lark import UnexpectedCharacters
from geovisio import errors
import logging
from flask_babel import gettext as _
from psycopg import sql
from pygeofilter import ast
from pygeofilter.backends.sql import to_sql_where
from pygeofilter.backends.evaluator import Evaluator, handle
from pygeofilter.parsers.ecql import parse as ecql_parser
from typing import Dict, Optional


def parse_cql2_filter(value: Optional[str], field_mapping: Dict[str, str], *, ast_updater=None) -> Optional[sql.SQL]:
    """Reads CQL2 filter parameter and sends SQL condition back.

    Need a mapping from API field name to database field name.

    And if needed, can take a function to update the AST before sending it to SQL.
    """
    if not value:
        return None
    try:
        filterAst = ecql_parser(value)

        if ast_updater:
            filterAst = ast_updater(filterAst)

        f = to_sql_where(filterAst, field_mapping).replace('"', "").replace("'me'", "%(account_id)s")
        return sql.SQL(f)  # type: ignore
    except:
        logging.error(f"Unsupported filter parameter: {value}")
        raise errors.InvalidAPIUsage(_("Unsupported filter parameter"), status_code=400)


SEMANTIC_FIELD_MAPPOING = {"key": "key", "value": "value"}


def parse_semantic_filter(value: Optional[str]) -> Optional[sql.SQL]:
    """Transform the semantic only filters to SQL

    >>> parse_semantic_filter("semantics.pouet='stop'")
    SQL("((key = 'pouet') AND (value = 'stop'))")
    >>> parse_semantic_filter("\\"semantics.osm|traffic_sign\\"='stop'")
    SQL("((key = 'osm|traffic_sign') AND (value = 'stop'))")
    """
    return parse_cql2_filter(value, SEMANTIC_FIELD_MAPPOING, ast_updater=lambda a: SemanticAttributesAstUpdater().evaluate(a))


def parse_search_filter(value: Optional[str]) -> Optional[sql.SQL]:
    """Transform STAC CQL2 filter on /search endpoint to SQL

    Note that, for the moment, only semantics are supported. If more needs to be supported, we should evaluate the
    non semantic filters separately (likely with a AstEvaluator).
    """
    s = parse_semantic_filter(value)

    if s is None:
        return None

    return sql.SQL(
        """(p.id in (
    SELECT picture_id
    FROM pictures_semantics
    WHERE {semantic_filter}
UNION
    SELECT DISTINCT(picture_id)
    FROM annotations_semantics ans
    JOIN annotations a ON a.id = ans.annotation_id
    WHERE {semantic_filter}
UNION
    SELECT sp.pic_id
    FROM sequences_pictures sp
    JOIN sequences_semantics sm ON sp.seq_id = sm.sequence_id 
    WHERE {semantic_filter}
LIMIT %(limit)s
))"""
    ).format(semantic_filter=s)


def get_semantic_attribute(node):
    if isinstance(node, ast.Attribute) and node.name.startswith("semantics."):
        return node.name[10:]
    return None


class SemanticAttributesAstUpdater(Evaluator):
    """
    We alter the AST to handle semantic attributes.

    So
    * `semantics.some_tag='some_value'` becomes `(key = 'some_tag' AND value = 'some_value')`
    * `semantics.some_tag IN ('some_value', 'some_other_value')` becomes `(key = 'some_tag' AND value IN ('some_value', 'some_other_value'))`
    """

    @handle(ast.Equal)
    def eq(self, node, lhs, rhs):
        semantic_attribute = get_semantic_attribute(lhs)
        if semantic_attribute is None:
            return node
        return ast.And(ast.Equal(ast.Attribute("key"), semantic_attribute), ast.Equal(ast.Attribute("value"), rhs))

    @handle(ast.Or)
    def or_(self, node, lhs, rhs):
        return ast.Or(lhs, rhs)

    @handle(ast.And)
    def and_(self, node, lhs, rhs):
        # uncomment this when we know how to handle `AND` in semantic filters
        # return ast.And(lhs, rhs)
        raise errors.InvalidAPIUsage("Unsupported filter parameter: AND semantic filters are not yet supported", status_code=400)

    @handle(ast.IsNull)
    def is_null(self, node, lhs):
        if not node.not_:
            raise errors.InvalidAPIUsage(
                "Unsupported filter parameter: only `IS NOT NULL` is supported (to express that we want all values of a semantic tags)",
                status_code=400,
            )
        semantic_attribute = get_semantic_attribute(lhs)
        if semantic_attribute is None:
            return node
        return ast.Equal(ast.Attribute("key"), semantic_attribute)

    @handle(ast.In)
    def in_(self, node, lhs, *options):
        semantic_attribute = get_semantic_attribute(lhs)
        if semantic_attribute is None:
            return node

        return ast.And(ast.Equal(ast.Attribute("key"), semantic_attribute), ast.In(ast.Attribute("value"), node.sub_nodes, not_=False))

    def adopt(self, node, *sub_args):
        return node
