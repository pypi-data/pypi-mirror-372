-- file_deletion_after_delete_no_dup
-- depends: 20250728_01_2zgur-upload-set-relative-heading

-- We do not want to have several deletion jobs for a same picture
-- so we add a constraint to the job_queue table, and handle this in the trigger that ask for file deletion on picture's row deletion.

ALTER TABLE job_queue ADD CONSTRAINT picture_to_delete_id_unique UNIQUE (picture_to_delete_id);

DROP FUNCTION IF EXISTS ask_for_all_file_deletion_after_delete CASCADE;
CREATE FUNCTION ask_for_all_file_deletion_after_delete() RETURNS trigger AS $$
BEGIN
    INSERT INTO job_queue(picture_to_delete_id, task)
    SELECT p.id, 'delete' FROM deleted_pictures p 
    ON CONFLICT (picture_to_delete_id) DO NOTHING
    ;
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER ask_for_all_file_deletion_after_delete_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH STATEMENT
EXECUTE FUNCTION ask_for_all_file_deletion_after_delete();


