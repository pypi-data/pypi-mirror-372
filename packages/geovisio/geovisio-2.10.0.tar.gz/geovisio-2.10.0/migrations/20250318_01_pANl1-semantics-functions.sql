-- semantics_functions
-- depends: 20250306_01_58oju-semantics-views

CREATE OR REPLACE FUNCTION get_picture_annotations(pic_id UUID)
RETURNS JSONB AS
$$
    SELECT 
        json_agg(json_strip_nulls(json_build_object(
            'id', a.id,
            'shape', a.shape,
            'semantics', a.semantics
        ))) AS annotations
    FROM (
        SELECT picture_id,
                shape,
                id,
                json_agg(json_strip_nulls(json_build_object(
                    'key', key,
                    'value', value
                )) ORDER BY key, value) AS semantics
        FROM annotations a
        LEFT JOIN annotations_semantics s ON a.id = s.annotation_id
        WHERE a.picture_id = pic_id
        GROUP BY a.id
    ) a
    GROUP BY picture_id;
$$ LANGUAGE sql STABLE PARALLEL SAFE;

CREATE OR REPLACE FUNCTION get_picture_semantics(pic_id UUID)
RETURNS JSONB AS
$$
    SELECT 
        json_agg(json_strip_nulls(json_build_object(
                    'key', key,
                    'value', value
        )) ORDER BY key, value) AS semantics
    FROM pictures
    LEFT JOIN pictures_semantics ON pictures.id = pictures_semantics.picture_id
    where pictures.id = pic_id
    GROUP by pictures.id
$$ LANGUAGE sql STABLE PARALLEL SAFE;