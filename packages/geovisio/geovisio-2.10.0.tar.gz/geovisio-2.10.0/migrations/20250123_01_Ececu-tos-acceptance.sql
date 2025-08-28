-- tos_acceptance
-- depends: 20250109_01_4OOP4-pages  20250114_01_ABaaL-collaborative-metadata-editing

ALTER TABLE accounts ADD COLUMN tos_accepted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE accounts ADD COLUMN tos_accepted BOOLEAN GENERATED ALWAYS AS (tos_accepted_at IS NOT NULL) STORED;
