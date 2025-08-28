-- remove_binary_fields
-- depends: 20240115_01_FatLR-token-delete-cascade

-- We want to run a vacuum after the migration, we cannot have a transaction around it
-- transactional: false

CREATE OR REPLACE PROCEDURE remove_maker_notes_from_all_pictures() AS
$$
DECLARE
	last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM pictures INTO last_inserted_at;

		WHILE last_inserted_at IS NOT NULL LOOP
		
		-- Temporary removal of all update triggers
		DROP TRIGGER pictures_updates_on_sequences_trg ON pictures;

		WITH 
			-- get a batch of 100 000 pictures to update
			pic_to_update AS (
				SELECT id, inserted_at from pictures where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 100000
			)
			, updated_pic AS (
				-- List of binary fields to remove.
				-- The most important here is `MakerNote` that takes a lot of useless space, but we decided not to store any binary fields, as they will be difficult to use 
				-- Note: they are still in the pictures if needed
				UPDATE pictures 
					SET 
						exif = exif - ARRAY[
									'Exif.Photo.MakerNote',
									'Exif.Photo.0xea1c',
									'Exif.Image.0xea1c',
									'Exif.Canon.CameraInfo',
									'Exif.Image.PrintImageMatching',
									'Exif.Image.0xc6d3',
									'Exif.Panasonic.FaceDetInfo',
									'Exif.Panasonic.DataDump',
									'Exif.Image.0xc6d2',
									'Exif.Canon.CustomFunctions',
									'Exif.Canon.AFInfo',
									'Exif.Canon.0x4011',
									'Exif.Canon.0x4019',
									'Exif.Canon.ColorData',
									'Exif.Canon.DustRemovalData',
									'Exif.Canon.VignettingCorr',
									'Exif.Canon.AFInfo3',
									'Exif.Canon.0x001f',
									'Exif.Canon.0x0018',
									'Exif.Canon.ContrastInfo',
									'Exif.Canon.0x002e',
									'Exif.Canon.0x0022',
									'Exif.Photo.0x9aaa'
						]
					WHERE id in (SELECT id FROM pic_to_update)
			)
			SELECT MAX(inserted_at) FROM pic_to_update INTO last_inserted_at;
		
		RAISE NOTICE 'max insertion date is now %', last_inserted_at;

		-- Restore all deactivated triggers
		CREATE TRIGGER pictures_updates_on_sequences_trg
		AFTER UPDATE ON pictures
		REFERENCING NEW TABLE AS pictures_after
		FOR EACH STATEMENT
		EXECUTE FUNCTION pictures_updates_on_sequences();

		-- commit transaction (as a procedure is in an implicit transaction, it will start a new transaction after this)
		COMMIT;
	END LOOP;

	-- After this, we need to do a full vacuum to clean dead tuples
	RAISE NOTICE 'Binary fields removed, you should run `VACUUM FULL pictures;` afterward (or use something like pg_repack)';

END
$$  LANGUAGE plpgsql;

CALL remove_maker_notes_from_all_pictures();
DROP PROCEDURE remove_maker_notes_from_all_pictures;

