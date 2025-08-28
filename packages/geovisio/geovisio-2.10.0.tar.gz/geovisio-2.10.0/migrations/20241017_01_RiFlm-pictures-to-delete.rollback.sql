-- pictures_to_delete
-- depends: 20240912_01_dAALm-account-index

ALTER TABLE job_queue DROP COLUMN IF EXISTS picture_to_delete_id;
-- ALTER TABLE job_queue DROP CONSTRAINT one_external_id;
ALTER TABLE job_queue ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id) = 1);

ALTER TABLE job_history DROP COLUMN IF EXISTS picture_to_delete_id;
-- ALTER TABLE job_history DROP CONSTRAINT one_external_id;
ALTER TABLE job_history ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id) = 1);

ALTER TABLE pictures
	DROP CONSTRAINT upload_set_fk_id ,
	ADD CONSTRAINT upload_set_fk_id FOREIGN KEY (upload_set_id) REFERENCES upload_sets(id);

ALTER TABLE upload_sets
ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE;

DROP TRIGGER ask_for_all_file_deletion_after_delete_trg ON pictures;

DROP FUNCTION IF EXISTS delete_upload_set_on_last_picture CASCADE;
CREATE FUNCTION delete_upload_set_on_last_picture() RETURNS trigger AS $$
BEGIN
    IF OLD.upload_set_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 
            FROM pictures 
            WHERE upload_set_id = OLD.upload_set_id AND id != OLD.id
            AND status != 'waiting-for-delete'
            LIMIT 1
        ) THEN
        -- if it's the last picture of an upload set, we delete the upload set
        UPDATE upload_sets SET deleted = true WHERE id = OLD.upload_set_id AND not deleted;
        INSERT INTO job_queue AS j (upload_set_id, task)  VALUES (OLD.upload_set_id, 'delete') ON CONFLICT (upload_set_id) DO UPDATE SET task = 'delete' WHERE j.task != 'delete';
    END IF;
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER delete_upload_set_on_last_picture_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH ROW -- a picture is always deleted by the workers, one by one, so it's useless to run this trigger for each statement
EXECUTE FUNCTION delete_upload_set_on_last_picture();