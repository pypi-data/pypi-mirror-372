-- annotation_semantics
-- depends: 20250109_01_4OOP4-pages  20250114_01_ABaaL-collaborative-metadata-editing

-- Annotation semantics will be stored in the pictures_semantics table (just with an additional annotation_id in the json)
-- This way if an annotation is deleted, we keep the history easily
DROP TABLE annotations_semantics_history;

-- psycopg doesn't support polygon natively, and polygon might not be enough in the futur, so we use directly jsonb here
ALTER TABLE annotations ALTER COLUMN shape TYPE JSONB USING NULL;

-- add indexes on history tables
CREATE INDEX pictures_semantics_history_picture_id_idx ON pictures_semantics_history(picture_id);
CREATE INDEX sequences_semantics_history_sequence_id_idx ON sequences_semantics_history(sequence_id);

-- ALTER TABLE pictures_semantics_history ADD COLUMN annotation UUID REFERENCES annotations(id);
