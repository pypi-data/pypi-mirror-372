-- collaborative_metadata_editing
-- depends: 20250102_01_EElhA-rm-cameras  20250107_01_EQN9v-tags-tables


ALTER TABLE accounts ADD COLUMN collaborative_metadata BOOLEAN;
COMMENT ON COLUMN accounts.collaborative_metadata IS 'If true, all sequences will be, by default, editable by all users';

CREATE TABLE configurations (
    onerow_id bool PRIMARY KEY DEFAULT true, -- add a boolean primary key, always true, making it impossible to have more than one row in this configuration table
    collaborative_metadata BOOLEAN, -- Note: it's important for the configurations not to have a default value, to know if it was set by the admin or not

    CONSTRAINT onerow_uni CHECK (onerow_id)
);

-- Add one empty value for the configuration
INSERT INTO configurations (collaborative_metadata) VALUES (null);