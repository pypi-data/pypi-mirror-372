-- upload_set_sort
-- depends: 20240723_01_ePGFe-upload-set-files
CREATE TYPE upload_set_sort_method_new AS ENUM (
    'filename_asc',
    'filename_desc',
    'time_asc',
    'time_desc'
);
ALTER TABLE upload_sets
ALTER COLUMN sort_method DROP DEFAULT;
ALTER TABLE upload_sets
ALTER COLUMN sort_method TYPE upload_set_sort_method_new USING sort_method::text::upload_set_sort_method_new;
ALTER TABLE upload_sets
ALTER COLUMN sort_method
SET DEFAULT 'time_asc';
DROP TYPE upload_set_sort_method;
ALTER TYPE upload_set_sort_method_new
RENAME TO upload_set_sort_method;