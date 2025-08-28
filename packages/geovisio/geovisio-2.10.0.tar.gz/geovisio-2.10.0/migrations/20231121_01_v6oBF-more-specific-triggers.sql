-- more specific triggers
-- depends: 20231110_01_3p070-jobs-error

-- Add more specific names and conditions on the trigger on pictures


-- This trigger only update the sequence geometry, so we can fire it only on update of geom
DROP TRIGGER pictures_update_sequences_trg ON pictures;

-- The function need to be changed since we now only triggers it from 1 column change, and in the meantime rename the function to a more specific name
-- In the meantime, rename the function to be more specific
DROP FUNCTION IF EXISTS pictures_update_sequence CASCADE;
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

