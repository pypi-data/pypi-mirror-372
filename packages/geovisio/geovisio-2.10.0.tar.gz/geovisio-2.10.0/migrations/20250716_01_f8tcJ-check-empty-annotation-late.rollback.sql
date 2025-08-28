-- check_empty_annotation_late
-- depends: 20250703_02_q0s3D-sequence-upload-set-fill

-- put back old trigger
DROP FUNCTION IF EXISTS delete_empty_annotations CASCADE;
CREATE FUNCTION delete_empty_annotations() RETURNS trigger AS $$
BEGIN
    -- Delete annotations where no remaining semantics exist
    DELETE FROM annotations a
    WHERE a.id IN (
        SELECT DISTINCT(deleted_as.annotation_id)
        FROM deleted_annotations_semantics deleted_as
        LEFT JOIN annotations_semantics ON deleted_as.annotation_id = annotations_semantics.annotation_id
        WHERE annotations_semantics.annotation_id IS NULL
    );
	RETURN NULL;
END $$ LANGUAGE plpgsql;

-- trigger to delete annotation is there is no semantics tags
CREATE TRIGGER delete_empty_annotation_trg
AFTER DELETE ON annotations_semantics
REFERENCING OLD TABLE AS deleted_annotations_semantics
FOR EACH STATEMENT
EXECUTE FUNCTION delete_empty_annotations();
