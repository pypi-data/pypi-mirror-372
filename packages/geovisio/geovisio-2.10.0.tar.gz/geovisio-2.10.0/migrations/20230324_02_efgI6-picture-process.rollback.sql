-- status
-- depends: 20230324_01_ba9WA-status

ALTER TABLE pictures 
	DROP COLUMN IF EXISTS inserted_at,
	DROP COLUMN IF EXISTS processed_at,
	DROP COLUMN IF EXISTS nb_errors,
	DROP COLUMN IF EXISTS process_error
;

DROP TABLE pictures_to_process;

-- update default from 'waiting-for-process' to 'preparing'
UPDATE pictures SET status = 'preparing' WHERE status = 'waiting-for-process';
ALTER TABLE pictures ALTER COLUMN status SET DEFAULT 'preparing'; 

UPDATE sequences SET status = 'preparing' WHERE status = 'waiting-for-process';
ALTER TABLE sequences ALTER COLUMN status SET DEFAULT 'preparing'; 

DROP FUNCTION picture_insertion CASCADE;
