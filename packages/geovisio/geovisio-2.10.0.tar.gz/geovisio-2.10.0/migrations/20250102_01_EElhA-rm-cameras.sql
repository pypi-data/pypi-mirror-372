-- rm-cameras
-- depends: 20241128_01_ugthx-job-queue-args

-- Get rid of cameras table, infos are coming from Tag Reader
DROP TABLE cameras;

-- Replace trigger which updated GPS accuracy & Px density to only update Px density
DROP TRIGGER trg_pictures_hpixdens_gpsacc ON pictures;
DROP TRIGGER trg_pictures_hpixdens_gpsacc_upd ON pictures;
DROP FUNCTION pictures_hpixdens_gpsacc;
DROP FUNCTION gps_accuracy;
DROP FUNCTION get_float;
DROP FUNCTION missing_fov;

CREATE OR REPLACE FUNCTION pictures_hpixdens() RETURNS TRIGGER AS $$
BEGIN
    NEW.h_pixel_density := h_pixel_density(NEW.metadata);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_pictures_hpixdens
BEFORE INSERT ON pictures
FOR EACH ROW
EXECUTE FUNCTION pictures_hpixdens();

CREATE TRIGGER trg_pictures_hpixdens_upd
BEFORE UPDATE OF metadata, exif ON pictures
FOR EACH ROW
EXECUTE FUNCTION pictures_hpixdens();
