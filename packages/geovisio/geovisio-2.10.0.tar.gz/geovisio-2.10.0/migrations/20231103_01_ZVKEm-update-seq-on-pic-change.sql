-- update_seq_on_pic_change
-- depends: 20231018_01_4G3YE-pictures-exiv2

CREATE FUNCTION pictures_updates_on_sequences() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET updated_at = current_timestamp
	WHERE id IN (
		SELECT DISTINCT sp.seq_id
		FROM pictures_after p
		JOIN sequences_pictures sp ON sp.pic_id = p.id
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_updates_on_sequences_trg
AFTER UPDATE ON pictures
REFERENCING NEW TABLE AS pictures_after
FOR EACH STATEMENT
EXECUTE FUNCTION pictures_updates_on_sequences();

CREATE TRIGGER pictures_deletes_on_sequences_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS pictures_after
FOR EACH STATEMENT
EXECUTE FUNCTION pictures_updates_on_sequences();

CREATE INDEX sequences_updated_at_idx ON sequences(updated_at);