-- initial schema
-- depends: 


--
-- Script for database setup
--

CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;


-- Pictures
CREATE TYPE picture_status AS ENUM (
	'preparing',         -- Default state
	'broken',           -- State when an error occured during import/blurring
	'ready',            -- State when picture is ready to serve
	'hidden'            -- State when admin disabled picture
);

CREATE TABLE pictures(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	file_path VARCHAR NOT NULL,    -- Relative to instance storage path
	status picture_status NOT NULL DEFAULT 'preparing',
	ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	heading INT,
	metadata JSONB,
	geom GEOMETRY(Point, 4326) NOT NULL
);

CREATE INDEX pictures_geom_idx ON pictures USING GIST(geom);
CREATE INDEX pictures_status_idx ON pictures(status);

-- Sequences
CREATE TYPE sequence_status AS ENUM (
	'preparing',         -- Default state
	'broken',           -- State when an error occured during import
	'ready',            -- State when sequence is ready to serve
	'hidden'            -- State when admin disabled sequence
);

CREATE TABLE sequences(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	folder_path VARCHAR NOT NULL,
	status sequence_status NOT NULL DEFAULT 'preparing',
	metadata JSONB,
	geom GEOMETRY(LineString, 4326)
);

CREATE INDEX sequences_geom_idx ON sequences USING GIST(geom);
CREATE INDEX sequences_status_idx ON sequences(status);
CREATE INDEX sequences_folder_path_idx ON sequences(folder_path);

-- Link between pictures and sequences
CREATE TABLE sequences_pictures(
	seq_id UUID NOT NULL REFERENCES sequences(id),
	rank BIGINT NOT NULL,
	pic_id UUID NOT NULL REFERENCES pictures(id),
	PRIMARY KEY (seq_id, rank)
);

CREATE INDEX sequences_pictures_pic_id_idx ON sequences_pictures(pic_id);

-- Link between sequences
CREATE TABLE next_sequences(
	seq_id UUID NOT NULL REFERENCES sequences(id),
	rank INT NOT NULL,
	next_seq_id UUID NOT NULL REFERENCES sequences(id),
	PRIMARY KEY (seq_id, rank)
);
