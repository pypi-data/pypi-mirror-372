-- annotation_semantics
-- depends: 20250109_01_4OOP4-pages  20250114_01_ABaaL-collaborative-metadata-editing

-- Annotation semantics will be stored in the pictures_semantics table (just with an additional annotation_id in the json)
-- This way if an annotation is deleted, we keep the history easily
CREATE TABLE annotations_semantics_history (
   annotation_id UUID NOT NULL REFERENCES annotations(id),
   account_id UUID REFERENCES accounts(id),
   ts TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
   updates JSONB NOT NULL
);
-- add indexes on history tables
DROP INDEX pictures_semantics_history_picture_id_idx;
DROP INDEX sequences_semantics_history_sequence_id_idx;
