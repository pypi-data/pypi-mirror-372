-- compute_heading_0
-- depends: 20230615_01_u7aRf-pic-delete-cascade

-- compute all heading that was set to 0
WITH h AS (
	SELECT p.id,
		CASE
			WHEN LEAD(sp.rank) OVER othpics IS NULL AND LAG(sp.rank) OVER othpics IS NULL THEN 
				NULL
			WHEN LEAD(sp.rank) OVER othpics IS NULL THEN (
				360 + FLOOR(DEGREES(ST_Azimuth(LAG(p.geom) OVER othpics, p.geom)))::int + (0 % 360)) % 360
			ELSE (
				360 + FLOOR(DEGREES(ST_Azimuth(p.geom, LEAD(p.geom) OVER othpics)))::int + (0 % 360)) % 360
		END AS heading
	FROM pictures p
	JOIN sequences_pictures sp ON sp.pic_id = p.id
	WINDOW othpics AS (
		PARTITION BY sp.seq_id
		ORDER BY sp.rank
	)
)
UPDATE pictures p
SET heading = h.heading, heading_computed = true
FROM h
WHERE h.id = p.id
	AND ((p.heading IS NULL OR p.heading = 0) AND NOT p.heading_computed)
;
