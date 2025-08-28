from tests import conftest
from tests.conftest import create_upload_set
from tests.conftest import add_files_to_upload_set
import pytest


AREA_NULL_ISLAND = {
    "type": "Feature",
    "properties": {"is_public": True, "label": "Null Island Neighboorhood"},
    "geometry": {"type": "Polygon", "coordinates": [[[-0.1, -0.1], [-0.1, 0.1], [0.1, 0.1], [0.1, -0.1], [-0.1, -0.1]]]},
}

AREA_BALARD = {
    "type": "Feature",
    "properties": {"is_public": False, "label": "Hexagone Balard"},
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[2.2785, 48.8345], [2.2820, 48.8345], [2.2820, 48.8365], [2.2785, 48.8365], [2.2785, 48.8345]]],
    },
}

AREA_SEQ = {
    "type": "Feature",
    "properties": {},
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [1.91922649674, 49.00690961335],
                [1.91912993722, 49.00690917349],
                [1.91919833355, 49.00685902933],
                [1.91922649674, 49.00690961335],
            ]
        ],
    },
}

AREA_SET1 = {"type": "FeatureCollection", "features": [AREA_NULL_ISLAND, AREA_BALARD]}

AREA_CAMILLE = {
    "type": "Feature",
    "properties": {},
    "geometry": {
        "type": "Polygon",
        "coordinates": [[[-1.9500, 48.3288], [-1.9479, 48.3288], [-1.9479, 48.3299], [-1.9500, 48.3299], [-1.9500, 48.3288]]],
    },
}


def _create_excluded_area(client, token, area, general=True):
    response = client.post(
        "/api/configuration/excluded_areas" if general else "/api/users/me/excluded_areas",
        json=area,
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200, response.text
    return response


@pytest.fixture
def areaNullIsland(client, defaultAccountToken):
    return _create_excluded_area(client, defaultAccountToken(), AREA_NULL_ISLAND)


@pytest.fixture
def areaBalard(client, defaultAccountToken):
    return _create_excluded_area(client, defaultAccountToken(), AREA_BALARD)


@pytest.fixture
def areaCamilleHouse(client, camilleAccountToken):
    return _create_excluded_area(client, camilleAccountToken(), AREA_CAMILLE, general=False)


def test_get_excluded_areas(client, defaultAccountToken, areaNullIsland, areaBalard):
    # Try to get only public areas
    response = client.get("/api/configuration/excluded_areas")
    assert response.status_code == 200, response.text
    assert response.headers.get("Content-Type") == "application/geo+json"
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 1
    assert r["features"][0]["properties"]["label"] == "Null Island Neighboorhood"
    assert r["features"][0]["properties"]["is_public"] is True

    # Try to get all areas unauthenticated
    response = client.get("/api/configuration/excluded_areas?all=true")
    assert response.status_code == 401, response.text

    # Try to get all areas authenticated
    response = client.get("/api/configuration/excluded_areas?all=true", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 200, response.text
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 2


def test_post_admin_excluded_areas_unauthorized_invalid(client, bobAccountToken, defaultAccountToken):
    # Unauthenticated
    response = client.post(
        "/api/configuration/excluded_areas",
        json=AREA_NULL_ISLAND,
        headers={
            "Content-Type": "application/geo+json",
        },
    )
    assert response.status_code == 403, response.text

    # Not admin
    response = client.post(
        "/api/configuration/excluded_areas",
        json=AREA_NULL_ISLAND,
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {bobAccountToken()}",
        },
    )
    assert response.status_code == 403, response.text

    # Wrong format
    response = client.post(
        "/api/configuration/excluded_areas",
        json={"bla": "bla"},
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )
    assert response.status_code == 400, response.text


def test_post_admin_excluded_areas(areaNullIsland):
    r = areaNullIsland.json
    assert r.get("type") == "Feature"
    assert r["properties"]["id"] is not None
    assert r["properties"]["is_public"] is True
    assert r["properties"]["label"] == "Null Island Neighboorhood"
    assert r["geometry"]["type"] == "MultiPolygon"
    assert len(r["geometry"]["coordinates"]) == 1
    assert r["geometry"]["coordinates"][0] == AREA_NULL_ISLAND["geometry"]["coordinates"]


def test_put_admin_excluded_areas_unauthorized_invalid(client, bobAccountToken, defaultAccountToken):
    # Unauthenticated
    response = client.put(
        "/api/configuration/excluded_areas",
        json=AREA_SET1,
        headers={
            "Content-Type": "application/geo+json",
        },
    )
    assert response.status_code == 403, response.text

    # Not admin
    response = client.put(
        "/api/configuration/excluded_areas",
        json=AREA_SET1,
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {bobAccountToken()}",
        },
    )
    assert response.status_code == 403, response.text

    # Invalid
    response = client.put(
        "/api/configuration/excluded_areas",
        json={"bla": "bla"},
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )
    assert response.status_code == 400, response.text


def test_put_admin_excluded_areas(client, defaultAccountToken, areaBalard, areaCamilleHouse):
    # Send new set of areas
    response = client.put(
        "/api/configuration/excluded_areas",
        json=AREA_SET1,
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )

    # Check response
    assert response.status_code == 200, response.text
    assert response.headers.get("Content-Type") == "application/geo+json"
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 3

    # Kept user-specific area
    a1 = r["features"][0]
    assert a1["geometry"]["coordinates"][0] == AREA_CAMILLE["geometry"]["coordinates"]

    # Has two uploaded areas
    a2 = r["features"][1]
    assert a2["geometry"]["coordinates"][0] == AREA_NULL_ISLAND["geometry"]["coordinates"]

    a3 = r["features"][2]
    assert a3["geometry"]["coordinates"][0] == AREA_BALARD["geometry"]["coordinates"]


def test_put_admin_excluded_areas_invert(client, defaultAccountToken, areaBalard, areaCamilleHouse):
    # Send new set of areas
    response = client.put(
        "/api/configuration/excluded_areas?invert=true",
        json=AREA_SET1,
        headers={
            "Content-Type": "application/geo+json",
            "Authorization": f"Bearer {defaultAccountToken()}",
        },
    )

    # Check response
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/geo+json"
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 2

    # Kept user-specific area
    a1 = r["features"][0]
    assert a1["geometry"]["coordinates"][0] == AREA_CAMILLE["geometry"]["coordinates"]

    # Has inverted allowed areas
    a2 = r["features"][1]
    assert a2["geometry"]["coordinates"] == [
        [
            [[-180.0, 90.0], [180.0, 90.0], [180.0, -90.0], [-180.0, -90.0], [-180.0, 90.0]],
            [[-0.1, -0.1], [0.1, -0.1], [0.1, 0.1], [-0.1, 0.1], [-0.1, -0.1]],
            [[2.2785, 48.8345], [2.282, 48.8345], [2.282, 48.8365], [2.2785, 48.8365], [2.2785, 48.8345]],
        ]
    ]


def test_delete_admin_excluded_areas(client, areaNullIsland, bobAccountToken, defaultAccountToken):
    areaId = areaNullIsland.json["properties"]["id"]

    # Unauthenticated
    response = client.delete(f"/api/configuration/excluded_areas/{areaId}")
    assert response.status_code == 403, response.text

    # Not admin
    response = client.delete(f"/api/configuration/excluded_areas/{areaId}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 403, response.text

    # Admin
    response = client.delete(f"/api/configuration/excluded_areas/{areaId}", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 204, response.text


def test_get_user_excluded_areas(client, defaultAccountToken, camilleAccountToken, areaNullIsland, areaBalard, areaCamilleHouse):
    # Try unauthenticated
    response = client.get("/api/users/me/excluded_areas")
    assert response.status_code == 403, response.text

    # Try user without areas
    response = client.get("/api/users/me/excluded_areas", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 200
    assert response.headers.get("Content-Type") == "application/geo+json"
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 0

    # Try user with areas
    response = client.get("/api/users/me/excluded_areas", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
    assert response.headers.get("Content-Type") == "application/geo+json"
    r = response.json
    assert r.get("type") == "FeatureCollection"
    assert len(r.get("features")) == 1
    assert r["features"][0]["properties"].get("label") is None
    assert r["features"][0]["properties"]["is_public"] is False
    assert r["features"][0]["geometry"]["coordinates"][0] == AREA_CAMILLE["geometry"]["coordinates"]


def test_post_user_excluded_areas_unauthorized_invalid(client, bobAccountToken):
    # Unauthenticated
    response = client.post(
        "/api/users/me/excluded_areas",
        json=AREA_NULL_ISLAND,
        headers={
            "Content-Type": "application/geo+json",
        },
    )
    assert response.status_code == 403, response.text

    # Invalid
    response = client.post(
        "/api/users/me/excluded_areas",
        json={"bla": "bla"},
        headers={"Content-Type": "application/geo+json", "Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 400, response.text


def test_post_user_excluded_areas(areaCamilleHouse):
    r = areaCamilleHouse.json
    assert r.get("type") == "Feature"
    assert r["properties"]["id"] is not None
    assert r["properties"]["is_public"] is False
    assert r["properties"].get("label") is None
    assert r["geometry"]["type"] == "MultiPolygon"
    assert len(r["geometry"]["coordinates"]) == 1
    assert r["geometry"]["coordinates"][0] == AREA_CAMILLE["geometry"]["coordinates"]


def test_delete_user_excluded_areas(client, areaCamilleHouse, camilleAccountToken, defaultAccountToken):
    areaId = areaCamilleHouse.json["properties"]["id"]

    # Unauthenticated
    response = client.delete(f"/api/users/me/excluded_areas/{areaId}")
    assert response.status_code == 403, response.text

    # Not owner
    response = client.delete(f"/api/users/me/excluded_areas/{areaId}", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 404, response.text

    # Owner
    response = client.delete(f"/api/users/me/excluded_areas/{areaId}", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
    assert response.status_code == 204, response.text


@conftest.SEQ_IMG
def test_upload_set_excluded_pictures(datafiles, client, defaultAccountToken):
    _create_excluded_area(client, defaultAccountToken(), AREA_SEQ)

    usid = create_upload_set(client, defaultAccountToken())
    response = add_files_to_upload_set(client, usid, datafiles / "1.jpg", defaultAccountToken(), raw_response=True)
    assert response.status_code == 400, response.text
    rjson = response.json
    assert rjson["message"] == "Picture has invalid metadata"
    assert rjson["details"]["error"] == "The picture is located within a general excluded area."


@conftest.SEQ_IMG
def test_collection_item_excluded_pictures(datafiles, client, defaultAccountToken):
    _create_excluded_area(client, defaultAccountToken(), AREA_SEQ)

    # Create collection
    r = client.post("/api/collections", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert r.status_code == 200
    cid = r.json["id"]

    # Try to post picture
    r = client.post(
        f"/api/collections/{cid}/items",
        headers={"Authorization": f"Bearer {defaultAccountToken()}", "Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "1.jpg").open("rb")},
    )

    assert r.status_code == 400, r.text
    rjson = r.json
    assert rjson["message"] == "Picture has invalid metadata"
    assert rjson["details"]["error"] == "The picture is located within a general excluded area."


@conftest.SEQ_IMG
def test_upload_set_user_excluded_pictures(datafiles, client, camilleAccountToken, defaultAccountToken):
    _create_excluded_area(client, camilleAccountToken(), AREA_SEQ, general=False)

    # Concerned user : not accepted
    usid = create_upload_set(client, camilleAccountToken())
    response = add_files_to_upload_set(client, usid, datafiles / "1.jpg", camilleAccountToken(), raw_response=True)
    assert response.status_code == 400, response.text
    rjson = response.json
    assert rjson["message"] == "Picture has invalid metadata"
    assert rjson["details"]["error"] == "The picture is located within one of your own excluded area."

    # Third-party user : no problem
    usid = create_upload_set(client, defaultAccountToken())
    response = add_files_to_upload_set(client, usid, datafiles / "1.jpg", defaultAccountToken(), raw_response=True)
    assert response.status_code == 202, response.text


@conftest.SEQ_IMG
def test_collection_item_user_excluded_pictures(datafiles, client, camilleAccountToken, defaultAccountToken):
    _create_excluded_area(client, camilleAccountToken(), AREA_SEQ, general=False)

    # Third-party user
    r = client.post("/api/collections", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert r.status_code == 200
    cid = r.json["id"]
    r = client.post(
        f"/api/collections/{cid}/items",
        headers={"Authorization": f"Bearer {defaultAccountToken()}", "Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "1.jpg").open("rb")},
    )
    assert r.status_code == 202, r.text

    # Concerned user
    r = client.post("/api/collections", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
    assert r.status_code == 200
    cid = r.json["id"]
    r = client.post(
        f"/api/collections/{cid}/items",
        headers={"Authorization": f"Bearer {camilleAccountToken()}", "Content-Type": "multipart/form-data"},
        data={"position": 1, "picture": (datafiles / "1.jpg").open("rb")},
    )

    assert r.status_code == 400, r.text
    rjson = r.json
    assert rjson["message"] == "Picture has invalid metadata"
    assert rjson["details"]["error"] == "The picture is located within one of your own excluded area."
