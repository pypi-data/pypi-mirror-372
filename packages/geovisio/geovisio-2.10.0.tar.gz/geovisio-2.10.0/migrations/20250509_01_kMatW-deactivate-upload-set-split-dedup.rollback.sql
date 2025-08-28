-- deactivate_upload_set_split_dedup
-- depends: 20250424_01_RBGXC-semantics-indexes

ALTER TABLE upload_sets DROP COLUMN no_deduplication;
ALTER TABLE upload_sets DROP COLUMN no_split;

-- drop default on the dispatch param, to be able to handle those at code level
alter table upload_sets ALTER COLUMN split_time SET DEFAULT INTERVAL '1 minute';
alter table upload_sets ALTER COLUMN split_distance SET DEFAULT 100;
alter table upload_sets ALTER COLUMN duplicate_distance SET DEFAULT 1;
alter table upload_sets ALTER COLUMN duplicate_rotation SET DEFAULT 30;

