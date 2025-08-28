-- status
-- depends: 20230324_01_ba9WA-status

ALTER TABLE pictures 
	ADD COLUMN IF NOT EXISTS inserted_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ,
	ADD COLUMN IF NOT EXISTS nb_errors INT NOT NULL DEFAULT 0,
	ADD COLUMN IF NOT EXISTS process_error VARCHAR
;

CREATE TABLE pictures_to_process(
	picture_id UUID PRIMARY KEY,
	ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE pictures_to_process ADD CONSTRAINT picture_id_fk FOREIGN KEY (picture_id) REFERENCES pictures (id);

CREATE INDEX pictures_to_process_ts_idx ON pictures_to_process(ts);

-- update default from 'preparing' to 'waiting-for-process'
UPDATE pictures SET status = 'waiting-for-process' WHERE status = 'preparing';
ALTER TABLE pictures ALTER COLUMN status SET DEFAULT 'waiting-for-process'; 

CREATE INDEX pictures_processed_at_idx ON pictures(inserted_at);

UPDATE sequences SET status = 'waiting-for-process' WHERE status = 'preparing';
ALTER TABLE sequences ALTER COLUMN status SET DEFAULT 'waiting-for-process'; 

-- Create Trigger to insert each new picture into pictures_to_process
CREATE OR REPLACE FUNCTION picture_insertion() RETURNS TRIGGER AS
$BODY$
BEGIN
    INSERT INTO
        pictures_to_process(picture_id)
	VALUES 
		(new.id);
	RETURN new;
END;
$BODY$
language plpgsql;

CREATE TRIGGER trigger_process_picture_insertion
     AFTER INSERT ON pictures
     FOR EACH ROW
     EXECUTE PROCEDURE picture_insertion();
