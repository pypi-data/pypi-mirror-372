-- pictures-exiv2
-- depends: 20230803_01_aXusm-fix-sequence-computed
-- transactional: false
-- Note: this migration is not in a transaction, since the transactions will be created inside it to update the `pictures` table (which can be very big) in batches

-- Most common properties retrieved with following request
-- SELECT jsonb_object_keys(exif) as k, count(*) as c
-- FROM pictures
-- GROUP BY k
-- HAVING count(*) >= 500
-- ORDER BY c desc;


CREATE OR REPLACE PROCEDURE update_all_pictures_exif() AS
$$
DECLARE
   last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM pictures INTO last_inserted_at;

	WHILE last_inserted_at IS NOT NULL LOOP
		
		-- Temporary removal of update trigger
		DROP TRIGGER pictures_update_sequences_trg ON pictures;
		WITH 
			pic_to_update AS (
				SELECT id, inserted_at from pictures where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 100000
			)
			, updated_pic AS (
				-- Map short EXIF tag names to Exiv2 format
UPDATE pictures SET exif = jsonb_strip_nulls(jsonb_build_object(
	'Exif.Image.ProcessingSoftware', exif->'ProcessingSoftware',
	'Exif.Image.ImageWidth', exif->'ImageWidth',
	'Exif.Image.ImageLength', exif->'ImageLength',
	'Exif.Image.ImageDescription', exif->'ImageDescription',
	'Exif.Image.Make', exif->'Make',
	'Exif.Image.Model', exif->'Model',
	'Exif.Image.Orientation', exif->'Orientation',
	'Exif.Image.XResolution', exif->'XResolution',
	'Exif.Image.YResolution', exif->'YResolution',
	'Exif.Image.ResolutionUnit', exif->'ResolutionUnit',
	'Exif.Image.Software', exif->'Software',
	'Exif.Image.DateTime', exif->'DateTime',
	'Exif.Image.Artist', exif->'Artist',
	'Exif.Image.YCbCrPositioning', exif->'YCbCrPositioning',
	'Exif.Image.Copyright', exif->'Copyright',
	'Exif.Image.ExposureTime', exif->'ExposureTime',
	'Exif.Image.FNumber', exif->'FNumber',
	'Exif.Image.ExposureProgram', exif->'ExposureProgram',
	'Exif.Image.ISOSpeedRatings', exif->'ISOSpeedRatings',
	'Exif.Image.DateTimeOriginal', exif->'DateTimeOriginal',
	'Exif.Image.CompressedBitsPerPixel', exif->'CompressedBitsPerPixel',
	'Exif.Image.ShutterSpeedValue', exif->'ShutterSpeedValue',
	'Exif.Image.ApertureValue', exif->'ApertureValue',
	'Exif.Image.BrightnessValue', exif->'BrightnessValue',
	'Exif.Image.ExposureBiasValue', exif->'ExposureBiasValue',
	'Exif.Image.MaxApertureValue', exif->'MaxApertureValue',
	'Exif.Image.SubjectDistance', exif->'SubjectDistance',
	'Exif.Image.MeteringMode', exif->'MeteringMode',
	'Exif.Image.LightSource', exif->'LightSource',
	'Exif.Image.Flash', exif->'Flash',
	'Exif.Image.FocalLength', exif->'FocalLength',
	'Exif.Image.FlashEnergy', exif->'FlashEnergy',
	'Exif.Image.FocalPlaneXResolution', exif->'FocalPlaneXResolution',
	'Exif.Image.FocalPlaneYResolution', exif->'FocalPlaneYResolution',
	'Exif.Image.FocalPlaneResolutionUnit', exif->'FocalPlaneResolutionUnit',
	'Exif.Image.ExposureIndex', exif->'ExposureIndex',
	'Exif.Image.SensingMethod', exif->'SensingMethod'
)) || jsonb_strip_nulls(jsonb_build_object(
	'Exif.Image.PrintImageMatching', exif->'PrintImageMatching',
	'Exif.Image.UniqueCameraModel', exif->'UniqueCameraModel',
	'Exif.Image.LocalizedCameraModel', exif->'LocalizedCameraModel',
	'Exif.Image.BaselineSharpness', exif->'BaselineSharpness',
	'Exif.Image.MakerNoteSafety', exif->'MakerNoteSafety',
	'Exif.Image.ProfileCopyright', exif->'ProfileCopyright',
	'Exif.Image.PreviewColorSpace', exif->'PreviewColorSpace',
	'Exif.Image.PreviewDateTime', exif->'PreviewDateTime',
	'Exif.Photo.ExposureTime', exif->'ExposureTime',
	'Exif.Photo.FNumber', exif->'FNumber',
	'Exif.Photo.ExposureProgram', exif->'ExposureProgram',
	'Exif.Photo.ISOSpeedRatings', exif->'ISOSpeedRatings',
	'Exif.Photo.SensitivityType', exif->'SensitivityType',
	'Exif.Photo.StandardOutputSensitivity', exif->'StandardOutputSensitivity',
	'Exif.Photo.RecommendedExposureIndex', exif->'RecommendedExposureIndex',
	'Exif.Photo.ExifVersion', exif->'ExifVersion',
	'Exif.Photo.DateTimeOriginal', exif->'DateTimeOriginal',
	'Exif.Photo.DateTimeDigitized', exif->'DateTimeDigitized',
	'Exif.Photo.OffsetTime', exif->'OffsetTime',
	'Exif.Photo.OffsetTimeOriginal', exif->'OffsetTimeOriginal',
	'Exif.Photo.OffsetTimeDigitized', exif->'OffsetTimeDigitized',
	'Exif.Photo.ComponentsConfiguration', exif->'ComponentsConfiguration',
	'Exif.Photo.CompressedBitsPerPixel', exif->'CompressedBitsPerPixel',
	'Exif.Photo.ShutterSpeedValue', exif->'ShutterSpeedValue',
	'Exif.Photo.ApertureValue', exif->'ApertureValue',
	'Exif.Photo.BrightnessValue', exif->'BrightnessValue',
	'Exif.Photo.ExposureBiasValue', exif->'ExposureBiasValue',
	'Exif.Photo.MaxApertureValue', exif->'MaxApertureValue',
	'Exif.Photo.SubjectDistance', exif->'SubjectDistance',
	'Exif.Photo.MeteringMode', exif->'MeteringMode',
	'Exif.Photo.LightSource', exif->'LightSource',
	'Exif.Photo.Flash', exif->'Flash',
	'Exif.Photo.FocalLength', exif->'FocalLength',
	'Exif.Photo.UserComment', exif->'UserComment',
	'Exif.Photo.FlashpixVersion', exif->'FlashpixVersion',
	'Exif.Photo.ColorSpace', exif->'ColorSpace',
	'Exif.Photo.FlashEnergy', exif->'FlashEnergy',
	'Exif.Photo.FocalPlaneXResolution', exif->'FocalPlaneXResolution',
	'Exif.Photo.FocalPlaneYResolution', exif->'FocalPlaneYResolution',
	'Exif.Photo.FocalPlaneResolutionUnit', exif->'FocalPlaneResolutionUnit'
)) || jsonb_strip_nulls(jsonb_build_object(
	'Exif.Photo.ExposureIndex', exif->'ExposureIndex',
	'Exif.Photo.SensingMethod', exif->'SensingMethod',
	'Exif.Photo.FileSource', exif->'FileSource',
	'Exif.Photo.SceneType', exif->'SceneType',
	'Exif.Photo.CustomRendered', exif->'CustomRendered',
	'Exif.Photo.ExposureMode', exif->'ExposureMode',
	'Exif.Photo.WhiteBalance', exif->'WhiteBalance',
	'Exif.Photo.DigitalZoomRatio', exif->'DigitalZoomRatio',
	'Exif.Photo.FocalLengthIn35mmFilm', exif->'FocalLengthIn35mmFilm',
	'Exif.Photo.SceneCaptureType', exif->'SceneCaptureType',
	'Exif.Photo.GainControl', exif->'GainControl',
	'Exif.Photo.Contrast', exif->'Contrast',
	'Exif.Photo.Saturation', exif->'Saturation',
	'Exif.Photo.Sharpness', exif->'Sharpness',
	'Exif.Photo.DeviceSettingDescription', exif->'DeviceSettingDescription',
	'Exif.Photo.SubjectDistanceRange', exif->'SubjectDistanceRange',
	'Exif.Photo.ImageUniqueID', exif->'ImageUniqueID',
	'Exif.Photo.BodySerialNumber', exif->'BodySerialNumber',
	'Exif.Photo.LensSpecification', exif->'LensSpecification',
	'Exif.Photo.LensMake', exif->'LensMake',
	'Exif.Photo.LensModel', exif->'LensModel',
	'Exif.Photo.SourceExposureTimesOfCompositeImage', exif->'SourceExposureTimesOfCompositeImage',
	'Exif.Iop.RelatedImageWidth', exif->'RelatedImageWidth',
	'Exif.Iop.RelatedImageLength', exif->'RelatedImageLength',
	'Exif.GPSInfo.GPSVersionID', exif->'GPSVersionID',
	'Exif.GPSInfo.GPSLatitudeRef', exif->'GPSLatitudeRef',
	'Exif.GPSInfo.GPSLatitude', exif->'GPSLatitude',
	'Exif.GPSInfo.GPSLongitudeRef', exif->'GPSLongitudeRef',
	'Exif.GPSInfo.GPSLongitude', exif->'GPSLongitude',
	'Exif.GPSInfo.GPSAltitudeRef', exif->'GPSAltitudeRef',
	'Exif.GPSInfo.GPSAltitude', exif->'GPSAltitude',
	'Exif.GPSInfo.GPSTimeStamp', exif->'GPSTimeStamp',
	'Exif.GPSInfo.GPSStatus', exif->'GPSStatus',
	'Exif.GPSInfo.GPSMeasureMode', exif->'GPSMeasureMode',
	'Exif.GPSInfo.GPSDOP', exif->'GPSDOP',
	'Exif.GPSInfo.GPSSpeedRef', exif->'GPSSpeedRef',
	'Exif.GPSInfo.GPSSpeed', exif->'GPSSpeed'
)) || jsonb_strip_nulls(jsonb_build_object(
	'Exif.GPSInfo.GPSTrackRef', exif->'GPSTrackRef',
	'Exif.GPSInfo.GPSTrack', exif->'GPSTrack',
	'Exif.GPSInfo.GPSImgDirectionRef', exif->'GPSImgDirectionRef',
	'Exif.GPSInfo.GPSImgDirection', exif->'GPSImgDirection',
	'Exif.GPSInfo.GPSMapDatum', exif->'GPSMapDatum',
	'Exif.GPSInfo.GPSProcessingMethod', exif->'GPSProcessingMethod',
	'Exif.GPSInfo.GPSDateStamp', exif->'GPSDateStamp',
	'Exif.GPSInfo.GPSDifferential', exif->'GPSDifferential',
	'Exif.MpfInfo.MPFNumberOfImages', exif->'MPFNumberOfImages',
	'Exif.MpfInfo.MPFPanOrientation', exif->'MPFPanOrientation',
	'Xmp.GPano.UsePanoramaViewer', exif->'GPano:UsePanoramaViewer',
	'Xmp.GPano.CaptureSoftware', exif->'GPano:CaptureSoftware',
	'Xmp.GPano.StitchingSoftware', exif->'GPano:StitchingSoftware',
	'Xmp.GPano.ProjectionType', exif->'GPano:ProjectionType',
	'Xmp.GPano.PoseHeadingDegrees', exif->'GPano:PoseHeadingDegrees',
	'Xmp.GPano.PosePitchDegrees', exif->'GPano:PosePitchDegrees',
	'Xmp.GPano.PoseRollDegrees', exif->'GPano:PoseRollDegrees',
	'Xmp.GPano.InitialViewHeadingDegrees', exif->'GPano:InitialViewHeadingDegrees',
	'Xmp.GPano.InitialViewPitchDegrees', exif->'GPano:InitialViewPitchDegrees',
	'Xmp.GPano.InitialViewRollDegrees', exif->'GPano:InitialViewRollDegrees',
	'Xmp.GPano.InitialHorizontalFOVDegrees', exif->'GPano:InitialHorizontalFOVDegrees',
	'Xmp.GPano.FirstPhotoDate', exif->'GPano:FirstPhotoDate',
	'Xmp.GPano.LastPhotoDate', exif->'GPano:LastPhotoDate',
	'Xmp.GPano.SourcePhotosCount', exif->'GPano:SourcePhotosCount',
	'Xmp.GPano.ExposureLockUsed', exif->'GPano:ExposureLockUsed',
	'Xmp.GPano.CroppedAreaImageWidthPixels', exif->'GPano:CroppedAreaImageWidthPixels',
	'Xmp.GPano.CroppedAreaImageHeightPixels', exif->'GPano:CroppedAreaImageHeightPixels',
	'Xmp.GPano.FullPanoWidthPixels', exif->'GPano:FullPanoWidthPixels',
	'Xmp.GPano.FullPanoHeightPixels', exif->'GPano:FullPanoHeightPixels',
	'Xmp.GPano.CroppedAreaLeftPixels', exif->'GPano:CroppedAreaLeftPixels',
	'Xmp.GPano.CroppedAreaTopPixels', exif->'GPano:CroppedAreaTopPixels',
	'Xmp.GPano.InitialCameraDolly', exif->'GPano:InitialCameraDolly'
))
					WHERE id in (SELECT id FROM pic_to_update)
			)
			SELECT MAX(inserted_at) FROM pic_to_update INTO last_inserted_at;
		
       RAISE NOTICE 'max insertion date is now %', last_inserted_at;


		-- Restore trigger
		CREATE TRIGGER pictures_update_sequences_trg
		AFTER UPDATE ON pictures
		REFERENCING OLD TABLE AS old_table NEW TABLE AS new_table
		FOR EACH STATEMENT EXECUTE FUNCTION  pictures_update_sequence();

		COMMIT;
   END LOOP;
   RAISE NOTICE 'update finished';
END
$$  LANGUAGE plpgsql;

CALL update_all_pictures_exif();

DROP PROCEDURE update_all_pictures_exif;



