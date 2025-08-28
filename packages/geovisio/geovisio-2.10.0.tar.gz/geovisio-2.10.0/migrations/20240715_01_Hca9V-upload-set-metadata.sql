-- upload_set_metadata
-- depends: 20240708_01_Xn7IH-job-queue

ALTER TABLE upload_sets
  ADD COLUMN metadata jsonb;
