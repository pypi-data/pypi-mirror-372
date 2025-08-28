-- upload_set
-- depends: 20240514_01_IT7DD-picture-delete-cascade

ALTER TABLE pictures DROP COLUMN IF EXISTS upload_set_id;
DROP TABLE upload_sets;
DROP TYPE upload_set_sort_method;
