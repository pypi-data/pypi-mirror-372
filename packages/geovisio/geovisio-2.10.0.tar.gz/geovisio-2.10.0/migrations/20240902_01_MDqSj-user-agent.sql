-- user_agent
-- depends: 20240801_01_DOqmf-reports  20240813_01_T1XkO-sequences-geom-splits

-- Sequences
ALTER TABLE sequences ADD COLUMN user_agent VARCHAR;
CREATE INDEX sequences_user_agent_idx ON sequences USING GIST(user_agent gist_trgm_ops);

-- Upload sets
ALTER TABLE upload_sets ADD COLUMN user_agent VARCHAR;
CREATE INDEX upload_sets_user_agent_idx ON upload_sets USING GIST(user_agent gist_trgm_ops);
