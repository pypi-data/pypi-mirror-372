-- deleted_tag
-- depends: 20231121_01_v6oBF-more-specific-triggers

-- since PG does not support removing values from enum, we create a new sequence status with old values

CREATE TYPE sequence_status_new AS ENUM (
	'preparing',
	'broken',
	'ready',
	'hidden',
	'waiting-for-process'
);

alter table sequences ALTER COLUMN status DROP DEFAULT;
alter table sequences ALTER COLUMN status TYPE sequence_status_new USING status::text::sequence_status_new;
alter table sequences ALTER COLUMN status SET DEFAULT 'waiting-for-process';

DROP TYPE sequence_status;
ALTER TYPE sequence_status_new RENAME TO sequence_status;
