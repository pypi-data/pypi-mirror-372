-- exclusion-zones
-- depends: 20240801_01_DOqmf-reports  20240801_01_uKqPo-remove-files-delete-cascade

-- Excluded areas
CREATE TABLE excluded_areas(
	id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
	label VARCHAR,
	is_public BOOLEAN NOT NULL DEFAULT false,
	account_id UUID REFERENCES accounts(id),
	geom GEOMETRY(MultiPolygon, 4326) NOT NULL
);

COMMENT ON COLUMN excluded_areas.is_public IS 'Public excluded area mean it will appear on coverage map. Excluded areas related to private property, military use or user-specific filtering should not be public.';
COMMENT ON COLUMN excluded_areas.account_id IS 'User ID this excluded area only applies for.';

CREATE INDEX excluded_areas_geom_idx ON excluded_areas USING GIST(geom);
CREATE INDEX ecluded_areas_account_id_idx ON excluded_areas(account_id);


-- Pictures check on insert/update
CREATE OR REPLACE FUNCTION is_picture_in_excluded_area()
RETURNS TRIGGER AS $$
DECLARE
    eaid UUID;
    acid UUID;
BEGIN
    -- General excluded areas
    SELECT ea.id, ea.account_id INTO eaid, acid
    FROM excluded_areas ea
    WHERE ST_Contains(ea.geom, NEW.geom)
    AND (ea.account_id IS NULL OR ea.account_id = NEW.account_id)
    ORDER BY ea.account_id NULLS FIRST
    LIMIT 1;
    IF eaid IS NOT NULL THEN
        IF acid IS NOT NULL THEN
            RAISE invalid_parameter_value USING MESSAGE = 'The picture is located within one of your own excluded area.';
        ELSE
            RAISE invalid_parameter_value USING MESSAGE = 'The picture is located within a general excluded area.';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER pictures_excluded_areas_trg
BEFORE INSERT OR UPDATE OF geom ON pictures
FOR EACH ROW
EXECUTE FUNCTION is_picture_in_excluded_area();
