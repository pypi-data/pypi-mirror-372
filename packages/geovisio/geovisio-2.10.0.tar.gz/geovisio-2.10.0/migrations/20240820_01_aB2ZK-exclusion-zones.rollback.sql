-- exclusion-zones
-- depends: 20240801_01_DOqmf-reports  20240801_01_uKqPo-remove-files-delete-cascade

DROP TRIGGER pictures_excluded_areas_trg ON pictures;
DROP FUNCTION is_picture_in_excluded_area;
DROP TABLE excluded_areas;
