-- sequences-summary
-- depends: 20230711_01_JGSPB-inserted-at-index

-- Add columns in sequences table for summary based on pictures
ALTER TABLE sequences
ADD COLUMN computed_type VARCHAR,
ADD COLUMN computed_model VARCHAR,
ADD COLUMN computed_capture_date DATE;

-- Create data for existing sequences
UPDATE sequences s
SET
	computed_type = CASE WHEN array_length(types, 1) = 1 THEN types[1] ELSE NULL END,
	computed_model = CASE WHEN array_length(models, 1) = 1 THEN models[1] ELSE NULL END,
	computed_capture_date = p.day
FROM (
	SELECT
		sp.seq_id,
		MIN(p.ts::DATE) AS day,
		ARRAY_AGG(DISTINCT TRIM(CONCAT(p.metadata->>'make', ' ', p.metadata->>'model'))) AS models,
		ARRAY_AGG(DISTINCT p.metadata->>'type') AS types
	FROM sequences_pictures sp
	JOIN pictures p ON sp.pic_id = p.id
	GROUP BY sp.seq_id
) p
WHERE s.id = p.seq_id; -- NOTE : this fix was added on 2023-08-03 (after original migration release)
