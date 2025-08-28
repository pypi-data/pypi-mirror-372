-- pictures_stats_on_sequences
-- depends: 20240223_01_LsMHB-remove-binary-fields  20240308_01_aF0Jb-migrate-sequence-geom-multi-linestring

ALTER TABLE sequences DROP COLUMN min_picture_ts;
ALTER TABLE sequences DROP COLUMN max_picture_ts;
ALTER TABLE sequences DROP COLUMN nb_pictures; 

