-- upload_set
-- depends: 20240514_01_IT7DD-picture-delete-cascade

--transactional: false

BEGIN;

CREATE TYPE upload_set_sort_method AS ENUM (
	'filename_asc',
	'filename_desc',
	'time_asc',
	'time_desc'
);


CREATE TABLE upload_sets(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed BOOLEAN NOT NULL DEFAULT false,
    dispatched BOOLEAN NOT NULL DEFAULT false,
    estimated_nb_files INT,

    sort_method upload_set_sort_method NOT NULL DEFAULT 'time_asc',
    split_time INTERVAL DEFAULT INTERVAL '1 minute',
    duplicate_distance real DEFAULT 1,
    split_distance INT DEFAULT 100,
    duplicate_rotation INT DEFAULT 30,

    title VARCHAR NOT NULL
);

COMMENT ON COLUMN upload_sets.sort_method IS 'Strategy used for sorting your pictures. Either by filename or EXIF time, in ascending or descending order.';
COMMENT ON COLUMN upload_sets.split_distance IS 'Maximum distance between two pictures to be considered in the same sequence (in meters).';
COMMENT ON COLUMN upload_sets.split_time IS 'Maximum time interval between two pictures to be considered in the same sequence.';
COMMENT ON COLUMN upload_sets.duplicate_distance IS 'Maximum distance between two pictures to be considered as duplicates (in meters).';
COMMENT ON COLUMN upload_sets.duplicate_rotation IS 'Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).';

ALTER TABLE pictures ADD COLUMN IF NOT EXISTS upload_set_id UUID;

ALTER TABLE pictures ADD CONSTRAINT upload_set_fk_id FOREIGN KEY (upload_set_id) REFERENCES upload_sets(id) NOT VALID;

COMMIT;

-- The foreign kye constraint is added as invalid first, then validated, since it will allow row updating while validating the constraint
ALTER TABLE pictures VALIDATE CONSTRAINT upload_set_fk_id;
