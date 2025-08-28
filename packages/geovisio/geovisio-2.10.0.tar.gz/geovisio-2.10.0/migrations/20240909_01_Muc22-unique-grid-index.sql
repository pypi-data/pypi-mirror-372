-- unique_grid_index
-- depends: 20240902_01_MDqSj-user-agent  20240905_01_C8F6U-conflicts

-- a unique index is necessary to be able to refresh the view concurrently
CREATE UNIQUE INDEX ON pictures_grid(id);
