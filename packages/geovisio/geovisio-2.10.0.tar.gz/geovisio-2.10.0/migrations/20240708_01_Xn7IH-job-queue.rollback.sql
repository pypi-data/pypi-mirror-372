-- job_queue
-- depends: 20240625_01_XMZ24-fix-sequence-stat-on-pic-insertion

ALTER TABLE job_history DROP COLUMN job_id;
ALTER TABLE job_history DROP COLUMN upload_set_id;
ALTER TABLE job_history DROP COLUMN sequence_id;
ALTER TABLE job_history DROP COLUMN job_task;

DELETE FROM job_history WHERE picture_id IS NULL; -- remove new style job history
ALTER TABLE job_history ALTER COLUMN picture_id SET NOT NULL;

DROP VIEW pictures_to_process;
DROP TABLE job_queue;
DROP TYPE job_type;


-- put back old table
CREATE TABLE pictures_to_process(
	picture_id UUID PRIMARY KEY,
	ts TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    task picture_process_task DEFAULT 'prepare',
    nb_errors INT NOT NULL DEFAULT 0
);
ALTER TABLE pictures_to_process ADD CONSTRAINT picture_id_fk FOREIGN KEY (picture_id) REFERENCES pictures (id);

CREATE INDEX pictures_to_process_nb_errors_ts_idx ON pictures_to_process(nb_errors, ts);

CREATE INDEX pictures_to_process_ts_idx ON pictures_to_process(ts);

DROP TRIGGER upload_sets_completion_trg ON upload_sets;
DROP COLLATION numeric_file_names;