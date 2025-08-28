-- upload_set files
-- depends: 20240715_01_Hca9V-upload-set-metadata

-- transactional: false

BEGIN;
-- Note: for the moment we only support pictures, but later we might accept more kind of files (like gpx traces, video, ...)
CREATE TYPE file_type AS ENUM (
	'picture'
);

CREATE TABLE files(
    upload_set_id UUID NOT NULL REFERENCES upload_sets(id) ON DELETE CASCADE,
    picture_id UUID REFERENCES pictures(id) ON DELETE CASCADE, -- some files might not be associated to a picture
    inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    file_type file_type NOT NULL,
    size INT NOT NULL,
    file_name VARCHAR NOT NULL,
    content_md5 UUID NOT NULL,
    rejection_reason VARCHAR
);

-- We consider that the file_name should be unique for a given upload_set, this way we can detect if an upload is an update of an existing file
CREATE UNIQUE INDEX files_upload_set_name_idx ON files(upload_set_id, file_name);

COMMIT;

-- also add an index on upload_set_id for the pictures table
CREATE INDEX CONCURRENTLY pictures_upload_set_idx ON pictures(upload_set_id);