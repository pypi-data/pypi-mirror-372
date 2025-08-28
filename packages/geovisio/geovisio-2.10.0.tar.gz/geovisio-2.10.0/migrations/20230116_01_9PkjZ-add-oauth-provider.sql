-- add-provider-oidc
-- depends: 20230113_01_0co97-rm-metadata-duplicates


ALTER TABLE accounts ADD COLUMN IF NOT EXISTS oauth_provider VARCHAR;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS oauth_id VARCHAR;
ALTER TABLE accounts ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE accounts DROP CONSTRAINT name_unique;

CREATE UNIQUE INDEX oauth_id_idx ON accounts (oauth_provider, oauth_id);
