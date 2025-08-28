-- account_index
-- depends: 20240905_01_E5Ki0-upload-set-delete  20240909_01_Muc22-unique-grid-index

CREATE INDEX sequences_account_idx ON sequences(account_id);
