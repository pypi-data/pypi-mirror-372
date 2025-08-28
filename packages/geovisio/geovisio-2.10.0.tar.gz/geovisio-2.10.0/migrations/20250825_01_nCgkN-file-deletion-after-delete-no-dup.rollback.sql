-- file_deletion_after_delete_no_dup
-- depends: 20250728_01_2zgur-upload-set-relative-heading

DROP FUNCTION IF EXISTS ask_for_all_file_deletion_after_delete CASCADE;

CREATE FUNCTION ask_for_all_file_deletion_after_delete() RETURNS trigger AS $$
BEGIN
    INSERT INTO job_queue(picture_to_delete_id, task)
    SELECT p.id, 'delete' FROM deleted_pictures p;
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER ask_for_all_file_deletion_after_delete_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH STATEMENT
EXECUTE FUNCTION ask_for_all_file_deletion_after_delete();

ALTER TABLE job_queue DROP CONSTRAINT picture_to_delete_id_unique;
