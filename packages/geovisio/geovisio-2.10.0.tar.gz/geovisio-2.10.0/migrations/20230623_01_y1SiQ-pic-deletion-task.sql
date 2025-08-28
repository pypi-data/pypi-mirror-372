-- pic_deletion_task
-- depends: 20230615_01_u7aRf-pic-delete-cascade
ALTER TYPE picture_status
ADD
	VALUE 'waiting-for-delete';

CREATE TYPE picture_process_task AS ENUM (
	'prepare', -- picture needs to be prepared to be published
	'delete' -- picture needs to be deleted
);

ALTER TABLE
	pictures_to_process
ADD
	COLUMN IF NOT EXISTS task picture_process_task DEFAULT 'prepare';

-- we change the trigger that insert all new pictures into the pictures_to_process table
CREATE
OR REPLACE FUNCTION picture_insertion() RETURNS TRIGGER AS $BODY$ BEGIN
	INSERT INTO
		pictures_to_process(picture_id, task)
	VALUES
		(NEW .id, 'prepare');

RETURN NEW;

END;

$BODY$ LANGUAGE plpgsql;

ALTER TABLE
	sequences_pictures DROP CONSTRAINT sequences_pictures_seq_id_fkey,
ADD
	CONSTRAINT sequences_pictures_seq_id_fkey FOREIGN KEY (seq_id) REFERENCES sequences(id) ON
DELETE
	CASCADE;