-- Remove picture and sequence file paths
-- depends: 20230417_01_ZgLMY-add-exif-metadata-column-for-pictures

ALTER TABLE pictures ADD COLUMN file_path VARCHAR;
ALTER TABLE sequences ADD COLUMN folder_path VARCHAR;
