-- timestamps
-- depends: 20230425_01_gYP77-pictures-edits-triggers

-- Remove trigger & function
DROP FUNCTION IF EXISTS sequences_update_ts CASCADE;

-- Remove timestamps for sequences
ALTER TABLE sequences
DROP COLUMN inserted_at,
DROP COLUMN updated_at;
