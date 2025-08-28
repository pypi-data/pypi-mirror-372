-- sequence_current_sort
-- depends: 20240115_01_FatLR-token-delete-cascade

ALTER TABLE sequences DROP COLUMN current_sort;

DROP TYPE sequence_sort;