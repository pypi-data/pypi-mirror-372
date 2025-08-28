from enum import Enum
from dataclasses import dataclass, field
from typing import Any, List, Generic, TypeVar, Protocol
from psycopg import sql
from geovisio import errors
from gettext import gettext as _


@dataclass
class FieldMapping:
    """Represent the mapping between a STAC field and a column in the database"""

    sql_column: sql.SQL
    stac: str

    @property
    def sql_filter(self, row_alias="s.") -> sql.Composable:
        return sql.SQL(row_alias + "{}").format(self.sql_column)


class SQLDirection(Enum):
    """Represent the direction in a SQL ORDER BY query"""

    ASC = sql.SQL("ASC")
    DESC = sql.SQL("DESC")


@dataclass
class SortByField:
    field: FieldMapping
    direction: SQLDirection

    def as_sql(self) -> sql.Composable:
        # Note: the column is the stac name, as the real sql column name will be aliased with the stac name in the query
        col = sql.SQL(self.field.stac)  # type: ignore
        return sql.SQL("{column} {dir}").format(column=col, dir=self.direction.value)

    def revert(self) -> sql.Composable:
        col = sql.SQL(self.field.stac)  # type: ignore
        revert_dir = SQLDirection.ASC if self.direction == SQLDirection.DESC else SQLDirection.DESC
        return sql.SQL("{column} {dir}").format(column=col, dir=revert_dir.value)

    def as_non_aliased_sql(self) -> sql.Composable:
        return sql.SQL("{column} {dir}").format(column=self.field.sql_column, dir=self.direction.value)

    def revert_non_aliased_sql(self) -> sql.Composable:
        revert_dir = SQLDirection.ASC if self.direction == SQLDirection.DESC else SQLDirection.DESC
        return sql.SQL("{column} {dir}").format(column=self.field.sql_column, dir=revert_dir.value)

    def as_stac(self) -> str:
        return f"{'+' if self.direction == SQLDirection.ASC else '-'}{self.field.stac}"


@dataclass
class SortBy:
    fields: List[SortByField] = field(default_factory=lambda: [])

    def as_sql(self) -> sql.Composable:
        return sql.SQL(", ").join([f.as_sql() for f in self.fields])

    def revert(self) -> sql.Composable:
        return sql.SQL(", ").join([f.revert() for f in self.fields])

    def as_non_aliased_sql(self) -> sql.Composable:
        return sql.SQL(", ").join([f.as_non_aliased_sql() for f in self.fields])

    def revert_non_aliased_sql(self) -> sql.Composable:
        return sql.SQL(", ").join([f.revert_non_aliased_sql() for f in self.fields])

    def as_stac(self) -> str:
        return ",".join([f.as_stac() for f in self.fields])

    def get_field_index(self, stac_name: str) -> int:
        return next((i for i, f in enumerate(self.fields) if f.field.stac == stac_name))


class Comparable(Protocol):
    """Protocol for annotating comparable types."""

    def __lt__(self, other: Any) -> bool: ...


T = TypeVar("T", bound=Comparable)


@dataclass
class Bounds(Generic[T]):
    """Represent some bounds (min and max) over a generic type"""

    first: T
    last: T


@dataclass
class BBox:
    """Represent a bounding box defined as 2 points"""

    minx: float
    maxx: float
    miny: float
    maxy: float


def parse_relative_heading(value: str) -> int:
    try:
        relHeading = int(value)
        if relHeading < -180 or relHeading > 180:
            raise ValueError()
        return relHeading
    except (ValueError, TypeError):
        raise errors.InvalidAPIUsage(_("Relative heading is not valid, should be an integer in degrees from -180 to 180"), status_code=400)
