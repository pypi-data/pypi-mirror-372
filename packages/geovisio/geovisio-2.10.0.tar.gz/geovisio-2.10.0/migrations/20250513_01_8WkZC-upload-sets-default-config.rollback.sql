-- upload_sets_default_config
-- depends: 20250502_01_ZNmkU-job-task-read-metadata  20250509_01_kMatW-deactivate-upload-set-split-dedup  20250509_01_s3hYk-semantic-delete-cascade
ALTER TABLE configurations
DROP COLUMN default_split_distance,
DROP COLUMN default_split_time,
DROP COLUMN default_duplicate_distance,
DROP COLUMN default_duplicate_rotation;
