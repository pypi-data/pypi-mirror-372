-- timestamps
-- depends: 20230425_01_gYP77-pictures-edits-triggers

-- Creation and update timestamps for sequences
ALTER TABLE sequences
ADD COLUMN inserted_at TIMESTAMPTZ DEFAULT current_timestamp,
ADD COLUMN updated_at TIMESTAMPTZ;

-- Trigger for updating sequences last update TS
DROP FUNCTION IF EXISTS sequences_update_ts CASCADE;
CREATE FUNCTION sequences_update_ts() RETURNS trigger AS $$
BEGIN
	NEW.updated_at = current_timestamp;
	RETURN NEW;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER sequences_update_ts_trg
BEFORE UPDATE ON sequences
FOR EACH ROW EXECUTE FUNCTION sequences_update_ts();
