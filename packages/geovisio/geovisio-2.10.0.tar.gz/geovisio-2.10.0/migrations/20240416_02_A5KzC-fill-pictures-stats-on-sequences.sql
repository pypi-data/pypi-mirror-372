-- fill_pictures_stats_on_sequences
-- depends: 20240416_01_FpyGs-pictures-stats-on-sequences

-- disable triggers on the current transaction, to avoid activating from update triggers only for a populating query
-- (for example we don't want a sequence update_ts to be updated)
SET session_replication_role = replica;

WITH aggregated_pics AS (
	SELECT sp.seq_id AS seq_id,
		MIN(p.ts) AS min_picture_ts,
		MAX(p.ts) AS max_picture_ts,
		COUNT(p.*) AS nb_pictures
	FROM sequences_pictures sp
	JOIN pictures p ON sp.pic_id = p.id
	GROUP BY sp.seq_id
)
UPDATE sequences SET
	min_picture_ts = a.min_picture_ts,
	max_picture_ts = a.max_picture_ts,
	nb_pictures = a.nb_pictures
FROM aggregated_pics a
WHERE sequences.id = seq_id;

-- put back the triggers
SET session_replication_role = DEFAULT;

-- Also add Triggers to maintain those counters

-- On picture insertion (usually do nothing, we want pictures to be ready to count them)
CREATE OR REPLACE FUNCTION update_sequence_on_picture_insertion() RETURNS TRIGGER AS
$BODY$
BEGIN
	UPDATE sequences
	SET 
		nb_pictures = nb_pictures + 1,
		min_picture_ts = LEAST(min_picture_ts, NEW.ts),
		max_picture_ts = GREATEST(max_picture_ts, NEW.ts)
	WHERE id IN (
		SELECT DISTINCT(seq_id) FROM sequences_pictures WHERE pic_id = NEW.id
	);

    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE CONSTRAINT TRIGGER picture_insertion_update_sequence_trigger
    AFTER INSERT ON pictures
    DEFERRABLE INITIALLY DEFERRED -- check at end of transaction for picture to be linked to a sequence
    FOR EACH ROW
    EXECUTE PROCEDURE update_sequence_on_picture_insertion();

-- On picture deletion (don't try to do clever stuff, compute from scratch)
CREATE OR REPLACE FUNCTION update_sequence_on_sequences_pictures_deletion() RETURNS TRIGGER AS
$BODY$
BEGIN
	WITH aggregated_pics AS (
		SELECT sp.seq_id AS seq_id,
			MIN(p.ts) AS min_picture_ts,
			MAX(p.ts) AS max_picture_ts,
			COUNT(p.*) AS nb_pictures
		FROM sequences_pictures sp
		JOIN pictures p ON sp.pic_id = p.id
		WHERE sp.seq_id IN (
				SELECT DISTINCT(seq_id) FROM old_table
			)
		GROUP BY sp.seq_id
	)
	UPDATE sequences SET
		min_picture_ts = a.min_picture_ts,
		max_picture_ts = a.max_picture_ts,
		nb_pictures = a.nb_pictures
	FROM aggregated_pics a
	WHERE sequences.id = seq_id;
    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE TRIGGER seq_picture_deletion_update_sequence_trigger
    AFTER DELETE ON sequences_pictures
	REFERENCING OLD TABLE AS old_table
    FOR EACH STATEMENT -- run this for each statement
    EXECUTE PROCEDURE update_sequence_on_sequences_pictures_deletion();
