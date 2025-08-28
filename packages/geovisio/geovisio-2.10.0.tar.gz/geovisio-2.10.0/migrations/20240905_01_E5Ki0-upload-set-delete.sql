-- upload_set_delete
-- depends: 20240801_01_DOqmf-reports  20240813_01_T1XkO-sequences-geom-splits


-- on upload set deletion, we remove the link to the pictures (and the handles will mark the pictures as to be deleted, and will be deleted by the workers)
ALTER TABLE upload_sets
ADD COLUMN IF NOT EXISTS deleted BOOLEAN DEFAULT FALSE;

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