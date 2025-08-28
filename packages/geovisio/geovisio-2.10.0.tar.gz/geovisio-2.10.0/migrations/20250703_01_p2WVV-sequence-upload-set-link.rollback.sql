-- sequence_upload_set_link
-- depends: 20250701_01_kr371-upload-set-semantics

ALTER TABLE sequences DROP COLUMN upload_set_id CASCADE;
