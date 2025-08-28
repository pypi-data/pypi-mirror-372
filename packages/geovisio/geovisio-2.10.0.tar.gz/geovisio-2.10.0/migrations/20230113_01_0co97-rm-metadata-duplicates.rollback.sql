-- rm-metadata-duplicates
-- depends: 20221222_01_fsB6f-add-account

UPDATE pictures
SET metadata = metadata || jsonb_build_object('lat', ST_Y(geom), 'lon', ST_X(geom), 'ts', EXTRACT(epoch FROM ts), 'heading', heading);
