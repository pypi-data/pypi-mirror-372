-- tokens
-- depends: 20230427_01_k5e5w-timestamps

CREATE TABLE tokens(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	account_id UUID,
	description VARCHAR,
	generated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE tokens ADD CONSTRAINT account_fk_id FOREIGN KEY (account_id) REFERENCES accounts (id);

-- generate a default token for each existing account
INSERT INTO tokens (account_id, description)
SELECT id, 'default token' from accounts;


-- Also add trigger to generate default token for each new account
DROP FUNCTION IF EXISTS generate_default_token CASCADE;
CREATE FUNCTION generate_default_token() RETURNS trigger AS
$BODY$
BEGIN
    INSERT INTO
        tokens (account_id, description)
	VALUES 
		(NEW.id, 'default token');
	RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE TRIGGER generate_default_token_trg
AFTER INSERT ON accounts
FOR EACH ROW EXECUTE PROCEDURE generate_default_token();