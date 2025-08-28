-- sequences-account
-- depends: 20230117_01_K71Pd-pictures-ts-index

-- Add account column on sequences
ALTER TABLE sequences ADD COLUMN IF NOT EXISTS account_id UUID;
ALTER TABLE sequences ADD CONSTRAINT account_fk_id FOREIGN KEY (account_id) REFERENCES accounts (id);

-- Try to fill it with sequence's first picture account
UPDATE sequences
SET account_id = p.account_id
FROM (
	SELECT DISTINCT ON (sp.seq_id) sp.seq_id, p.account_id, COUNT(*) as nb
	FROM pictures p
	JOIN sequences_pictures sp on sp.pic_id = p.id
	GROUP BY sp.seq_id, p.account_id
	ORDER BY sp.seq_id, nb DESC
) p;

-- Otherwise, use default account
UPDATE sequences
SET account_id = (SELECT id FROM accounts WHERE is_default)
WHERE account_id IS NULL;

-- After initial init, set NOT NULL constraint on account_id
ALTER TABLE sequences ALTER COLUMN account_id SET NOT NULL;
