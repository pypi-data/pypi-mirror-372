-- rm-metadata-duplicates
-- depends: 20221222_01_fsB6f-add-account

UPDATE pictures
SET metadata = metadata - '{lat,lon,ts,heading}'::text[];
