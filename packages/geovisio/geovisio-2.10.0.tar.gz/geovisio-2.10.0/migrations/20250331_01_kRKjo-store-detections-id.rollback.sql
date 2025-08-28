-- store_detections
-- depends: 20250318_01_pANl1-semantics-functions

ALTER TABLE pictures DROP column blurring_id;

DROP TRIGGER delete_empty_annotation_trg ON annotations_semantics;
DROP FUNCTION delete_empty_annotations();