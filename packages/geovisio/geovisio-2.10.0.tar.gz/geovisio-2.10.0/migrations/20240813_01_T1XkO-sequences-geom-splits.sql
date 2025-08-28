-- sequences_geom_splits
-- depends: 20240801_01_uKqPo-remove-files-delete-cascade

-- Change sequence split value to 75 meters (distance made at 135km/h during two seconds)
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
	-- make a multiline geometry for the sequence, spliting each pictures separated by more than 75 meters
	, seq_geom as (
		SELECT
			seq_id,
			ST_LineMerge(ST_Collect(segment)) as geom
		FROM segments
		WHERE ST_Length(segment::geography) <= 75
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

-- Update sequences geometries
DROP TRIGGER sequences_update_ts_trg ON sequences;

UPDATE sequences 
SET geom = compute_sequence_geom(id)
WHERE ST_NumGeometries(geom) > 1;

-- Restore all deactivated triggers
CREATE TRIGGER sequences_update_ts_trg
BEFORE UPDATE ON sequences
FOR EACH ROW
EXECUTE FUNCTION sequences_update_ts();
