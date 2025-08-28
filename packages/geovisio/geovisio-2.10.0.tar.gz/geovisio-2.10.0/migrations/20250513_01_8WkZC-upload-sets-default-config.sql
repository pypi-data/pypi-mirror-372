-- upload_sets_default_config
-- depends: 20250502_01_ZNmkU-job-task-read-metadata  20250509_01_kMatW-deactivate-upload-set-split-dedup  20250509_01_s3hYk-semantic-delete-cascade
ALTER TABLE configurations
ADD COLUMN default_split_distance INT DEFAULT 100,
ADD COLUMN default_split_time INTERVAL DEFAULT INTERVAL '5 minute',
ADD COLUMN default_duplicate_distance real DEFAULT 1,
ADD COLUMN default_duplicate_rotation INT DEFAULT 60;

COMMENT ON COLUMN configurations.default_split_distance IS 'Maximum distance between two pictures to be considered in the same sequence (in meters).';

COMMENT ON COLUMN configurations.default_split_time IS 'Maximum time interval between two pictures to be considered in the same sequence.';

COMMENT ON COLUMN configurations.default_duplicate_distance IS 'Maximum distance between two pictures to be considered as duplicates (in meters).';

COMMENT ON COLUMN configurations.default_duplicate_rotation IS 'Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).';
