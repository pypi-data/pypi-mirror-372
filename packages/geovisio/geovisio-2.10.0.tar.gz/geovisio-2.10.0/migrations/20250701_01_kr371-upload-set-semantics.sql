-- upload_set_semantics
-- depends: 20250624_01_SETp6-job-warnings


-- Upload set semantic is just a temporary bag of tags that will be copied into all the upload_set sequences.
-- We also keep the account_id to be able to track who added the tag.
CREATE TABLE upload_sets_semantics (
   upload_set_id UUID NOT NULL References upload_sets(id) ON DELETE CASCADE,
   key TEXT NOT NULL,
   value TEXT NOT NULL,
   account_id UUID REFERENCES accounts(id) ON DELETE SET NULL,
   PRIMARY KEY (upload_set_id, key, value)
);

CREATE INDEX upload_sets_semantics_upload_set_id_idx ON upload_sets_semantics(upload_set_id);
