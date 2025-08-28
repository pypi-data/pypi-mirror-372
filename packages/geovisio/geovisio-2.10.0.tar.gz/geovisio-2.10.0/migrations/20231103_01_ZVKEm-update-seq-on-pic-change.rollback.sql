-- update_seq_on_pic_change
-- depends: 20231018_01_4G3YE-pictures-exiv2

DROP INDEX sequences_updated_at_idx;
DROP TRIGGER pictures_updates_on_sequences_trg ON pictures;
DROP TRIGGER pictures_deletes_on_sequences_trg ON pictures;
DROP FUNCTION pictures_updates_on_sequences();
