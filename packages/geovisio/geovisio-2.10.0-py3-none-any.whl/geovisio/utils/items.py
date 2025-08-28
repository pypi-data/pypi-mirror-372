from .fields import SQLDirection
from psycopg.sql import SQL, Identifier
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, List


class SortableItemField(Enum):
    ts = Identifier("ts")
    updated = Identifier("updated_at")
    distance_to = ""
    id = Identifier("id")


@dataclass
class ItemSortByField:
    field: SortableItemField
    direction: SQLDirection

    # Note that this obj_to_compare is only used for the `distance_to` field, but we cannot put it in the enum
    obj_to_compare: Optional[SQL] = None

    def to_sql(self, alias) -> SQL:
        sql_order = None
        if self.obj_to_compare:
            if self.field == SortableItemField.distance_to:
                sql_order = SQL('{alias}."geom" <-> {obj_to_compare} {direction}').format(
                    alias=alias, obj_to_compare=self.obj_to_compare, direction=self.direction.value
                )
            else:
                raise InvalidAPIUsage("For the moment only the distance comparison to another item is supported")
        else:
            sql_order = SQL("{alias}.{field} {direction}").format(alias=alias, field=self.field.value, direction=self.direction.value)
        return sql_order


@dataclass
class SortBy:
    fields: List[ItemSortByField] = field(default_factory=lambda: [])

    def to_sql(self, alias=Identifier("p")) -> SQL:
        if len(self.fields) == 0:
            return SQL("")
        return SQL("ORDER BY {fields}").format(fields=SQL(", ").join([f.to_sql(alias=alias) for f in self.fields]))
