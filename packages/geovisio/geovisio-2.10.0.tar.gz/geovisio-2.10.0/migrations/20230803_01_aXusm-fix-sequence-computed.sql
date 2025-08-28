-- fix-sequence-computed
-- depends: 20230720_01_EyQ0e-sequences-summary

-- Fix for invalid migration 20230720_01_EyQ0e-sequences-summary
--   which lacked "WHERE" condition on its initial release
-- This new migration ensures already migrated instances
--   also get the fix for their database.
-- New instances will just play two times the same fixed
--   SQL request, which is not so bad after all...
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
WHERE s.id = p.seq_id;
