-- inserted_at_index
-- depends: 20230623_01_y1SiQ-pic-deletion-task  20230629_01_ZdB3i-compute-heading-0

CREATE INDEX sequences_inserted_at_idx ON sequences(inserted_at);
