-- fill_pictures_stats_on_sequences
-- depends: 20240416_01_FpyGs-pictures-stats-on-sequences

DROP TRIGGER picture_insertion_update_sequence_trigger ON pictures CASCADE;
DROP TRIGGER seq_picture_deletion_update_sequence_trigger ON sequences_pictures CASCADE;
