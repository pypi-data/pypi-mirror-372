-- pictures_to_delete
-- depends: 20240912_01_dAALm-account-index

-- Add another column to the job_queue tabel to store the pictures to delete without using a foreign key, 
-- so that we can keep them even after their deletion
ALTER TABLE job_queue DROP CONSTRAINT one_external_id;

ALTER TABLE job_queue ADD COLUMN IF NOT EXISTS picture_to_delete_id UUID;

ALTER TABLE job_queue ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id, picture_to_delete_id) = 1);

ALTER TABLE job_history ADD COLUMN IF NOT EXISTS picture_to_delete_id UUID;
ALTER TABLE job_history DROP CONSTRAINT one_external_id;
ALTER TABLE job_history ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id, picture_to_delete_id) = 1);

-- when an upload set is deleted, all it's pictures are added to the deletion queue, and deleted from the database (since there is a `ON DELETE CASCADE`)

ALTER TABLE pictures
	DROP CONSTRAINT upload_set_fk_id ,
	ADD CONSTRAINT upload_set_fk_id FOREIGN KEY (upload_set_id) REFERENCES upload_sets(id) ON DELETE CASCADE;

-- also update how the last picture trigger the deletion of its upload set
DROP FUNCTION IF EXISTS delete_upload_set_on_last_picture CASCADE;
CREATE FUNCTION delete_upload_set_on_last_picture() RETURNS trigger AS $$
BEGIN
    IF OLD.upload_set_id IS NOT NULL AND NOT EXISTS (
            SELECT 1 
            FROM pictures 
            WHERE upload_set_id = OLD.upload_set_id AND id != OLD.id
            AND status != 'waiting-for-delete' -- Note: this status is deprecated, but we need to consider it anyway since it can remain some pictures with this status in the database for the migration
            LIMIT 1
        ) THEN
        -- if it's the last picture of an upload set, we delete the upload set
        DELETE FROM upload_sets WHERE id = OLD.upload_set_id;
    END IF;
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER delete_upload_set_on_last_picture_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH ROW -- a picture is always deleted by the workers, one by one, so it's useless to run this trigger for each statement
EXECUTE FUNCTION delete_upload_set_on_last_picture();

-- Add to the new queue all pictures marked and waiting for delete and all pictures from deleted upload sets
INSERT INTO job_queue(picture_to_delete_id, task)
SELECT p.id, 'delete' 
FROM pictures p 
LEFT JOIN upload_sets us ON us.id = p.upload_set_id 
WHERE p.status = 'waiting-for-delete' OR us.deleted;

-- cleanup all pictures/uploadset, as we don't need them anymore since they are added to the new deletion queue
DELETE FROM pictures WHERE status = 'waiting-for-delete';
DELETE FROM upload_sets WHERE deleted;

-- the deleted column of upload_sets is now useless, we can delete them right away
ALTER TABLE upload_sets DROP COLUMN deleted;

DROP FUNCTION IF EXISTS ask_for_all_file_deletion_after_delete;
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


