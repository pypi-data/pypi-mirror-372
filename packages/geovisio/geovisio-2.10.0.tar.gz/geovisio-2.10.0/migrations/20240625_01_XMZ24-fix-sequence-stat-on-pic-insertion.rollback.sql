-- fix_sequence_stat_on_pic_insertion
-- depends: 20240612_01_yNcuE-upload-set  20240617_01_tKtlx-md5-concurrent-index

-- put back old triggers
DROP TRIGGER sequences_pictures_insertion_update_sequence_trigger ON sequences_pictures CASCADE;

-- DROP TRIGGER picture_insertion_update_sequence_trigger ON pictures CASCADE;
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

