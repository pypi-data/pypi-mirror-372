from typing import Any, Dict, List
from pydantic import BaseModel
from psycopg.sql import SQL, Identifier, Placeholder, Composed
from psycopg.types.json import Jsonb


class ParamsAndValues:
    """Simple wrapper used to help building a query with the right psycopg types"""

    params_as_dict: Dict[str, Any]

    def __init__(self, model: BaseModel, jsonb_fields=set(), **kwargs):
        self.params_as_dict = model.model_dump(exclude_none=True) | kwargs

        for k, v in self.params_as_dict.items():
            if isinstance(v, Dict) or k in jsonb_fields:
                self.params_as_dict[k] = Jsonb(v)  # convert dict to jsonb in database

    def has_updates(self):
        return bool(self.params_as_dict)

    def fields(self) -> Composed:
        """Get the database fields identifiers"""
        return SQL(", ").join([Identifier(f) for f in self.params_as_dict.keys()])

    def placeholders(self) -> Composed:
        """Get the placeholders for the query"""
        return SQL(", ").join([Placeholder(f) for f in self.params_as_dict.keys()])

    def fields_for_set(self) -> Composed:
        """Get the fields and the placeholders formatted for an update query like:
        '"a" = %(a)s, "b" = %(b)s'

        Can be used directly with a query like:
        ```python
        SQL("UPDATE some_table SET {fields}").format(fields=fields)
        ```
        """
        return SQL(", ").join(self.fields_for_set_list())

    def fields_for_set_list(self) -> List[Composed]:
        """Get the fields and the placeholders formatted for an update query like:
        ['"a" = %(a)s', '"b" = %(b)s']

        Note that the returned list should be joined with SQL(", ").join()
        """
        return [SQL("{f} = {p}").format(f=Identifier(f), p=Placeholder(f)) for f in self.params_as_dict.keys()]


def get_db_params_and_values(model: BaseModel, **kwargs):
    """Get a simple wrapper to help building a query with the right psycopg types

    check the unit tests in test_model_query.py for examples
    """
    return ParamsAndValues(model, **kwargs)
