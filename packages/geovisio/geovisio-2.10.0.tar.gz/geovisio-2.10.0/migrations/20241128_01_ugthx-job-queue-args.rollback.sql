-- job_queue_args
-- depends: 20241017_01_GuOjF-pic-quality-update  20241104_01_yhRVu-rejection-details

ALTER TABLE job_queue DROP COLUMN args;
ALTER TABLE job_history DROP COLUMN args;

-- put trigger as old value
DROP TRIGGER trigger_process_picture_insertion ON pictures;

CREATE OR REPLACE FUNCTION picture_insertion() RETURNS TRIGGER AS
$BODY$
BEGIN
    INSERT INTO
        pictures_to_process(picture_id)
	VALUES 
		(new.id);
	RETURN new;
END;
$BODY$
language plpgsql;

CREATE TRIGGER trigger_process_picture_insertion
     AFTER INSERT ON pictures
     FOR EACH ROW
     EXECUTE PROCEDURE picture_insertion();
