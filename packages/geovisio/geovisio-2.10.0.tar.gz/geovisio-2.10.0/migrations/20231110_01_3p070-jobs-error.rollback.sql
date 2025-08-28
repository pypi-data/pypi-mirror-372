-- jobs_error
-- depends: 20231103_01_ZVKEm-update-seq-on-pic-change
DROP TABLE job_history CASCADE;
ALTER TABLE pictures_to_process DROP COLUMN nb_errors;

ALTER TABLE pictures DROP COLUMN preparing_status;
DROP TYPE picture_preparing_status;
