"""
Camera metadata
"""

from yoyo import step
import json

__depends__ = {"20221201_01_wpCGc-initial-schema"}

# NOTE : cameras / sensor_data is not used anymore in versions > 2.7.1
#       For updating cameras metadata, please see GeoPicture Tag Reader repository


def _read_models():
    from pathlib import Path

    with open(Path(__file__).parent / "data" / "sensor_data.json", "r") as f:
        sensorsJson = json.loads(f.read())
        return sensorsJson


def apply_step(conn):
    with conn.cursor() as cursor:
        cursor.execute(
            """
CREATE TABLE cameras(
	model VARCHAR PRIMARY KEY,
	sensor_width FLOAT NOT NULL
);

CREATE INDEX cameras_model_idx ON cameras USING GIST(model gist_trgm_ops);
"""
        )
        print("Initializing cameras metadata...")

        sensorsJson = _read_models()

        with cursor.copy("COPY cameras(model, sensor_width) FROM STDIN") as copy:
            for sensor in sensorsJson.items():
                copy.write_row(sensor)
            print("Cameras metadata initialized")


def rollback_step(conn):
    with conn.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS cameras;")


steps = [step(apply_step, rollback_step)]
