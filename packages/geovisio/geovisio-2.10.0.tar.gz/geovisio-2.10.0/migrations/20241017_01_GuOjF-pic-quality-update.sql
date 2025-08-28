-- pic_quality_update
-- depends: 20241011_01_e1j5C-pic-quality
-- transactional: false

-- Update pictures in batch
CREATE OR REPLACE PROCEDURE update_pictures_gps_accuracy() AS $$
DECLARE
	last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM pictures INTO last_inserted_at;

	WHILE last_inserted_at IS NOT NULL LOOP

		WITH 
			-- get a batch of 100 000 pictures to update
			pic_to_update AS (
				SELECT id, inserted_at from pictures where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 100000
			)
			, updated_pic AS (
				UPDATE pictures 
					SET gps_accuracy_m = gps_accuracy(metadata, exif),
						h_pixel_density = h_pixel_density(missing_fov(metadata)),
						exif = clean_exif(exif),
						metadata = missing_fov(metadata)
					WHERE id in (SELECT id FROM pic_to_update)
			)
			SELECT MAX(inserted_at) FROM pic_to_update INTO last_inserted_at;
		
		RAISE NOTICE 'max insertion date is now %', last_inserted_at;

		-- commit transaction (as a procedure is in an implicit transaction, it will start a new transaction after this)
		COMMIT;

	END LOOP;
	RAISE NOTICE 'update finished';
END
$$ LANGUAGE plpgsql;

-- Perform pictures update
SET session_replication_role = replica;
CALL update_pictures_gps_accuracy();

-- Update sequences as well
UPDATE sequences s
SET
	computed_h_pixel_density = CASE WHEN array_length(reshpd, 1) = 1 THEN reshpd[1] ELSE NULL END,
	computed_gps_accuracy = gpsacc
FROM (
	SELECT
		sp.seq_id,
		ARRAY_AGG(DISTINCT p.h_pixel_density) AS reshpd,
		PERCENTILE_CONT(0.9) WITHIN GROUP(ORDER BY p.gps_accuracy_m) AS gpsacc
	FROM sequences_pictures sp
	JOIN pictures p ON sp.pic_id = p.id
	GROUP BY sp.seq_id
) p
WHERE s.id = p.seq_id;

-- Put back triggers && cleanup
SET session_replication_role = DEFAULT;
DROP PROCEDURE update_pictures_gps_accuracy;
