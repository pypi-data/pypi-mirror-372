-- sequence_upload_set_link
-- depends: 20250701_01_kr371-upload-set-semantics

ALTER TABLE sequences ADD COLUMN upload_set_id UUID REFERENCES upload_sets(id) ON DELETE SET NULL;
