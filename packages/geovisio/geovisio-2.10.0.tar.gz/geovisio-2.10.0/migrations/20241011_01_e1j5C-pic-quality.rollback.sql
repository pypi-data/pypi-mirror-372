-- pic_quality
-- depends: 20240912_01_dAALm-account-index

ALTER TABLE sequences DROP COLUMN computed_h_pixel_density, DROP COLUMN computed_gps_accuracy;
DROP TRIGGER IF EXISTS trg_pictures_hpixdens_gpsacc_upd ON pictures;
DROP TRIGGER IF EXISTS trg_pictures_hpixdens_gpsacc ON pictures;
DROP FUNCTION IF EXISTS pictures_hpixdens_gpsacc;
ALTER TABLE pictures DROP COLUMN gps_accuracy_m, DROP COLUMN h_pixel_density;
DROP FUNCTION IF EXISTS clean_exif;
DROP FUNCTION IF EXISTS h_pixel_density;
DROP FUNCTION IF EXISTS gps_accuracy;
DROP FUNCTION IF EXISTS get_float;
DROP FUNCTION IF EXISTS missing_fov;

DELETE FROM cameras WHERE model IN (
	'samsung SM-A336B','Viofo A119 Mini 2','GoPro HERO9 Black','GoPro HERO5 Black',
	'HUAWEI EML-L29','Panasonic DC-LX100M2','SONY FDR-X1000V','GoPro Max','samsung SM-G950F',
	'GoPro HERO7 Black','Xiaomi M2101K6G','HUAWEI VOG-L29','samsung SM-A546B','GoPro HERO10 Black',
	'Xiaomi 2107113SG','Xiaomi Redmi Note 9 Pro','GoPro HERO11 Black','OnePlus A5000','samsung SM-A500FU',
	'XIAOYI YDXJ 2','Apple iPhone 6s','samsung SM-G901F','OnePlus A3003','GoPro HERO8 Black','XIAOYI YDXJ 1'
);