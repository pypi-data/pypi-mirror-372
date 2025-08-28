-- pictures-grid
-- depends: 20240223_01_LsMHB-remove-binary-fields  20240308_01_aF0Jb-migrate-sequence-geom-multi-linestring

-- it's mandatory for a vaccum analyze to be done to be able to use `ST_EstimatedExtent`

CREATE MATERIALIZED VIEW pictures_grid AS
SELECT
    row_number() over () as id,
    count(*) as nb_pictures,
    g.geom
FROM
    ST_SquareGrid(
        0.1,
        ST_SetSRID(ST_EstimatedExtent('public', 'pictures', 'geom'), 4326)
    ) AS g
JOIN pictures AS p ON p.geom && g.geom
JOIN sequences_pictures sp on sp.pic_id = p.id -- Added otherwise can't init from empty database
GROUP BY g.geom;

CREATE INDEX pictures_grid_id_idx ON pictures_grid(id);
CREATE INDEX pictures_grid_geom_idx ON pictures_grid USING GIST(geom);
