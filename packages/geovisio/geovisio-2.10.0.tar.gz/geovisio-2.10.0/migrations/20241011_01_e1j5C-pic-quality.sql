-- pic_quality
-- depends: 20240912_01_dAALm-account-index

-- NOTE : this migration is split in two files
--   this one, and next migration pic_quality_update
--   this migration is transactional, the next one is not


-- Add common cameras focal length (for FOV + HPixelDensity)
-- NOTE : cameras / sensor_data is not used anymore in versions > 2.7.1
--       For updating cameras metadata, please see GeoPicture Tag Reader repository
INSERT INTO cameras(model, sensor_width) VALUES
('samsung SM-A336B', 6.4),
('Viofo A119 Mini 2', 5.2),
('GoPro HERO9 Black', 6.17),
('GoPro HERO5 Black', 6.17),
('HUAWEI EML-L29', 6.29),
('Panasonic DC-LX100M2', 17.3),
('SONY FDR-X1000V', 6.19),
('GoPro Max', 6.17),
('samsung SM-G950F',7.05),
('GoPro HERO7 Black',6.17),
('Xiaomi M2101K6G',8.4),
('HUAWEI VOG-L29',7.3),
('samsung SM-A546B', 12),
('GoPro HERO10 Black', 6.17),
('Xiaomi 2107113SG',7.4),
('Xiaomi Redmi Note 9 Pro',7.2),
('GoPro HERO11 Black', 6.74),
('OnePlus A5000', 5.22),
('samsung SM-A500FU', 4.69),
('XIAOYI YDXJ 2', 10.2),
('Apple iPhone 6s', 4.8),
('samsung SM-G901F', 5.95),
('OnePlus A3003', 6.4),
('GoPro HERO8 Black', 6.17),
('XIAOYI YDXJ 1', 10.2);


-- Complete FOV for imported pictures
CREATE OR REPLACE FUNCTION missing_fov(metadata JSONB) RETURNS JSONB AS $$
DECLARE
	sensor_width FLOAT;
BEGIN
	IF metadata->>'field_of_view' IS NOT NULL OR metadata->>'focal_length' IS NULL OR (metadata->>'focal_length')::float = 0 THEN
		RETURN metadata;
	END IF;

	-- Find appropriate sensor width
	IF metadata->>'make' = 'samsung' AND metadata->>'model' = 'SM-A336B' THEN
		sensor_width :=  6.4;
	ELSIF metadata->>'make' = 'Viofo' AND metadata->>'model' = 'A119 Mini 2' THEN
		sensor_width := 5.2;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO9 Black' THEN
		sensor_width :=  6.17;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO5 Black' THEN
		sensor_width :=  6.17;
	ELSIF metadata->>'make' = 'HUAWEI' AND metadata->>'model' = 'EML-L29' THEN
		sensor_width :=  6.29;
	ELSIF metadata->>'make' = 'Panasonic' AND metadata->>'model' = 'DC-LX100M2' THEN
		sensor_width :=  17.3;
	ELSIF metadata->>'make' = 'SONY' AND metadata->>'model' = 'FDR-X1000V' THEN
		sensor_width :=  6.19;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'Max' THEN
		sensor_width := 6.17;
	ELSIF metadata->>'make' = 'samsung' AND metadata->>'model' = 'SM-G950F' THEN
		sensor_width := 7.05;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO7 Black' THEN
		sensor_width := 6.17;
	ELSIF metadata->>'make' = 'Xiaomi' AND metadata->>'model' = 'M2101K6G' THEN
		sensor_width := 8.4;
	ELSIF metadata->>'make' = 'HUAWEI' AND metadata->>'model' = 'VOG-L29' THEN
		sensor_width := 7.3;
	ELSIF metadata->>'make' = 'samsung' AND metadata->>'model' = 'SM-A546B' THEN
		sensor_width := 12;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO10 Black' THEN
		sensor_width :=  6.17;
	ELSIF metadata->>'make' = 'Xiaomi' AND metadata->>'model' = '2107113SG' THEN
		sensor_width := 7.4;
	ELSIF metadata->>'make' = 'Xiaomi' AND metadata->>'model' = 'Redmi Note 9 Pro' THEN
		sensor_width := 7.2;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO11 Black' THEN
		sensor_width := 6.74;
	ELSIF metadata->>'make' = 'OnePlus' AND metadata->>'model' = 'A5000' THEN
		sensor_width := 5.22;
	ELSIF metadata->>'make' = 'samsung' AND metadata->>'model' = 'SM-A500FU' THEN
		sensor_width := 4.69;
	ELSIF metadata->>'make' = 'XIAOYI' AND metadata->>'model' = 'YDXJ 2' THEN
		sensor_width := 10.2;
	ELSIF metadata->>'make' = 'Apple' AND metadata->>'model' = 'iPhone 6s' THEN
		sensor_width := 4.8;
	ELSIF metadata->>'make' = 'samsung' AND metadata->>'model' = 'SM-G901F' THEN
		sensor_width := 5.95;
	ELSIF metadata->>'make' = 'OnePlus' AND metadata->>'model' = 'A3003' THEN
		sensor_width := 6.4;
	ELSIF metadata->>'make' = 'GoPro' AND metadata->>'model' = 'HERO8 Black' THEN
		sensor_width := 6.17;
	ELSIF metadata->>'make' = 'XIAOYI' AND metadata->>'model' = 'YDXJ 1' THEN
		sensor_width := 10.2;
	-- If not found, just send back original metadata
	ELSE
		RETURN metadata;
	END IF;

	-- Update metadata
	RETURN jsonb_set(
		metadata,
		'{field_of_view}'::text[],
		((ROUND(DEGREES(2 * ATAN(sensor_width / (2 * (metadata->>'focal_length')::float)))))::varchar)::jsonb
	);
END;
$$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;


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


-- Number of pixels on horizon per FOV degree
CREATE OR REPLACE FUNCTION h_pixel_density(metadata JSONB) RETURNS INT AS $$
BEGIN
	RETURN round((metadata->>'width')::float / (metadata->>'field_of_view')::float);
END;
$$ LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE;


-- Clean-up EXIF, as we're here to rewrite all pictures...
--   Removes all proprietary keys ending in .0x1234 (hex key)
CREATE OR REPLACE FUNCTION clean_exif(exif JSONB) RETURNS JSONB AS $$
	SELECT jsonb_object_agg(key, value)
	FROM (
		SELECT key, value
		FROM jsonb_each(exif)
		WHERE key !~ '\.0x[0-9a-fA-F]+$'
	) a;
$$ LANGUAGE sql IMMUTABLE PARALLEL SAFE;


-- Add columns for pictures
ALTER TABLE pictures
	ADD COLUMN gps_accuracy_m FLOAT,
	ADD COLUMN h_pixel_density INT;


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


-- Add info on sequences too
ALTER TABLE sequences
	ADD COLUMN computed_h_pixel_density INT,
	ADD COLUMN computed_gps_accuracy FLOAT;
