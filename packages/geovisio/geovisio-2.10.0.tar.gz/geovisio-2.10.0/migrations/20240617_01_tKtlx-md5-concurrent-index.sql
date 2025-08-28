-- md5_concurrent_index
-- depends: 20240611_01_jftHn-content-md5

-- transactional: false


CREATE INDEX CONCURRENTLY pictures_original_content_md5_idx ON pictures(original_content_md5);

