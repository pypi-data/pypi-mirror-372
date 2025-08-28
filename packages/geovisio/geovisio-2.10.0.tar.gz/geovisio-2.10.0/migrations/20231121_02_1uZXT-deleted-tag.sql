-- deleted_tag
-- depends: 20231121_01_v6oBF-more-specific-triggers

-- type cannot be altered in a transaction, so we ask yolo not to create one
-- transactional: false

ALTER TYPE sequence_status ADD VALUE 'deleted';


CREATE OR REPLACE FUNCTION is_sequence_visible_by_user(seq sequences, account_id UUID) RETURNS boolean AS $$
    SELECT seq.status != 'deleted' AND (seq.status = 'ready' OR seq.account_id = account_id);
$$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE COST 10;

