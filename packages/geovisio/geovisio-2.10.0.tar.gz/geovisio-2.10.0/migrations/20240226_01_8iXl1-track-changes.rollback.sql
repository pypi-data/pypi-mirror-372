-- track_changes
-- depends: 20240220_01_9wZs0-sequence-current-sort

DROP TABLE sequences_changes CASCADE;
DROP TABLE pictures_changes CASCADE;

DROP TRIGGER picture_modification_history_trg ON pictures;
DROP TRIGGER sequence_modification_history_trg ON sequences;

DROP FUNCTION IF EXISTS jsonb_diff, get_sequence_diffable_fields, sequence_modification_history, picture_modification_history CASCADE;

ALTER TABLE sequences DROP COLUMN IF EXISTS last_account_to_edit;
ALTER TABLE pictures DROP COLUMN IF EXISTS last_account_to_edit;