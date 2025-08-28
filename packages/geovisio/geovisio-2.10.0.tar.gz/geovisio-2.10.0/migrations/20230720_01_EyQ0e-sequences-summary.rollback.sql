-- sequences-summary
-- depends: 20230711_01_JGSPB-inserted-at-index

ALTER TABLE sequences
DROP COLUMN computed_type,
DROP COLUMN computed_model,
DROP COLUMN computed_capture_date;
