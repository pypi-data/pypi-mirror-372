-- pic_deletion_task
-- depends: 20230615_01_u7aRf-pic-delete-cascade
UPDATE
	pictures
SET
	status = 'hidden'
WHERE
	status :: text = 'waiting-for-delete';

-- removing waiting-for-delete from picture_status enum
-- Note: PG does not support removing enum values, so we need to rename and replace with the old one
CREATE TYPE picture_status_new AS ENUM (
	'preparing',
	'broken',
	'ready',
	'hidden',
	'waiting-for-process',
	'preparing-derivates',
	'preparing-blur'
);


ALTER TABLE pictures ALTER COLUMN status DROP DEFAULT;
ALTER TABLE pictures ALTER COLUMN status TYPE picture_status_new USING status::text::picture_status_new;
ALTER TABLE pictures ALTER COLUMN status SET DEFAULT 'waiting-for-process';

DROP TYPE picture_status;
ALTER TYPE picture_status_new RENAME TO picture_status;

-- remove all delete task as we don't know how to handle them anymore
DELETE FROM
	pictures_to_process
WHERE
	task = 'delete';

ALTER TABLE
	pictures_to_process DROP COLUMN IF EXISTS task;

DROP TYPE picture_process_task;