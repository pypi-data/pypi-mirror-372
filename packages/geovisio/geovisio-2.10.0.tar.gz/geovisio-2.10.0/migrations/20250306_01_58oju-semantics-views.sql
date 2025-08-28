-- semantics_views
-- depends: 20250123_01_Ececu-tos-acceptance  20250206_01_PjrEL-annotation-semantics

CREATE VIEW sequences_semantics_aggregated AS (
    SELECT sequence_id, json_agg(json_strip_nulls(json_build_object(
                        'key', key,
                        'value', value
                    )) ORDER BY key, value) AS semantics
                    FROM sequences_semantics
                    GROUP BY sequence_id
);

-- This view groups all semantics associated to a picture, so its tags and its annotations tags
CREATE VIEW pictures_semantics_aggregated AS (
   WITH annotation_semantics_as_json AS (
        SELECT picture_id,
        shape,
        id,
        json_agg(json_strip_nulls(json_build_object(
                                'key', key,
                                'value', value
        )) ORDER BY key, value) AS semantics
        FROM annotations a
        LEFT JOIN annotations_semantics s on a.id = s.annotation_id
        GROUP BY a.id
    )
    , aggregated_annotations AS (
        select pictures.id as picture_id,
            json_agg(json_strip_nulls(json_build_object(
                            'id', a.id,
                            'shape', a.shape,
                            'semantics', a.semantics))) AS annotations
            FROM pictures
            LEFT JOIN annotation_semantics_as_json a ON a.picture_id = pictures.id
            GROUP by pictures.id
    )
    , pics_semantics AS (
        select id,
        json_agg(json_strip_nulls(json_build_object(
                            'key', key,
                            'value', value
        )) ORDER BY key, value) AS semantics
        FROM pictures
        LEFT JOIN pictures_semantics ON pictures.id = pictures_semantics.picture_id
        GROUP by pictures.id
    )
    select a.picture_id,
    a.annotations,
    p.semantics
    FROM pics_semantics p
    LEFT JOIN aggregated_annotations a ON a.picture_id = p.id
);
