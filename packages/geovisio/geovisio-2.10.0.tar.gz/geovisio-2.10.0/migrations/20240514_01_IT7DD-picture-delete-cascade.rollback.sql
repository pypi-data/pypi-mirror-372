-- picture_delete_cascade
-- depends: 20240507_02_dzVET-picture-grid-public


-- only recompute sequences shape for non deleted sequences
CREATE OR REPLACE FUNCTION sequences_pictures_delete() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET
		geom = compute_sequence_geom(id),
		bbox = compute_sequence_bbox(id)
	WHERE id IN (SELECT DISTINCT seq_id FROM old_table);

	RETURN NULL;
END $$ LANGUAGE plpgsql;

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
