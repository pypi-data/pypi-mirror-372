-- content_md5
-- depends: 20240514_01_IT7DD-picture-delete-cascade

-- concurrent index cannot be run inside a transaction
-- transactional: false

ALTER TABLE pictures ADD COLUMN IF NOT EXISTS original_content_md5 UUID;
