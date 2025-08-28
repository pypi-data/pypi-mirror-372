-- add-provider-oidc
-- depends: 20230113_01_0co97-rm-metadata-duplicates

DROP INDEX oauth_id_idx;

ALTER TABLE accounts 
	DROP COLUMN oauth_provider,
	DROP COLUMN oauth_id,
	DROP COLUMN created_at;

ALTER TABLE accounts ADD CONSTRAINT name_unique UNIQUE (name);

