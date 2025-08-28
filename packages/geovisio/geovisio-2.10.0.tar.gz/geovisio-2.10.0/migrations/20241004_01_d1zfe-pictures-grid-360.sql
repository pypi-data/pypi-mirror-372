-- pictures_grid_360
-- depends: 20240912_01_dAALm-account-index

DROP MATERIALIZED VIEW IF EXISTS pictures_grid;

--only consider public pictures in this view and count 360° pictures
CREATE MATERIALIZED VIEW pictures_grid AS
SELECT
    row_number() over () as id,
    count(*) as nb_pictures,
    count(*) FILTER (WHERE p.metadata->>'type' = 'equirectangular') as nb_360_pictures,
    g.geom
FROM
    ST_SquareGrid(
        0.1,
        ST_SetSRID(ST_EstimatedExtent('public', 'pictures', 'geom'), 4326)
    ) AS g
JOIN pictures AS p ON p.geom && g.geom
JOIN sequences_pictures sp on sp.pic_id = p.id
JOIN sequences s ON s.id = sp.seq_id
WHERE p.status = 'ready' and s.status = 'ready'
GROUP BY g.geom;

CREATE UNIQUE INDEX ON pictures_grid(id);
