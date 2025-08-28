-- sequences-account
-- depends: 20230117_01_K71Pd-pictures-ts-index

-- Drop account column on sequences
ALTER TABLE sequences DROP COLUMN account_id;
