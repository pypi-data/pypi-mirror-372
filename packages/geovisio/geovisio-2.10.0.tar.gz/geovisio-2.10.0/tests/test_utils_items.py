from geovisio.utils.items import SortBy, ItemSortByField, SortableItemField
from geovisio.utils.fields import SQLDirection
from psycopg.sql import SQL, Identifier


def test_sort_by_to_sql():
    sort_by = SortBy(
        fields=[
            ItemSortByField(field=SortableItemField.updated, direction=SQLDirection.DESC),
            ItemSortByField(field=SortableItemField.id, direction=SQLDirection.ASC),
        ]
    )

    assert sort_by.to_sql().as_string(None) == 'ORDER BY "p"."updated_at" DESC, "p"."id" ASC'


def test_sort_by_distance_to_sql():
    sort_by = SortBy(
        fields=[
            ItemSortByField(field=SortableItemField.distance_to, direction=SQLDirection.DESC, obj_to_compare=SQL("ST_Point(1, 2, 4326)")),
            ItemSortByField(field=SortableItemField.distance_to, direction=SQLDirection.ASC, obj_to_compare=SQL("ST_Point(2, 4, 4326)")),
        ]
    )

    assert (
        sort_by.to_sql(alias=Identifier("pic")).as_string(None)
        == 'ORDER BY "pic"."geom" <-> ST_Point(1, 2, 4326) DESC, "pic"."geom" <-> ST_Point(2, 4, 4326) ASC'
    )
