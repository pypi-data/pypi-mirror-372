-- improve_deletion_triggers
-- depends: 20240729_01_HALjj-upload-set-sort

-- Change the trigger counting the number of pictures to deleted from a sequences since it was not working
-- we pictures were added and deleted in the same transaction
CREATE OR REPLACE FUNCTION update_sequence_on_sequences_pictures_deletion() RETURNS TRIGGER AS
$BODY$
BEGIN
	WITH aggregated_pics AS (
		SELECT sp.seq_id AS seq_id,
			MIN(p.ts) AS min_picture_ts,
			MAX(p.ts) AS max_picture_ts
		FROM sequences_pictures sp
		JOIN pictures p ON sp.pic_id = p.id
		WHERE sp.seq_id IN (
				SELECT DISTINCT(seq_id) FROM old_table
			)
		GROUP BY sp.seq_id
	)
	UPDATE sequences SET
		min_picture_ts = a.min_picture_ts,
		max_picture_ts = a.max_picture_ts
	FROM aggregated_pics a
	WHERE sequences.id = seq_id;
    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE OR REPLACE FUNCTION update_sequence_nb_pics_on_sequences_pictures_deletion() RETURNS TRIGGER AS
$BODY$
BEGIN
	WITH aggregated_pics AS (
		SELECT
			sp.seq_id AS seq_id,
			COUNT(sp.*) AS nb_removed_pictures
		FROM old_table sp
		GROUP BY sp.seq_id
	)
	UPDATE sequences SET
		nb_pictures = nb_pictures - a.nb_removed_pictures
	FROM aggregated_pics a
	WHERE sequences.id = seq_id;
    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE TRIGGER update_sequence_nb_pics_on_sequences_pictures_deletion_trigger
    AFTER DELETE ON sequences_pictures
	REFERENCING OLD TABLE AS old_table
    FOR EACH STATEMENT -- run this for each statement
    EXECUTE PROCEDURE update_sequence_nb_pics_on_sequences_pictures_deletion();
