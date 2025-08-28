-- job_queue
-- depends: 20240625_01_XMZ24-fix-sequence-stat-on-pic-insertion

CREATE TYPE job_type AS ENUM (
	'prepare', -- picture needs to be prepared to be published
	'delete', -- picture needs to be deleted
	'dispatch', -- upload set needs to be dispatched into several collections
	'finalize' -- finalize a collection
);

CREATE TABLE job_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- job can be linked to either a picture, an upload set or a sequence
    picture_id UUID REFERENCES pictures(id) ON DELETE CASCADE,
    upload_set_id UUID REFERENCES upload_sets(id) ON DELETE CASCADE,
    sequence_id UUID REFERENCES sequences(id) ON DELETE CASCADE,

	ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- If not null, this job will not be done before this timestamp
	to_do_after_ts TIMESTAMPTZ,

    nb_errors INT NOT NULL DEFAULT 0,

    task job_type NOT NULL,

	CONSTRAINT picture_id_unique UNIQUE (picture_id),
	CONSTRAINT upload_set_id_unique UNIQUE (upload_set_id),
	CONSTRAINT sequence_id_unique UNIQUE (sequence_id) 
);

-- Add a constraint to ensure that one and only one of the three foreign keys is set
ALTER TABLE job_queue
ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id) = 1);

CREATE INDEX job_queue_nb_errors_ts_idx ON job_queue(nb_errors, ts);

-- this index is used to handle a 'ON CONFLICT' clause in the collection delete
CREATE INDEX job_queue_picture_id_idx ON job_queue(picture_id);

INSERT INTO job_queue (picture_id, ts, task, nb_errors)
SELECT 
    picture_id, 
    ts, 
    case WHEN task = 'delete' THEN 'delete'::job_type ELSE 'prepare'::job_type END, 
    nb_errors
FROM pictures_to_process;

DROP TABLE pictures_to_process CASCADE;

CREATE VIEW pictures_to_process AS (
    SELECT picture_id, ts, task, nb_errors FROM job_queue WHERE task IN ('prepare', 'delete')
);

-- we change the trigger that insert all new pictures into the pictures_to_process table
CREATE
OR REPLACE FUNCTION picture_insertion() RETURNS TRIGGER AS $BODY$ BEGIN
	INSERT INTO
		job_queue(picture_id, task)
	VALUES
		(NEW.id, 'prepare');
    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

-- Link the job_history table to the new job_queue table

ALTER TABLE job_history ADD COLUMN job_id UUID; -- do not add a foreign key constraint yet since the job is only temporarily in the job_queue and cannot add non nullity for old history
ALTER TABLE job_history ADD COLUMN upload_set_id UUID REFERENCES upload_sets(id) ON DELETE CASCADE;
ALTER TABLE job_history ADD COLUMN sequence_id UUID REFERENCES sequences(id) ON DELETE CASCADE;

ALTER TABLE job_history ADD COLUMN job_task job_type NOT NULL DEFAULT 'prepare';
ALTER TABLE job_history ALTER COLUMN picture_id DROP NOT NULL;
ALTER TABLE job_history
ADD CONSTRAINT one_external_id CHECK (num_nonnulls(picture_id, upload_set_id, sequence_id) = 1);

UPDATE job_history SET job_task = case WHEN task = 'delete' THEN 'delete'::job_type ELSE 'prepare'::job_type END where job_task IS NULL;


CREATE INDEX job_history_upload_set_id_idx ON job_history(upload_set_id);
CREATE INDEX job_history_sequence_id_idx ON job_history(sequence_id);

-- add a trigger on upload_set completion to dispatch it
CREATE
OR REPLACE FUNCTION upload_set_completion() RETURNS TRIGGER AS $BODY$ BEGIN

    IF NEW.completed THEN
        INSERT INTO
            job_queue(upload_set_id, task)
        VALUES
            (NEW.id, 'dispatch')
        ON CONFLICT (upload_set_id) DO UPDATE SET ts = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$BODY$ LANGUAGE plpgsql;

CREATE TRIGGER upload_sets_completion_trg
AFTER UPDATE OF completed ON upload_sets
FOR EACH ROW EXECUTE FUNCTION upload_set_completion();

-- Create a collation to sort file names using natural sort (with numbers mixed with letters)
CREATE COLLATION numeric_file_names (provider = icu, locale = 'en@colNumeric=yes'); 