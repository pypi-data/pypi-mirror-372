-- delete_upload_set_on_last_picture_trg_statement
-- depends: 20241128_01_ugthx-job-queue-args

--put back old trigger

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
        DELETE FROM upload_sets WHERE id = OLD.upload_set_id;
    END IF;
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER delete_upload_set_on_last_picture_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH ROW 
EXECUTE FUNCTION delete_upload_set_on_last_picture();