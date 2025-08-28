-- conflicts
-- depends: 20240820_01_aB2ZK-exclusion-zones  20240904_01_gFjlV-files-rejection-msg

CREATE TYPE file_rejection_status_new AS ENUM (
    'capture_duplicate',
    'invalid_file',
    'invalid_metadata',
    'other_error'
);

ALTER TABLE files ALTER COLUMN rejection_status TYPE file_rejection_status_new USING rejection_status::text::file_rejection_status_new;
DROP TYPE file_rejection_status;
ALTER TYPE file_rejection_status_new RENAME TO file_rejection_status;