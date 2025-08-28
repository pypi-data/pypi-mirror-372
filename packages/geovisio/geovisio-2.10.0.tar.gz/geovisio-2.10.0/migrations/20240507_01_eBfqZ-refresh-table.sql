-- refresh_table
-- depends: 20240409_01_jnhra-pictures-grid  20240416_02_A5KzC-fill-pictures-stats-on-sequences


CREATE TABLE refresh_database(
	refreshed_at TIMESTAMPTZ
);

INSERT INTO refresh_database(refreshed_at) VALUES (null);