-- content_md5
-- depends: 20240514_01_IT7DD-picture-delete-cascade

ALTER TABLE pictures DROP COLUMN IF EXISTS original_content_md5;

