-- rejection_status
-- depends: 20240730_01_2BaCy-improve-deletion-triggers


CREATE TYPE file_rejection_status AS ENUM (
    'capture_duplicate',
    'invalid_file',
    'invalid_metadata',
    'other_error'
);

ALTER TABLE files DROP COLUMN rejection_reason;

ALTER TABLE files ADD COLUMN rejection_status file_rejection_status;

CREATE INDEX files_picture_idx ON files(picture_id);
