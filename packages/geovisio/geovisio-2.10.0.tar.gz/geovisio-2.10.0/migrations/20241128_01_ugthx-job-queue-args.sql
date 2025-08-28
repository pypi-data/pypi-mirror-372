-- job_queue_args
-- depends: 20241017_01_GuOjF-pic-quality-update  20241104_01_yhRVu-rejection-details

ALTER TABLE job_queue ADD COLUMN IF NOT EXISTS args JSONB;
ALTER TABLE job_history ADD COLUMN IF NOT EXISTS args JSONB;

-- Update the trigger that insert each new picture into pictures_to_process
-- Now we check if the picture has been blurred before upload, to skip the blurring process
DROP TRIGGER trigger_process_picture_insertion ON pictures;
CREATE OR REPLACE FUNCTION picture_insertion() RETURNS TRIGGER AS
$BODY$
DECLARE
	args JSONB;
BEGIN
    IF new.metadata->>'blurredByAuthor' THEN
        args := jsonb_build_object('skip_blurring', true);
    END IF;

    INSERT INTO
        job_queue(picture_id, task, args)
	VALUES 
		(new.id, 'prepare', args);
	RETURN new;
END;
$BODY$
language plpgsql;

CREATE TRIGGER trigger_process_picture_insertion
     AFTER INSERT ON pictures
     FOR EACH ROW
     EXECUTE PROCEDURE picture_insertion();
