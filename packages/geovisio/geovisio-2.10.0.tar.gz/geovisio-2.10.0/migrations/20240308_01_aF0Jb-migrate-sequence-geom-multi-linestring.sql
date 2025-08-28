-- migrate_sequence_geom_multi_linestring
-- depends: 20240226_01_8iXl1-track-changes  20240229_01_SgfQY-sequence-geom-multi-linestring



-- We do not want a transaction around this, as we'll be commiting batches of geometry updates
-- transactional: false

CREATE OR REPLACE PROCEDURE migrate_sequences_split_geom() AS
$$
DECLARE
	last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM sequences INTO last_inserted_at;

	WHILE last_inserted_at IS NOT NULL LOOP
		
		-- Temporary removal of all update triggers
		DROP TRIGGER sequences_update_ts_trg ON sequences;

		WITH 
			-- get a batch of 1 000 sequences to update
			seq_to_update AS (
				SELECT id, inserted_at from sequences where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 1000
			)
			, updated_seq AS (
				UPDATE sequences 
					SET 
						geom = compute_sequence_geom(id)
					WHERE id in (SELECT id FROM seq_to_update)
			)
			SELECT MAX(inserted_at) FROM seq_to_update INTO last_inserted_at;
		
		RAISE NOTICE 'max insertion date is now %', last_inserted_at;

		-- Restore all deactivated triggers
		CREATE TRIGGER sequences_update_ts_trg
		BEFORE UPDATE ON sequences
		FOR EACH ROW EXECUTE FUNCTION sequences_update_ts();

		-- commit transaction (as a procedure is in an implicit transaction, it will start a new transaction after this)
		COMMIT;
	END LOOP;

	-- After this, we need to do a full vacuum to clean dead tuples
	RAISE NOTICE 'Geometry fields updated, you should run `VACUUM FULL sequences;` afterward (or use something like pg_repack)';

END
$$  LANGUAGE plpgsql;

CALL migrate_sequences_split_geom();
DROP PROCEDURE migrate_sequences_split_geom;
