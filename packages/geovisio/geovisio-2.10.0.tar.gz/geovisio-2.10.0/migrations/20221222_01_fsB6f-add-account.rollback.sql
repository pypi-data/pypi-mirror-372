-- add-account
-- depends: 20221201_02_ZG8AR-camera-information

ALTER TABLE pictures DROP CONSTRAINT account_fk_id;
ALTER TABLE pictures DROP COLUMN account_id;

DROP TABLE IF EXISTS accounts CASCADE;
