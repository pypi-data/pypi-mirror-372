-- tags_tables
-- depends: 20241224_01_xuN6n-delete-upload-set-on-last-picture-trg-statement

CREATE TABLE annotations (
   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
   picture_id UUID NOT NULL REFERENCES pictures(id) ON DELETE CASCADE,
   shape polygon NOT NULL -- postgres geometry, not postgis.
);

CREATE INDEX annotations_picture_id_idx ON annotations(picture_id);

CREATE TABLE annotations_semantics (
   annotation_id UUID NOT NULL REFERENCES annotations(id) ON DELETE CASCADE,
   key TEXT NOT NULL,
   value TEXT NOT NULL,
   PRIMARY KEY (annotation_id, key, value)
);

CREATE INDEX annotations_semantics_annotation_id_idx ON annotations_semantics(annotation_id);

CREATE TABLE sequences_semantics (
   sequence_id UUID NOT NULL References sequences(id) ON DELETE CASCADE,
   key TEXT NOT NULL,
   value TEXT NOT NULL,
   PRIMARY KEY (sequence_id, key, value)
);

CREATE INDEX sequences_semantics_sequence_id_idx ON sequences_semantics(sequence_id);

CREATE TABLE pictures_semantics (
   picture_id UUID NOT NULL References pictures(id) ON DELETE CASCADE,
   key TEXT NOT NULL,
   value TEXT NOT NULL,
   PRIMARY KEY (picture_id, key, value)
);

CREATE INDEX pictures_semantics_picture_id_idx ON pictures_semantics(picture_id);

-- history tables, one associated to each table
CREATE TABLE annotations_semantics_history (
   annotation_id UUID NOT NULL REFERENCES annotations(id),
   account_id UUID REFERENCES accounts(id),
   ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updates JSONB NOT NULL
);

CREATE TABLE sequences_semantics_history (
   sequence_id UUID NOT NULL References sequences(id),
   account_id UUID REFERENCES accounts(id),
   ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updates JSONB NOT NULL
);
CREATE TABLE pictures_semantics_history (
   picture_id UUID NOT NULL References pictures(id),
   account_id UUID REFERENCES accounts(id),
   ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updates JSONB NOT NULL
);
