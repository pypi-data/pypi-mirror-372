-- sequence_geom_multi_linestring
-- depends: 20240220_01_9wZs0-sequence-current-sort

CREATE OR REPLACE FUNCTION compute_sequence_geom(IN sequence_id UUID) RETURNS GEOMETRY(MultiLineString, 4326) AS $$
	WITH
	all_pics AS (
		SELECT p.geom AS geom, sp.seq_id
		FROM sequences_pictures sp
		JOIN pictures p ON sp.pic_id = p.id
		WHERE sp.seq_id = sequence_id
		ORDER BY sp.rank
	)
	, pic_as_line AS (
		SELECT seq_id, ST_MakeLine(geom) AS geom
		FROM all_pics
		GROUP BY seq_id
	)
	, segments as (
		SELECT
			seq_id,
			(ST_DumpSegments(geom)).geom AS segment
		FROM pic_as_line
	)
	-- make a multiline geometry for the sequence, spliting each pictures separated by more than 50 meters
	, seq_geom as (
		SELECT
			seq_id,
			ST_LineMerge(ST_Collect(segment)) as geom
		FROM segments
		WHERE ST_Length(segment::geography) < 50
		GROUP BY seq_id
	) 
	, seq_multi_ls_geom as (
		SELECT
			seq_id,
			ST_Multi(geom) as geom
		FROM seq_geom
		WHERE NOT ST_IsEmpty(geom)
	)
	SELECT seq_multi_ls_geom.geom
	FROM seq_multi_ls_geom;
$$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE;