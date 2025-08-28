-- status
-- depends: 20230116_01_9PkjZ-add-oauth-provider  20230130_01_VRIv2-sequences-account

UPDATE pictures SET status = 'preparing' WHERE status::text like 'preparing-' OR status = 'waiting-for-process';
-- Note: PG does not support removing enum values, so we need to rename and replace with another one

CREATE TYPE picture_status_new AS ENUM (
	'preparing',
	'broken',
	'ready',
	'hidden'
);


alter table pictures ALTER COLUMN status DROP DEFAULT;
alter table pictures ALTER COLUMN status TYPE picture_status_new USING status::text::picture_status_new;
alter table pictures ALTER COLUMN status SET DEFAULT 'preparing';
DROP TYPE picture_status;
ALTER TYPE picture_status_new RENAME TO picture_status;


CREATE TYPE sequence_status_new AS ENUM (
	'preparing',
	'broken',
	'ready',
	'hidden'
);


alter table sequences ALTER COLUMN status DROP DEFAULT;
alter table sequences ALTER COLUMN status TYPE sequence_status_new USING status::text::sequence_status_new;
alter table sequences ALTER COLUMN status SET DEFAULT 'preparing';

DROP TYPE sequence_status;
ALTER TYPE sequence_status_new RENAME TO sequence_status;
