-- sequence_upload_set_fill
-- depends: 20250703_01_p2WVV-sequence-upload-set-link
-- transactional: false

-- outside a transaction, we fill the link sequence/upload_set while disabling triggers (to speed up thing and not update the `updated_at` value for the sequence) and compute the index concurrently
-- Note: if the database does not support to set the replication role, 
-- you'll need to disable the sequences_update_ts_trg trigger manually (and enable it after the update)

SET session_replication_role = replica;

-- big update to add upload_set_id to all sequences
WITH sequences_upload_set_link AS (
    SELECT DISTINCT ON (sp.seq_id) sp.seq_id, p.upload_set_id
    FROM sequences_pictures sp
    JOIN pictures p ON sp.pic_id = p.id
    WHERE p.upload_set_id IS NOT NULL
)
UPDATE sequences s
SET upload_set_id = link.upload_set_id
FROM sequences_upload_set_link link
WHERE s.id = link.seq_id;

-- put back the triggers
SET session_replication_role = DEFAULT;

CREATE INDEX CONCURRENTLY sequences_upload_set_id_idx ON sequences(upload_set_id);
