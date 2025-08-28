-- computed_headings
-- depends: 20230324_02_efgI6-picture-process

-- We need to be able to tell if the heading have been computed or given as input

ALTER TABLE pictures ADD COLUMN IF NOT EXISTS heading_computed BOOLEAN NOT NULL DEFAULT false;
