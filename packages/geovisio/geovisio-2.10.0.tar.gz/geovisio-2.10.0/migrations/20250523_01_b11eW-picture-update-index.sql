-- picture_update_index
-- depends: 20250513_01_8WkZC-upload-sets-default-config

-- Add a `updated_at` column to pictures and all the necessary triggers to make it up to date
-- Note that this should only encompass user's changes  (so update to the history table (pictures_change) + semantics (and annotations))

ALTER TABLE pictures ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE FUNCTION update_pictures_updated_at_on_pictures_change() RETURNS trigger AS $$
BEGIN
	UPDATE pictures
	SET updated_at = current_timestamp
	WHERE id IN (
		SELECT DISTINCT picture_id
		FROM pictures_change_after
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_updated_at_on_picture_change_trg
AFTER INSERT ON pictures_changes
REFERENCING NEW TABLE AS pictures_change_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_pictures_change();

CREATE FUNCTION update_pictures_updated_at_on_semantics() RETURNS trigger AS $$
BEGIN
	UPDATE pictures
	SET updated_at = current_timestamp
	WHERE id IN (
		SELECT DISTINCT picture_id
		FROM pictures_sem_after
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_updated_at_on_semantic_insert_trg
AFTER INSERT ON pictures_semantics
REFERENCING NEW TABLE AS pictures_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_semantics();

CREATE TRIGGER pictures_updated_at_on_semantic_change_trg
AFTER UPDATE ON pictures_semantics
REFERENCING NEW TABLE AS pictures_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_semantics();

CREATE TRIGGER pictures_updated_at_on_semantic_delete_trg
AFTER DELETE ON pictures_semantics
REFERENCING OLD TABLE AS pictures_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_semantics();


CREATE FUNCTION update_pictures_updated_at_on_annotation() RETURNS trigger AS $$
BEGIN
	UPDATE pictures
	SET updated_at = current_timestamp
	WHERE id IN (
		SELECT DISTINCT a.picture_id
		FROM annotation_sem_after s
        JOIN annotations a ON a.id = s.annotation_id
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_updated_at_on_annotation_insert_trg
AFTER INSERT ON annotations_semantics
REFERENCING NEW TABLE AS annotation_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_annotation();

CREATE TRIGGER pictures_updated_at_on_annotation_change_trg
AFTER UPDATE ON annotations_semantics
REFERENCING NEW TABLE AS annotation_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_annotation();

-- Note: this trigger is called a_ because PG call the trigger in alphabetical order, and we want to be called before the `delete_empty_annotation_trg`
-- that deletes the annotation
CREATE TRIGGER a_pictures_updated_at_on_annotation_delete_trg
AFTER DELETE ON annotations_semantics
REFERENCING OLD TABLE AS annotation_sem_after
FOR EACH STATEMENT
EXECUTE FUNCTION update_pictures_updated_at_on_annotation();



-- Drop old triggers updating the sequence 'updated_at' field, now we do this only when a picture 'updated_at' field is updated
DROP FUNCTION IF EXISTS pictures_updates_on_sequences CASCADE;
DROP TRIGGER IF EXISTS pictures_updates_on_sequences_trg ON pictures;

CREATE FUNCTION pictures_updates_on_sequences() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET updated_at = current_timestamp
	WHERE id IN (
		SELECT sp.seq_id
		FROM sequences_pictures sp
        WHERE sp.pic_id = NEW.id
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_updates_on_sequences_trg
AFTER UPDATE OF updated_at ON pictures
FOR EACH ROW
EXECUTE FUNCTION pictures_updates_on_sequences();

-- for deletion use statement level triggers
CREATE FUNCTION pictures_deletions_updated_at_on_sequences() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET updated_at = current_timestamp
	WHERE 
        status != 'deleted' 
        AND id IN (
		SELECT DISTINCT sp.seq_id
		FROM pictures_after p
		JOIN sequences_pictures sp ON sp.pic_id = p.id
	);
	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_deletes_on_sequences_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS pictures_after
FOR EACH STATEMENT
EXECUTE FUNCTION pictures_deletions_updated_at_on_sequences();

-- Also change the picture_changes trigger so that we do not consider the `updated_at` field
DROP FUNCTION picture_modification_history CASCADE;
CREATE FUNCTION picture_modification_history() RETURNS TRIGGER AS
$BODY$
DECLARE
    previous_value_changed JSONB;
    parent_sequence_change_id UUID;
BEGIN
    previous_value_changed := jsonb_diff(to_jsonb(OLD), to_jsonb(NEW)) - 'last_account_to_edit' - 'updated_at';

    -- if there is a sequence modified on the same transaction, we link the picture change to the sequence change.
    IF EXISTS (
        SELECT 1
                FROM information_schema.tables 
                WHERE table_type = 'LOCAL TEMPORARY'
                AND table_name = 'sequence_current_change'
            
    ) THEN
        SELECT change_id FROM sequence_current_change INTO parent_sequence_change_id;
    END IF;

    INSERT INTO pictures_changes (picture_id, account_id, previous_value_changed, sequences_changes_id)
    VALUES (NEW.id, NEW.last_account_to_edit, previous_value_changed, parent_sequence_change_id);

    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE TRIGGER picture_modification_history_trg
AFTER UPDATE OF 
    last_account_to_edit
 ON pictures
FOR EACH ROW
EXECUTE PROCEDURE picture_modification_history();
