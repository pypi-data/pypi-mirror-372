-- picture_update_index
-- depends: 20250513_01_8WkZC-upload-sets-default-config

ALTER TABLE pictures DROP COLUMN updated_at CASCADE;

DROP TRIGGER pictures_updated_at_on_semantic_insert_trg ON pictures_semantics;
DROP TRIGGER pictures_updated_at_on_semantic_change_trg ON pictures_semantics;
DROP TRIGGER pictures_updated_at_on_semantic_delete_trg ON pictures_semantics;
DROP TRIGGER pictures_updated_at_on_annotation_insert_trg ON annotations_semantics;
DROP TRIGGER pictures_updated_at_on_annotation_change_trg ON annotations_semantics;
DROP TRIGGER a_pictures_updated_at_on_annotation_delete_trg ON annotations_semantics;

DROP TRIGGER pictures_updated_at_on_picture_change_trg ON pictures_changes;

DROP FUNCTION update_pictures_updated_at_on_pictures_change;
DROP FUNCTION update_pictures_updated_at_on_semantics;
DROP FUNCTION update_pictures_updated_at_on_annotation;

-- put back old behavior for sequences's updated_at update

DROP TRIGGER IF EXISTS pictures_updates_on_sequences_trg ON pictures CASCADE;
DROP TRIGGER IF EXISTS pictures_deletes_on_sequences_trg ON pictures CASCADE;

DROP FUNCTION IF EXISTS pictures_updates_on_sequences;
DROP FUNCTION pictures_deletions_updated_at_on_sequences;


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

DROP FUNCTION picture_modification_history CASCADE;
CREATE FUNCTION picture_modification_history() RETURNS TRIGGER AS
$BODY$
DECLARE
    previous_value_changed JSONB;
    parent_sequence_change_id UUID;
BEGIN
    previous_value_changed := jsonb_diff(to_jsonb(OLD), to_jsonb(NEW)) - 'last_account_to_edit' ;

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