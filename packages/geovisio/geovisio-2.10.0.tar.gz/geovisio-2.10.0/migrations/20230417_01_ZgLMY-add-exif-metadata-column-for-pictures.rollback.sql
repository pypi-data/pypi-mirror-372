-- Add exif metadata column for pictures
-- depends: 20230407_01_wofh1-computed-headings

ALTER TABLE pictures DROP COLUMN exif;
