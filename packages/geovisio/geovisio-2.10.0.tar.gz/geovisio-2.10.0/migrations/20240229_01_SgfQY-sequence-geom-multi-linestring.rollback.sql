-- sequence_geom_multi_linestring
-- depends: 20240220_01_9wZs0-sequence-current-sort


ALTER TABLE sequences 
	ALTER COLUMN geom TYPE GEOMETRY(LineString, 4326),
	DROP COLUMN bbox;
DROP FUNCTION compute_sequence_bbox;

DROP FUNCTION compute_sequence_geom;

-- put back old functions
DROP FUNCTION IF EXISTS pictures_update_geom_sequence CASCADE;
CREATE FUNCTION pictures_update_geom_sequence() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET geom = s.geom
	FROM (
		SELECT seq_id, ST_MakeLine(array_agg(geom)) AS geom
		FROM (
			SELECT sp.seq_id, p.geom
			FROM sequences_pictures sp
			JOIN pictures p ON sp.pic_id = p.id
			WHERE sp.seq_id IN (
				SELECT DISTINCT sequences_pictures.seq_id
				FROM sequences_pictures
				WHERE sequences_pictures.pic_id = NEW.id
			)
			ORDER BY sp.seq_id, sp.rank
		) sp
		GROUP BY seq_id
	) s
	WHERE sequences.id = s.seq_id;
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_update_sequences_geom_trg
AFTER UPDATE OF geom ON pictures
FOR EACH ROW EXECUTE FUNCTION pictures_update_geom_sequence();

DROP FUNCTION IF EXISTS sequences_pictures_delete CASCADE;
CREATE FUNCTION sequences_pictures_delete() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET geom = s.geom
	FROM (
		SELECT seq_id, ST_MakeLine(array_agg(geom)) AS geom
		FROM (
			SELECT sp.seq_id, sp.rank, p.geom
			FROM sequences_pictures sp
			JOIN pictures p ON sp.pic_id = p.id
			WHERE sp.seq_id IN (
				SELECT DISTINCT seq_id
				FROM old_table
			)
			ORDER BY sp.seq_id, sp.rank
		) sp
		GROUP BY seq_id
	) s
	WHERE sequences.id = s.seq_id;
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER sequences_pictures_delete_trg
AFTER DELETE ON sequences_pictures
REFERENCING OLD TABLE AS old_table
FOR EACH STATEMENT EXECUTE FUNCTION sequences_pictures_delete();
