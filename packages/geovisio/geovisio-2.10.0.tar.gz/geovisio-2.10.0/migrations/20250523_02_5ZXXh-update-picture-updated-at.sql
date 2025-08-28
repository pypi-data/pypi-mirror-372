-- update_picture_updated_at
-- depends: 20250523_01_b11eW-picture-update-index

-- transactional: false

CREATE INDEX CONCURRENTLY pictures_updated_at_idx ON pictures(updated_at);

