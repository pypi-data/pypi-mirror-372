-- fix_sequence_stat_on_pic_insertion
-- depends: 20240612_01_yNcuE-upload-set  20240617_01_tKtlx-md5-concurrent-index

-- drop old triggers on insertion on pictures table, we want the trigger to be on sequences_pictures instead

DROP TRIGGER picture_insertion_update_sequence_trigger ON pictures CASCADE;

CREATE OR REPLACE FUNCTION update_sequence_on_picture_insertion() RETURNS TRIGGER AS
$BODY$
BEGIN
    WITH p AS (
        SELECT NEW.seq_id, ts FROM pictures WHERE id = NEW.pic_id
    )
	UPDATE sequences
	SET
		nb_pictures = nb_pictures + 1,
		min_picture_ts = LEAST(min_picture_ts, p.ts),
		max_picture_ts = GREATEST(max_picture_ts, p.ts)
    FROM p
	WHERE id = p.seq_id;

    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE CONSTRAINT TRIGGER sequences_pictures_insertion_update_sequence_trigger
    AFTER INSERT ON sequences_pictures
    DEFERRABLE INITIALLY DEFERRED -- check at end of transaction for picture to be linked to a sequence
    FOR EACH ROW
    EXECUTE PROCEDURE update_sequence_on_picture_insertion();
