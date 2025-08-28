-- jobs_error
-- depends: 20231103_01_ZVKEm-update-seq-on-pic-change
-- transactional: false
-- Note: this migration is not in a transaction, since the transactions will be created inside it to update the `pictures` table (which can be very big) in batches


-- Add a job_history tables to log all async jobs
-- Note: error replace `pictures.process_error` and `pictures_to_process.nb_errors` replace `pictures.nb_errors`
-- Those fields are note removed right away for a smooth database migration transition, but should be removed afterward


CREATE TABLE job_history(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	picture_id UUID NOT NULL REFERENCES pictures(id) ON DELETE CASCADE,
	task picture_process_task,
	started_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
	finished_at TIMESTAMPTZ,
	error VARCHAR
);



CREATE INDEX job_history_picture_id_idx ON job_history(picture_id);

ALTER TABLE pictures_to_process ADD COLUMN nb_errors INT NOT NULL DEFAULT 0;

CREATE INDEX pictures_to_process_nb_errors_ts_idx ON pictures_to_process(nb_errors, ts);

CREATE TYPE picture_preparing_status AS ENUM (
	'not-processed',  -- Default state, the picture has not been processed yet
	'prepared',  -- State when the picture has been correctly prepared
	'broken' -- State when the picture has not been correctly processed
);

ALTER TABLE pictures ADD COLUMN preparing_status picture_preparing_status NOT NULL DEFAULT 'not-processed';

CREATE OR REPLACE PROCEDURE update_all_pictures_preparing_status() AS
$$
DECLARE
   last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM pictures INTO last_inserted_at;

	WHILE last_inserted_at IS NOT NULL LOOP
		
		-- remove triggers on picture before updating the table
		DROP TRIGGER pictures_update_sequences_trg ON pictures;
		DROP TRIGGER pictures_updates_on_sequences_trg ON pictures;

		WITH 
			pic_to_update AS (
				SELECT id, inserted_at from pictures where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 100000
			)
			, updated_pic AS (
				-- Populate table with values based on the `status` column
				UPDATE pictures
					SET preparing_status =
						CASE
							WHEN status IN ('hidden', 'ready') THEN 'prepared'::picture_preparing_status
							WHEN status = 'broken' THEN 'broken'::picture_preparing_status
							ELSE 'not-processed'
						END
					WHERE id in (SELECT id FROM pic_to_update)
			)
			SELECT MAX(inserted_at) FROM pic_to_update INTO last_inserted_at;
		
       RAISE NOTICE 'max insertion date is now %', last_inserted_at;

		-- put back triggers
		CREATE TRIGGER pictures_updates_on_sequences_trg
		AFTER UPDATE ON pictures
		REFERENCING NEW TABLE AS pictures_after
		FOR EACH STATEMENT
		EXECUTE FUNCTION pictures_updates_on_sequences();

		CREATE TRIGGER pictures_update_sequences_trg
		AFTER UPDATE ON pictures
		REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table
		FOR EACH STATEMENT EXECUTE FUNCTION pictures_update_sequence();

		-- commit batch of change
		COMMIT;
   END LOOP;

   RAISE NOTICE 'update finished';
END
$$  LANGUAGE plpgsql;

CALL update_all_pictures_preparing_status();

DROP PROCEDURE update_all_pictures_preparing_status;

CREATE INDEX pictures_preparing_status_idx ON pictures(preparing_status);
