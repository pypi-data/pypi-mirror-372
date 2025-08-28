-- pictures_stats_on_sequences
-- depends: 20240223_01_LsMHB-remove-binary-fields  20240308_01_aF0Jb-migrate-sequence-geom-multi-linestring

-- To avoid a costly join on sequence_pictures and picture, we add aggregated values at the sequence level, computed using triggers (in the next migration to split the table migration in 2 transactions)

ALTER TABLE sequences
ADD COLUMN min_picture_ts TIMESTAMPTZ,
ADD COLUMN max_picture_ts TIMESTAMPTZ,
ADD COLUMN nb_pictures BIGINT DEFAULT 0;
