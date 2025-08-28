-- status
-- depends: 20230116_01_9PkjZ-add-oauth-provider  20230130_01_VRIv2-sequences-account

-- type cannot be altered in a transaction, so we ask yolo not to create one
-- transactional: false

ALTER TYPE picture_status ADD VALUE 'waiting-for-process';
ALTER TYPE picture_status ADD VALUE 'preparing-derivates';
ALTER TYPE picture_status ADD VALUE 'preparing-blur';

ALTER TYPE sequence_status ADD VALUE 'waiting-for-process';
