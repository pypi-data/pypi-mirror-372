-- rm-cameras
-- depends: 20241128_01_ugthx-job-queue-args

DROP TRIGGER trg_pictures_hpixdens_upd ON pictures;
DROP TRIGGER trg_pictures_hpixdens ON pictures;
DROP FUNCTION pictures_hpixdens;

-- Read float values from EXIF
CREATE OR REPLACE FUNCTION get_float(val VARCHAR) RETURNS FLOAT AS $$
DECLARE
	list VARCHAR[];
BEGIN
	IF val ~ '^\d+\/\d+$' THEN
		list := regexp_split_to_array(val, '/');
		RETURN list[1]::float / list[2]::float;
    ELSIF val ~ '^\d+(\.\d+)?$' THEN
        RETURN val::float;
    ELSE
        RETURN NULL;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;


-- GPS accuracy function
CREATE OR REPLACE FUNCTION gps_accuracy(metadata JSONB, exif JSONB) RETURNS FLOAT AS $$
DECLARE
	gps_dop FLOAT;
	gps_diff INT;
	gps_hpos_err FLOAT;
BEGIN
	-- Parse GPS DOP, either float or fraction
	gps_dop := get_float(COALESCE(exif->>'Exif.GPSInfo.GPSDOP', exif->>'Xmp.exif.GPSDOP', ''));
	gps_diff := (COALESCE(exif->>'Exif.GPSInfo.GPSDifferential', exif->>'Xmp.exif.GPSDifferential'))::INT;
	gps_hpos_err := get_float(COALESCE(exif->>'Exif.GPSInfo.GPSHPositioningError', exif->>'Xmp.exif.GPSHPositioningError'));

	-- Direct horizontal positioning error in meters -> return as is
	IF gps_hpos_err IS NOT NULL AND gps_hpos_err > 0 THEN
		RETURN gps_hpos_err;
	
	-- GPS DOP available
	ELSIF gps_dop IS NOT NULL AND gps_dop > 0 THEN
		-- With a DGPS -> consider GPS nominal error as 1 meter
		IF gps_diff = 1 THEN
			RETURN gps_dop;
		
		-- Without DGPS -> consider GPS nominal error as 3 meters in average
		ELSE
			RETURN 3 * gps_dop;
		END IF;
	
	-- DGPS -> return 2 meters precision
	ELSIF gps_diff = 1 THEN
		RETURN 2;

	-- Approximate guesses based on model
	ELSIF metadata->>'make' IS NOT NULL OR metadata->>'model' IS NOT NULL THEN
		-- Good non-diff GPS devices (best case is 3m, so setting 4 for tolerance)
		IF lower(metadata->>'make') IN (
			'gopro', 'insta360', 'garmin', 'viofo', 'xiaoyi', 'blackvue', 'tectectec',
			'arashi vision'
		)
		OR metadata->>'model' IN ('LG-R105', 'FDR-X1000V') 
		OR metadata->>'make' ILIKE '%xiaoyi%' THEN
			RETURN 4;

		-- Diff GPS devices
		ELSIF lower(metadata->>'make') IN ('stfmani', 'trimble', 'imajing')
		OR metadata->>'model' IN ('LB5') OR metadata->>'model' ILIKE '%ladybug%' THEN
			RETURN 2;

		-- Smartphones or not-so-good non-diff GPS devices
		ELSIF lower(metadata->>'make') IN (
			'samsung', 'xiaomi', 'huawei', 'ricoh', 'lenovo', 'motorola', 'oneplus',
			'apple', 'google', 'sony', 'wiko', 'asus', 'cubot', 'lge', 'fairphone',
			'realme', 'symphony', 'crosscall', 'htc', 'homtom', 'hmd global', 'oppo',
			'ulefone'
		) THEN
			RETURN 5;
		
		-- Fallback for unknown make/model
		ELSE
			RETURN NULL;
		END IF;
	-- Fallback : no value
	ELSE
		RETURN NULL;
	END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;

-- Function should not be used in rollback, created a mock one for db_migration tests
CREATE OR REPLACE FUNCTION missing_fov(metadata JSONB) RETURNS JSONB AS $$
DECLARE
	sensor_width FLOAT;
BEGIN
	RETURN metadata;
END;
$$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;

-- Auto-insert pixel density/GPS accuracy for new pictures
CREATE OR REPLACE FUNCTION pictures_hpixdens_gpsacc() RETURNS TRIGGER AS $$
BEGIN
    NEW.h_pixel_density := h_pixel_density(NEW.metadata);
	NEW.gps_accuracy_m := gps_accuracy(NEW.metadata, NEW.exif);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pictures_hpixdens_gpsacc
BEFORE INSERT ON pictures
FOR EACH ROW
EXECUTE FUNCTION pictures_hpixdens_gpsacc();

CREATE TRIGGER trg_pictures_hpixdens_gpsacc_upd
BEFORE UPDATE OF metadata, exif ON pictures
FOR EACH ROW
EXECUTE FUNCTION pictures_hpixdens_gpsacc();

-- Mock table for db_migration tests
CREATE TABLE cameras(
	model VARCHAR PRIMARY KEY,
	sensor_width FLOAT NOT NULL
);

CREATE INDEX cameras_model_idx ON cameras USING GIST(model gist_trgm_ops);
