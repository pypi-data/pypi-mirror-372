-- delete_upload_set_on_last_picture_trg_statement
-- depends: 20241128_01_ugthx-job-queue-args

-- Change the trigger to run for each statement, so that we run it once when deleting an uploadset 

DROP FUNCTION IF EXISTS delete_upload_set_on_last_picture CASCADE;
CREATE FUNCTION delete_upload_set_on_last_picture() RETURNS trigger AS $$
BEGIN
    WITH upload_sets AS (
        SELECT distinct(upload_set_id)
        FROM deleted_pictures
        WHERE NOT EXISTS (
                SELECT 1 
                FROM pictures p
                WHERE p.upload_set_id = upload_set_id AND p.id NOT in (SELECT id FROM deleted_pictures)
                LIMIT 1
            )
    )
    DELETE FROM upload_sets WHERE id IN (SELECT upload_set_id FROM upload_sets);
    RETURN NULL;

END $$ LANGUAGE plpgsql;

CREATE TRIGGER delete_upload_set_on_last_picture_trg
AFTER DELETE ON pictures
REFERENCING OLD TABLE AS deleted_pictures
FOR EACH STATEMENT
EXECUTE FUNCTION delete_upload_set_on_last_picture();