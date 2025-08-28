-- rejection_details
-- depends: 20241004_01_d1zfe-pictures-grid-360  20241017_01_RiFlm-pictures-to-delete

ALTER TABLE files ADD COLUMN rejection_details JSONB;
