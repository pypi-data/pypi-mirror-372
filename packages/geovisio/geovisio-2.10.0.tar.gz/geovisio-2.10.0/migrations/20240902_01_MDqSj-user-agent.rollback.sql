-- user_agent
-- depends: 20240801_01_DOqmf-reports  20240813_01_T1XkO-sequences-geom-splits

ALTER TABLE sequences DROP COLUMN user_agent;
ALTER TABLE upload_sets DROP COLUMN user_agent;
