-- picture_grid_public
-- depends: 20240507_01_eBfqZ-refresh-table
-- transactional: false

BEGIN;

DROP MATERIALIZED VIEW pictures_grid;

--only consider public pictures in this view
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
JOIN sequences_pictures sp on sp.pic_id = p.id
JOIN sequences s ON s.id = sp.seq_id
WHERE p.status = 'ready' and s.status = 'ready'
GROUP BY g.geom;

COMMIT;
