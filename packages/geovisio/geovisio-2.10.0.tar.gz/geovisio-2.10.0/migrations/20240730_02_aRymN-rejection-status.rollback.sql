-- rejection_status
-- depends: 20240730_01_2BaCy-improve-deletion-triggers

ALTER TABLE files ADD COLUMN rejection_reason VARCHAR;

ALTER TABLE files DROP COLUMN rejection_status;

DROP INDEX files_picture_idx;

DROP TYPE file_rejection_status;