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
			MAX(p.ts) AS max_picture_ts,
			COUNT(p.*) AS nb_pictures
		FROM sequences_pictures sp
		JOIN pictures p ON sp.pic_id = p.id
		JOIN sequences s ON sp.seq_id = s.id
		WHERE sp.seq_id IN (
				SELECT DISTINCT(seq_id) FROM old_table
			) AND s.status <> 'deleted'
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


DROP TRIGGER update_sequence_nb_pics_on_sequences_pictures_deletion_trigger ON sequences_pictures;
