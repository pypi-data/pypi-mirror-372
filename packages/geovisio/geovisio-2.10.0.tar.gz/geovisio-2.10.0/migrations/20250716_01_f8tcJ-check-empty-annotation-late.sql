-- check_empty_annotation_late
-- depends: 20250703_02_q0s3D-sequence-upload-set-fill

-- We do not want triggers to remove empty annotations, as it needs to be done at the end of the transaction
-- and constraint triggers (that can be deffered) cannot be for each statement
-- and we fear this will be too slow when deleting lots of pictures (so lots of annotations, so lots of semantics)
-- This will be checked in the code, in the `update_tags` function, so we can better control this

DROP TRIGGER delete_empty_annotation_trg ON annotations_semantics;
DROP FUNCTION delete_empty_annotations();
