-- token_delete_cascade
-- depends: 20231121_02_1uZXT-deleted-tag


ALTER TABLE tokens
	DROP CONSTRAINT account_fk_id ,
	ADD CONSTRAINT account_fk_id FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE;
