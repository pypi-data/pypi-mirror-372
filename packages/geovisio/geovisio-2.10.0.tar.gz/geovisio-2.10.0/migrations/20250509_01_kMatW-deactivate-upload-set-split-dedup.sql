-- deactivate_upload_set_split_dedup
-- depends: 20250424_01_RBGXC-semantics-indexes

ALTER TABLE upload_sets ADD COLUMN no_deduplication BOOLEAN;
ALTER TABLE upload_sets ADD COLUMN no_split BOOLEAN;

-- drop default on the dispatch param, to be able to handle those at code level
alter table upload_sets ALTER COLUMN split_time DROP DEFAULT;
alter table upload_sets ALTER COLUMN split_distance DROP DEFAULT;
alter table upload_sets ALTER COLUMN duplicate_distance DROP DEFAULT;
alter table upload_sets ALTER COLUMN duplicate_rotation DROP DEFAULT;

