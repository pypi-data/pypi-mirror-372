-- track_changes
-- depends: 20240220_01_9wZs0-sequence-current-sort

CREATE TABLE sequences_changes(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sequence_id UUID NOT NULL REFERENCES sequences(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,

    -- json will contains all modified keys, with old db values
    previous_value_changed JSONB,

    ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX sequences_changes_seq_id_idx ON sequences_changes(sequence_id);

CREATE TABLE pictures_changes(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    picture_id UUID NOT NULL REFERENCES pictures(id) ON DELETE CASCADE,
    account_id UUID NOT NULL REFERENCES accounts(id) ON DELETE CASCADE,
    -- If the changes is part of global changes on a sequence, id of that change
    sequences_changes_id UUID REFERENCES sequences_changes(id),

    -- json will contains all modified keys, with old db values
    previous_value_changed JSONB,

    ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX pictures_changes_pic_id_idx ON pictures_changes(picture_id);


ALTER TABLE sequences ADD COLUMN IF NOT EXISTS last_account_to_edit UUID;
ALTER TABLE sequences ADD CONSTRAINT last_account_to_edit_fk_id FOREIGN KEY (last_account_to_edit) REFERENCES accounts (id) ON DELETE CASCADE;

ALTER TABLE pictures ADD COLUMN IF NOT EXISTS last_account_to_edit UUID;
ALTER TABLE pictures ADD CONSTRAINT last_account_to_edit_fk_id FOREIGN KEY (last_account_to_edit) REFERENCES accounts (id) ON DELETE CASCADE;

CREATE OR REPLACE FUNCTION jsonb_diff(IN a jsonb, IN b jsonb) RETURNS jsonb AS
$BODY$
    SELECT jsonb_object_agg(key, value)
    FROM (
        SELECT * FROM jsonb_each(to_jsonb(a))
        EXCEPT SELECT * FROM jsonb_each(to_jsonb(b))
    ) as t;
$BODY$
LANGUAGE SQL IMMUTABLE STRICT;

COMMENT ON FUNCTION jsonb_diff IS 'Create a Json with all the key/values that are in the first one and not in the second. Only works for top level fields';

-- We only consider a specified set of fields. If we want to track the history of a new field, a new migration should add them here
-- We also put the metadata fields at the same level in order not to have a nested `metadata` field inside, since it would make comparison more difficult
CREATE OR REPLACE FUNCTION get_sequence_diffable_fields(IN seq sequences) RETURNS jsonb AS
$BODY$
    SELECT jsonb_build_object(
            'status', seq.status, 
            'current_sort', seq.current_sort
        ) || seq.metadata;
$BODY$
LANGUAGE SQL IMMUTABLE STRICT;

COMMENT ON FUNCTION get_sequence_diffable_fields IS 'Short list the sequence fields we want to trank updates for';


-- Create a trigger to track the history of the change
CREATE OR REPLACE FUNCTION sequence_modification_history() RETURNS TRIGGER AS
$BODY$
DECLARE
    previous_value_changed JSONB;
    change_id UUID;
BEGIN
    previous_value_changed := jsonb_diff(get_sequence_diffable_fields(OLD), get_sequence_diffable_fields(NEW));
    
    INSERT INTO sequences_changes (sequence_id, account_id, previous_value_changed)
    VALUES (NEW.id, NEW.last_account_to_edit, previous_value_changed) RETURNING id INTO change_id;

    CREATE TEMP TABLE IF NOT EXISTS sequence_current_change ON COMMIT DROP AS SELECT change_id;

    RETURN NULL;
END;
$BODY$
language plpgsql;

CREATE OR REPLACE FUNCTION picture_modification_history() RETURNS TRIGGER AS
$BODY$
DECLARE
    previous_value_changed JSONB;
    parent_sequence_change_id UUID;
BEGIN
    previous_value_changed := jsonb_diff(to_jsonb(OLD), to_jsonb(NEW)) - 'last_account_to_edit';

    -- if there is a sequence modified on the same transaction, we link the picture change to the sequence change.
    IF EXISTS (
        SELECT 1
                FROM information_schema.tables 
                WHERE table_type = 'LOCAL TEMPORARY'
                AND table_name = 'sequence_current_change'
            
    ) THEN
        SELECT change_id FROM sequence_current_change INTO parent_sequence_change_id;
    END IF;

    INSERT INTO pictures_changes (picture_id, account_id, previous_value_changed, sequences_changes_id)
    VALUES (NEW.id, NEW.last_account_to_edit, previous_value_changed, parent_sequence_change_id);

    RETURN NULL;
END;
$BODY$
language plpgsql;

-- We only trigger this for updates of last_account_to_edit. All changes that needs to be tracked need to set this field.
CREATE TRIGGER sequence_modification_history_trg
AFTER UPDATE OF 
    last_account_to_edit
 ON sequences
FOR EACH ROW
EXECUTE PROCEDURE sequence_modification_history();

CREATE TRIGGER picture_modification_history_trg
AFTER UPDATE OF 
    last_account_to_edit
 ON pictures
FOR EACH ROW
EXECUTE PROCEDURE picture_modification_history();