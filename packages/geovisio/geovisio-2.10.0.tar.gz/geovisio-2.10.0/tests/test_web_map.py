import os
import pytest
import mapbox_vector_tile

from geovisio.web import map
from geovisio import errors
from . import conftest
from geovisio.utils import sequences


FIXTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


def test_getStyle(client):
    response = client.get("/api/map/style.json")
    assert response.status_code == 200
    assert response.json == {
        "version": 8,
        "name": "Panoramax",
        "metadata": {
            "panoramax:fields": {
                "sequences": ["id", "account_id", "model", "type", "date", "gps_accuracy", "h_pixel_density"],
                "pictures": ["id", "account_id", "ts", "heading", "sequences", "type", "model", "gps_accuracy", "h_pixel_density"],
                "grid": ["id", "nb_pictures", "nb_360_pictures", "nb_flat_pictures", "coef", "coef_360_pictures", "coef_flat_pictures"],
            }
        },
        "sources": {
            "geovisio": {"type": "vector", "tiles": ["http://localhost:5000/api/map/{z}/{x}/{y}.mvt"], "minzoom": 0, "maxzoom": 15}
        },
        "layers": [
            {
                "id": "geovisio_sequences",
                "type": "line",
                "source": "geovisio",
                "source-layer": "sequences",
                "paint": {
                    "line-color": "#FF6F00",
                    "line-width": ["interpolate", ["linear"], ["zoom"], 0, 0.5, 10, 2, 14, 4, 16, 5, 22, 3],
                    "line-opacity": ["interpolate", ["linear"], ["zoom"], 6.25, 0, 7, 1],
                },
                "layout": {
                    "line-cap": "square",
                },
            },
            {
                "id": "geovisio_pictures",
                "type": "circle",
                "source": "geovisio",
                "source-layer": "pictures",
                "paint": {
                    "circle-color": "#FF6F00",
                    "circle-radius": ["interpolate", ["linear"], ["zoom"], 15, 4.5, 17, 8, 22, 12],
                    "circle-opacity": ["interpolate", ["linear"], ["zoom"], 15, 0, 16, 1],
                    "circle-stroke-color": "#ffffff",
                    "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 17, 0, 20, 2],
                },
            },
            {
                "id": "geovisio_grid",
                "type": "circle",
                "source": "geovisio",
                "source-layer": "grid",
                "layout": {
                    "circle-sort-key": ["get", "coef"],
                },
                "paint": {
                    "circle-radius": [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        1,
                        ["match", ["get", "coef"], 0, 0, 1],
                        6 - 2,
                        ["match", ["get", "coef"], 0, 0, 6],
                        6 - 1,
                        ["match", ["get", "coef"], 0, 0, 2.5],
                        6,
                        ["match", ["get", "coef"], 0, 0, 4],
                        6 + 1,
                        ["match", ["get", "coef"], 0, 0, 7],
                    ],
                    "circle-color": ["interpolate", ["linear"], ["get", "coef"], 0, "#FFA726", 0.5, "#E65100", 1, "#3E2723"],
                    "circle-opacity": [
                        "interpolate",
                        ["linear"],
                        ["zoom"],
                        6 - 2,
                        0.5,
                        6 - 1,
                        1,
                        6 + 0.75,
                        1,
                        6 + 1,
                        0,
                    ],
                },
            },
        ],
    }


@conftest.SEQ_IMG
def test_getUserStyle(datafiles, initSequenceApp, bobAccountID):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        response = client.get(f"/api/users/{str(bobAccountID)}/map/style.json")
        assert response.status_code == 200
        assert response.json == {
            "version": 8,
            "name": "Panoramax",
            "metadata": {
                "panoramax:fields": {
                    "sequences": ["id", "account_id", "model", "type", "date", "gps_accuracy", "h_pixel_density"],
                    "pictures": ["id", "account_id", "ts", "heading", "sequences", "type", "model", "gps_accuracy", "h_pixel_density"],
                }
            },
            "sources": {
                f"geovisio_{str(bobAccountID)}": {
                    "type": "vector",
                    "tiles": ["http://localhost:5000/api/users/" + str(bobAccountID) + "/map/{z}/{x}/{y}.mvt"],
                    "minzoom": 0,
                    "maxzoom": 15,
                }
            },
            "layers": [
                {
                    "id": f"geovisio_{str(bobAccountID)}_sequences",
                    "type": "line",
                    "source": f"geovisio_{str(bobAccountID)}",
                    "source-layer": "sequences",
                    "paint": {
                        "line-color": "#FF6F00",
                        "line-width": ["interpolate", ["linear"], ["zoom"], 0, 0.5, 10, 2, 14, 4, 16, 5, 22, 3],
                        "line-opacity": 1,
                    },
                    "layout": {
                        "line-cap": "square",
                    },
                },
                {
                    "id": f"geovisio_{str(bobAccountID)}_pictures",
                    "type": "circle",
                    "source": f"geovisio_{str(bobAccountID)}",
                    "source-layer": "pictures",
                    "paint": {
                        "circle-color": "#FF6F00",
                        "circle-radius": ["interpolate", ["linear"], ["zoom"], 15, 4.5, 17, 8, 22, 12],
                        "circle-opacity": ["interpolate", ["linear"], ["zoom"], 15, 0, 16, 1],
                        "circle-stroke-color": "#ffffff",
                        "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 17, 0, 20, 2],
                    },
                },
            ],
        }


@conftest.SEQ_IMG
def test_getMyStyle(app, client, defaultAccountToken):
    response = client.get("/api/users/me/map/style.json", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 200
    assert response.json == {
        "version": 8,
        "name": "Panoramax",
        "metadata": {
            "panoramax:fields": {
                "sequences": ["id", "account_id", "model", "type", "date", "gps_accuracy", "h_pixel_density"],
                "pictures": ["id", "account_id", "ts", "heading", "sequences", "type", "model", "gps_accuracy", "h_pixel_density"],
            }
        },
        "sources": {
            "geovisio_me": {
                "type": "vector",
                "tiles": ["http://localhost:5000/api/users/me/map/{z}/{x}/{y}.mvt"],
                "minzoom": 0,
                "maxzoom": 15,
            }
        },
        "layers": [
            {
                "id": "geovisio_me_sequences",
                "type": "line",
                "source": "geovisio_me",
                "source-layer": "sequences",
                "paint": {
                    "line-color": "#FF6F00",
                    "line-width": ["interpolate", ["linear"], ["zoom"], 0, 0.5, 10, 2, 14, 4, 16, 5, 22, 3],
                    "line-opacity": 1,
                },
                "layout": {
                    "line-cap": "square",
                },
            },
            {
                "id": "geovisio_me_pictures",
                "type": "circle",
                "source": "geovisio_me",
                "source-layer": "pictures",
                "paint": {
                    "circle-color": "#FF6F00",
                    "circle-radius": ["interpolate", ["linear"], ["zoom"], 15, 4.5, 17, 8, 22, 12],
                    "circle-opacity": ["interpolate", ["linear"], ["zoom"], 15, 0, 16, 1],
                    "circle-stroke-color": "#ffffff",
                    "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 17, 0, 20, 2],
                },
            },
        ],
    }


@pytest.mark.parametrize(
    ("z", "x", "y", "format", "result"),
    (
        (6, 0, 0, "mvt", True),
        (6, 0, 1, "mvt", True),
        (6, 1, 0, "mvt", True),
        (6, 1, 1, "mvt", True),
        (-1, 0, 0, "mvt", 404),
        (16, 0, 0, "mvt", 404),
        (6, -1, 0, "mvt", 404),
        (6, 64, 0, "mvt", 404),
        (6, 0, -1, "mvt", 404),
        (6, 0, 64, "mvt", 404),
        (6, 0, 0, "jpg", 400),
        (None, 0, 0, "jpg", 400),
        (6, None, 0, "jpg", 400),
        (6, 0, None, "jpg", 400),
        (6, 0, 0, None, 400),
    ),
)
def test_isTileValid(z, x, y, format, result):
    if result is True:
        map.checkTileValidity(z, x, y, format)
    else:
        with pytest.raises(errors.InvalidAPIUsage) as e_info:
            map.checkTileValidity(z, x, y, format)
            assert e_info.value.status_code == result


@conftest.SEQ_IMGS
@pytest.mark.parametrize(
    ("z", "x", "y", "layersCount"),
    (
        (14, 8279, 5626, {"sequences": 1}),  # pictures are shown from zoom 15
        (15, 16558, 11252, {"pictures": 5, "sequences": 1}),
        (11, 1034, 703, {"sequences": 1}),
        (11, 0, 0, {}),
        (6, 32, 21, {"grid": 1}),  # No sequences due to simplification
        (5, 16, 10, {"grid": 1}),
        (0, 0, 0, {"grid": 1}),
    ),
)
def test_getTile(datafiles, initSequenceApp, dburl, z, x, y, layersCount):
    with initSequenceApp(datafiles, preprocess=False) as client:

        if "grid" in layersCount:
            sequences.update_pictures_grid()

        response = client.get(f"/api/map/{z}/{x}/{y}.mvt")

        assert response.status_code == 200
        data = mapbox_vector_tile.decode(response.get_data())

        for layerName, layerCount in layersCount.items():
            assert layerName in data
            assert len(data[layerName]["features"]) == layerCount
            # all pictures and sequence should be set as visible
            for f in data[layerName]["features"]:
                if layerName == "grid":
                    assert "id" in f["properties"]
                    assert "nb_pictures" in f["properties"]
                    assert "nb_360_pictures" in f["properties"]
                    assert "nb_flat_pictures" in f["properties"]
                    assert "coef" in f["properties"]
                    assert "coef_360_pictures" in f["properties"]
                    assert "coef_flat_pictures" in f["properties"]
                else:
                    assert "hidden" not in f["properties"]  # if hidden is not in properties, it means it's visible
                    # all pictures and sequence should have an accountId
                    assert "account_id" in f["properties"]
                    assert f["properties"].get("model") == "GoPro Max"
                    assert f["properties"].get("type") == "equirectangular"
                    assert f["properties"].get("h_pixel_density") == 16
                    assert f["properties"].get("gps_accuracy") == 4

                    if layerName == "sequences":
                        assert f["properties"].get("date") == "2021-07-29"
                    else:
                        assert f["properties"].get("ts").startswith("2021-07-29")
                        assert f["properties"].get("first_sequence") is not None


def _get_prop_by_id(geoj):
    res = {}
    for t in ["pictures", "sequences"]:
        res[t] = {t["properties"]["id"]: t["properties"] for t in geoj.get(t, {}).get("features", [])}
    return res


def _get_tiles_data(response):
    assert response.status_code == 200
    data = mapbox_vector_tile.decode(response.get_data())
    return data, {
        "nb_pic": len(data.get("pictures", {}).get("features", [])),
        "nb_seq": len(data.get("sequences", {}).get("features", [])),
        "nb_grid": len(data.get("grid", {}).get("features", [])),
    }


@conftest.SEQ_IMGS
def test_getTile_hidden(datafiles, initSequenceApp, dburl, bobAccountToken, bobAccountID):
    with initSequenceApp(datafiles, preprocess=False, withBob=True) as client:
        sequence = conftest.getPictureIds(dburl)[0]

        def _get_general_tiles_features(asBob: bool):
            headers = {"Authorization": f"Bearer {bobAccountToken()}"} if asBob else {}
            response = client.get("/api/map/15/16558/11252.mvt", headers=headers)
            # the tiles can be cached by a shared cache as they do not contain any user data
            assert response.headers.get("Cache-Control") == "public"
            return _get_tiles_data(response)

        def _get_bob_tiles_features(asBob: bool):
            headers = {"Authorization": f"Bearer {bobAccountToken()}"} if asBob else {}
            response = client.get(f"/api/users/{bobAccountID}/map/15/16558/11252.mvt", headers=headers)
            if asBob:
                # the tiles cannot be cached by a shared cache as they do not contain user's specific data
                assert response.headers.get("Cache-Control") == "private"
            else:
                # the tiles can be cached by a shared cache as they do not contain any user data
                assert response.headers.get("Cache-Control") == "public"
            return _get_tiles_data(response)

        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        # since there are only bob's data, getting bob's tile should return all tiles
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        assert _get_bob_tiles_features(asBob=True)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}

        # we hide a picture
        response = client.patch(
            f"/api/collections/{str(sequence.id)}/items/{str(sequence.pictures[0].id)}",
            data={"visible": "false"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200

        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        # even the owner shouldn't see it in the generic tiles
        assert _get_general_tiles_features(asBob=True)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        # but they should be in the user's tiles, only if it's bob whose asking
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        t, stats = _get_bob_tiles_features(asBob=True)
        assert stats == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        all_props = _get_prop_by_id(t)
        assert all_props["pictures"][str(sequence.pictures[0].id)]["hidden"] is True
        for p in sequence.pictures[1:]:
            assert "hidden" not in all_props["pictures"][str(p.id)]

        # we hide the whole sequence
        response = client.patch(
            f"/api/collections/{str(sequence.id)}", data={"visible": "false"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 200

        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        # same, even the owner shouldn't see it in the generic tiles
        assert _get_general_tiles_features(asBob=True)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        # but they should be in the user's tiles, only if it's bob whose asking
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        t, stats = _get_bob_tiles_features(asBob=True)
        assert stats == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        all_props = _get_prop_by_id(t)
        assert all_props["sequences"][str(sequence.id)]["hidden"] is True
        for p in sequence.pictures:
            assert all_props["pictures"][str(p.id)]["hidden"] is True

        # we unhide the sequence
        response = client.patch(
            f"/api/collections/{str(sequence.id)}", data={"visible": "true"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )

        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        assert _get_general_tiles_features(asBob=True)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        # but they should be in the user's tiles, only if it's bob whose asking
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 4, "nb_seq": 1, "nb_grid": 0}
        t, stats = _get_bob_tiles_features(asBob=True)
        all_props = _get_prop_by_id(t)
        assert "hidden" not in all_props["sequences"][str(sequence.id)]
        assert all_props["pictures"][str(sequence.pictures[0].id)]["hidden"] is True
        for p in sequence.pictures[1:]:
            assert "hidden" not in all_props["pictures"][str(p.id)]

        # we unhide the picture
        response = client.patch(
            f"/api/collections/{str(sequence.id)}/items/{str(sequence.pictures[0].id)}",
            data={"visible": "true"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200
        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        assert _get_general_tiles_features(asBob=True)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}
        assert _get_bob_tiles_features(asBob=True)[1] == {"nb_pic": 5, "nb_seq": 1, "nb_grid": 0}

        # if we delete the sequence, nobody should see nothing anymore
        response = client.delete(
            f"/api/collections/{str(sequence.id)}",
            data={"visible": "true"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 204
        assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        assert _get_general_tiles_features(asBob=True)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        assert _get_bob_tiles_features(asBob=False)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
        assert _get_bob_tiles_features(asBob=True)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}


def test_get_user_Tiles(app, client, dburl, bobAccountToken, bobAccountID, defaultAccountID, defaultAccountToken):
    """Load 1 sequence as a 'bob' and one as 'default_account' and check that each user's tile correctly return only owned data"""

    import pathlib

    datadir = pathlib.Path(FIXTURE_DIR)

    conftest.uploadSequenceFromPics(
        test_client=client,
        title="bob's sequence",
        wait=True,
        jwtToken=bobAccountToken(),
        pics=[
            datadir / "1.jpg",
            datadir / "2.jpg",
            datadir / "3.jpg",
        ],
    )
    conftest.uploadSequenceFromPics(
        test_client=client,
        title="default account sequence",
        wait=True,
        jwtToken=defaultAccountToken(),
        pics=[
            datadir / "4.jpg",
            datadir / "5.jpg",
        ],
    )

    def _get_general_tiles_features(asBob: bool):
        headers = {"Authorization": f"Bearer {bobAccountToken()}"} if asBob else {}
        response = client.get("/api/map/14/8279/5626.mvt", headers=headers)
        return _get_tiles_data(response)

    def _get_user_tiles_features(id, token_func=None, query_params=""):
        headers = {"Authorization": f"Bearer {token_func()}"} if token_func else {}
        response = client.get(f"/api/users/{id}/map/14/8279/5626.mvt{query_params}", headers=headers)
        return _get_tiles_data(response)

    # zoom 14 does not contains pictures anymore, they are shown from zoom 15
    assert _get_general_tiles_features(asBob=False)[1] == {"nb_pic": 0, "nb_seq": 2, "nb_grid": 0}
    assert _get_user_tiles_features(bobAccountID, None)[1] == {"nb_pic": 0, "nb_seq": 1, "nb_grid": 0}
    assert _get_user_tiles_features(bobAccountID, bobAccountToken)[1] == {"nb_pic": 0, "nb_seq": 1, "nb_grid": 0}
    assert _get_user_tiles_features(defaultAccountID, None)[1] == {"nb_pic": 0, "nb_seq": 1, "nb_grid": 0}
    assert _get_user_tiles_features(defaultAccountID, defaultAccountToken)[1] == {"nb_pic": 0, "nb_seq": 1, "nb_grid": 0}

    def _get_lower_general_tiles_features(asBob: bool):
        headers = {"Authorization": f"Bearer {bobAccountToken()}"} if asBob else {}
        response = client.get("/api/map/15/16558/11252.mvt", headers=headers)
        return _get_tiles_data(response)

    def _get_lower_user_tiles_features(id, token_func=None, query_params=""):
        headers = {"Authorization": f"Bearer {token_func()}"} if token_func else {}
        response = client.get(f"/api/users/{id}/map/15/16558/11252.mvt{query_params}", headers=headers)
        return _get_tiles_data(response)

    assert _get_lower_general_tiles_features(asBob=False)[1] == {"nb_pic": 5, "nb_seq": 2, "nb_grid": 0}
    assert _get_lower_user_tiles_features(bobAccountID, None)[1] == {"nb_pic": 3, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(bobAccountID, bobAccountToken)[1] == {"nb_pic": 3, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(defaultAccountID, None)[1] == {"nb_pic": 2, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(defaultAccountID, defaultAccountToken)[1] == {"nb_pic": 2, "nb_seq": 1, "nb_grid": 0}
    # we can also hide bob's seqence and 1 pic from the default account's sequence
    sequence = conftest.getPictureIds(dburl)
    response = client.patch(
        f"/api/collections/{str(sequence[0].id)}",
        data={"visible": "false"},
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 200
    response = client.patch(
        f"/api/collections/{str(sequence[1].id)}/items/{str(sequence[1].pictures[0].id)}",
        data={"visible": "false"},
        headers={"Authorization": f"Bearer {defaultAccountToken()}"},
    )
    assert response.status_code == 200

    # only one sequence is visible for everybody
    assert _get_lower_general_tiles_features(asBob=False)[1] == {"nb_pic": 1, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(bobAccountID, None)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
    assert _get_lower_user_tiles_features(bobAccountID, bobAccountToken)[1] == {"nb_pic": 3, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(defaultAccountID, None)[1] == {"nb_pic": 1, "nb_seq": 1, "nb_grid": 0}
    assert _get_lower_user_tiles_features(defaultAccountID, defaultAccountToken)[1] == {"nb_pic": 2, "nb_seq": 1, "nb_grid": 0}

    # and we can only get the hidden pic when adding the `?filter=status=hidden` if queried by the author
    # the query param is only available for user's specific tiles
    only_hidden = "?filter=status='hidden'"

    assert _get_lower_user_tiles_features(bobAccountID, None, query_params=only_hidden)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}
    assert _get_lower_user_tiles_features(bobAccountID, bobAccountToken, query_params=only_hidden)[1] == {
        "nb_pic": 3,
        "nb_seq": 1,
        "nb_grid": 0,
    }
    # asking for only hidden when we don't have the rights to see them result in 0 pics shown
    assert _get_lower_user_tiles_features(defaultAccountID, None, query_params=only_hidden)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 0}

    assert _get_lower_user_tiles_features(defaultAccountID, defaultAccountToken, query_params=only_hidden)[1] == {
        "nb_pic": 1,
        "nb_seq": 0,
        "nb_grid": 0,
    }

    # there are also shortcut to get one's tiles
    response = client.get("/api/users/me/map/15/16558/11252.mvt", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
    assert response.status_code == 200
    assert _get_tiles_data(response)[1] == {"nb_pic": 2, "nb_seq": 1, "nb_grid": 0}
    response = client.get(
        f"/api/users/me/map/15/16558/11252.mvt{only_hidden}", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
    )
    assert response.status_code == 200
    assert _get_tiles_data(response)[1] == {"nb_pic": 1, "nb_seq": 0, "nb_grid": 0}


def test_get_user_Tiles_higher_zoom(app, client, dburl, bobAccountToken, bobAccountID):
    """Load 1 sequence with far points, not to simplified at higher zoom level"""

    import pathlib

    datadir = pathlib.Path(FIXTURE_DIR)

    seq_location = conftest.createSequence(client, "seq1", jwtToken=bobAccountToken())
    initial_lon = 1.7
    initial_lat = 46
    step = 4 / 11111  # roughly 40m
    pics = [
        datadir / "1.jpg",
        datadir / "2.jpg",
        datadir / "3.jpg",
        datadir / "4.jpg",
        datadir / "5.jpg",
    ]

    for i, p in enumerate(pics * 3):  # load 15 points to have a geometry even avec simplification
        conftest.uploadPicture(
            client,
            seq_location,
            open(p, "rb"),
            p.name,
            i + 1,
            jwtToken=bobAccountToken(),
            overrides={"override_longitude": initial_lon + step * i, "override_latitude": initial_lat},
        )

    conftest.waitForSequence(client, seq_location)
    sequences.update_pictures_grid()

    sequence = conftest.getPictureIds(dburl)[0]
    response = client.get("/api/map/5/16/11.mvt", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 200
    t, stats = _get_tiles_data(response)
    # high zoom tile should not contains picture info
    assert _get_tiles_data(response)[1] == {"nb_pic": 0, "nb_seq": 0, "nb_grid": 2}
    all_props = _get_prop_by_id(t)

    response = client.get("/api/users/me/map/5/16/11.mvt", headers={"Authorization": f"Bearer {bobAccountToken()}"})
    assert response.status_code == 200
    t, stats = _get_tiles_data(response)
    # high zoom tile should not contains picture info
    assert _get_tiles_data(response)[1] == {"nb_pic": 0, "nb_seq": 1, "nb_grid": 0}
    all_props = _get_prop_by_id(t)

    # we get more info, even at higher zoom
    assert all_props["sequences"][str(sequence.id)] == {
        "id": sequence.id,
        "account_id": str(bobAccountID),
        "date": "2021-07-29",
        "model": "GoPro Max",
        "type": "equirectangular",
        "h_pixel_density": 16,
        "gps_accuracy": 4,
    }
