-- Remove picture and sequence file paths
-- depends: 20230417_01_ZgLMY-add-exif-metadata-column-for-pictures

ALTER TABLE pictures DROP COLUMN IF EXISTS file_path;
ALTER TABLE sequences DROP COLUMN IF EXISTS folder_path;
