-- add-account
-- depends: 20221201_02_ZG8AR-camera-information

CREATE TABLE accounts(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	name VARCHAR NOT NULL,
	is_default BOOLEAN NOT NULL DEFAULT false,

	CONSTRAINT name_unique UNIQUE (name) 
);

-- At most one account can be the default one
CREATE UNIQUE INDEX at_most_one_default 
ON accounts (is_default) WHERE (is_default);

-- Add a link betwen account and picture
ALTER TABLE pictures ADD COLUMN IF NOT EXISTS account_id UUID;
ALTER TABLE pictures ADD CONSTRAINT account_fk_id FOREIGN KEY (account_id) REFERENCES accounts (id);

-- Create default account and associate existing pictures to default account
WITH default_account AS (
	INSERT INTO accounts(name, is_default) 
		VALUES('Default account', true)
		ON CONFLICT DO NOTHING
		RETURNING id
)
UPDATE pictures
	SET account_id = default_account.id
	FROM default_account
	WHERE account_id IS NULL;

-- After initial init, set NOT NULL constraint on account_id
ALTER TABLE pictures ALTER COLUMN account_id SET NOT NULL;
