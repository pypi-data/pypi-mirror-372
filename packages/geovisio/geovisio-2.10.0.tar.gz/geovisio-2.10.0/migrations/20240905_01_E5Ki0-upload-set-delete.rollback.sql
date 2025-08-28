-- upload_set_delete
-- depends: 20240801_01_DOqmf-reports  20240813_01_T1XkO-sequences-geom-splits

DROP TRIGGER delete_upload_set_on_last_picture_trg ON pictures;
DROP FUNCTION delete_upload_set_on_last_picture();
