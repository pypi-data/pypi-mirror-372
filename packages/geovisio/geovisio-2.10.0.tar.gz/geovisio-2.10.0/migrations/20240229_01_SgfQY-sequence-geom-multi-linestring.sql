-- sequence_geom_multi_linestring
-- depends: 20240220_01_9wZs0-sequence-current-sort

ALTER TABLE sequences 
	ALTER COLUMN geom TYPE GEOMETRY(MultiLineString, 4326) USING ST_Multi(geom),
	-- Since some geometries can now be null (if all points are too far appart)
	-- We store a bounding box of the geometry, always computed with the pictures of the geometry
	ADD COLUMN IF NOT EXISTS bbox box2d;

CREATE FUNCTION compute_sequence_geom(IN sequence_id UUID) RETURNS GEOMETRY(MultiLineString, 4326) AS $$
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


CREATE FUNCTION compute_sequence_bbox(IN sequence_id UUID) RETURNS box2d AS $$
	SELECT
		ST_Extent(geom)
	FROM sequences_pictures sp
	JOIN pictures p ON sp.pic_id = p.id
	WHERE sp.seq_id = sequence_id;
$$ LANGUAGE SQL IMMUTABLE PARALLEL SAFE;


-- update bbox in sequences
UPDATE sequences
	SET
		bbox = compute_sequence_bbox(id);

-- change sql function called by trigger on picture's geom update
DROP FUNCTION IF EXISTS pictures_update_geom_sequence CASCADE;
CREATE FUNCTION pictures_update_geom_sequence() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET
		geom = compute_sequence_geom(id),
		bbox = compute_sequence_bbox(id)
	WHERE id IN (
		SELECT DISTINCT sequences_pictures.seq_id
		FROM sequences_pictures
		WHERE sequences_pictures.pic_id = NEW.id
	);

	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_update_sequences_geom_trg
AFTER UPDATE OF geom ON pictures
FOR EACH ROW EXECUTE FUNCTION pictures_update_geom_sequence();

DROP FUNCTION IF EXISTS sequences_pictures_delete CASCADE;
CREATE FUNCTION sequences_pictures_delete() RETURNS trigger AS $$
BEGIN
	UPDATE sequences
	SET
		geom = compute_sequence_geom(id),
		bbox = compute_sequence_bbox(id)
	WHERE id IN (SELECT DISTINCT seq_id FROM old_table);

	RETURN NULL;
END $$ LANGUAGE plpgsql;

CREATE TRIGGER sequences_pictures_delete_trg
AFTER DELETE ON sequences_pictures
REFERENCING OLD TABLE AS old_table
FOR EACH STATEMENT EXECUTE FUNCTION sequences_pictures_delete();
