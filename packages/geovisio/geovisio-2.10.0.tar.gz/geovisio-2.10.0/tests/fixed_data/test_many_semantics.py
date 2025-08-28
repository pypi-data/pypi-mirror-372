import pytest
from flask import current_app
from .. import conftest

"""
Module for tests needing a lot of semantic annotations.

To reduce testing time, the data is loaded only once for all tests.

No tests should change the data!
"""


@pytest.fixture(scope="module")
def app(dburl, fs):
    with conftest.create_test_app(
        {
            "TESTING": True,
            "DB_URL": dburl,
            "FS_URL": None,
            "FS_TMP_URL": fs.tmp,
            "FS_PERMANENT_URL": fs.permanent,
            "FS_DERIVATES_URL": fs.derivates,
            "PICTURE_PROCESS_DERIVATES_STRATEGY": "ON_DEMAND",
            "SECRET_KEY": "a very secret key",
            "SERVER_NAME": "localhost:5000",
            "API_PICTURES_LICENSE_SPDX_ID": "etalab-2.0",
            "API_PICTURES_LICENSE_URL": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
        }
    ) as app:
        yield app


@pytest.fixture(scope="module")
def app_data(app):
    """
    Fixture returning an app's client with many sequences loaded.
    Data shouldn't be modified by tests as it will be shared by several tests
    """
    import pathlib

    datadir = pathlib.Path(conftest.FIXTURE_DIR)
    conftest.insert_db_model(
        conftest.ModelToInsert(
            upload_sets=[
                conftest.UploadSetToInsert(
                    semantics=["transport_mode=bike"],
                    sequences=[
                        conftest.SequenceToInsert(
                            title="sequence_1",
                            pictures=[
                                conftest.PictureToInsert(
                                    original_file_name="1.jpg", semantics=["osm|traffic_sign=yes", "osm|highway=traffic_signals"]
                                ),
                                conftest.PictureToInsert(
                                    original_file_name="2.jpg",
                                    semantics=[
                                        "osm|advertising=billboard",
                                        "osm|message=commercial",
                                        "wd|P31=Q623149",
                                        "hashtags=StreetArt",
                                        "hashtags=🥰",
                                    ],
                                    annotations=[
                                        conftest.TAnnotation(semantics=["osm|traffic_sign=yes"]),
                                    ],
                                ),
                                conftest.PictureToInsert(original_file_name="3.jpg"),
                            ],
                            semantics=["weather=sunny", "camera_support=bike"],
                        ),
                        conftest.SequenceToInsert(
                            title="sequence_2",
                            pictures=[
                                conftest.PictureToInsert(
                                    original_file_name="e1.jpg",
                                    annotations=[
                                        conftest.TAnnotation(
                                            semantics=[
                                                "osm|traffic_sign=yes",
                                                "detection_model[osm|traffic_sign=yes]=SGBlur/1.2.3",
                                                "osm|traffic_sign=FR:A15b",
                                                "detection_model[osm|traffic_sign=FR:A15b]=PanneauBiche/1.3.37",
                                            ]
                                        ),
                                        conftest.TAnnotation(
                                            semantics=[
                                                "osm|amenity=recycling",
                                                "osm|recycling_type=container",
                                                "wd|P31=Q4743886",
                                                "wd|P528=2.800L",
                                                "wd|P972[wd|P528]=https://www.contenur.fr/produits/apport-volontaire/colonnes-aeriennes",
                                                "weather=sunny",
                                                "hashtags=🥳",
                                                "hashtags=🥰",
                                                "hashtags=#StreetArt",
                                            ]
                                        ),
                                    ],
                                    semantics=["#=ILoveMapping"],
                                ),
                                conftest.PictureToInsert(original_file_name="e2.jpg"),
                                conftest.PictureToInsert(original_file_name="e3.jpg", semantics=["osm|traffic_sign=FR:A1a"]),
                            ],
                            semantics=["camera_support=hand"],
                        ),
                    ],
                )
            ]
        )
    )
    return app


@pytest.fixture(scope="function")
def client(app_data):
    with app_data.app_context(), app_data.test_client() as client:
        yield client


def get_images(response):
    assert response.status_code == 200, response.text
    return [i["properties"]["original_file:name"] for i in response.json["features"]]


def test_simple_search(client):
    r = client.get("/api/search?filter=\"semantics.osm|traffic_sign\"='yes'")
    # 1.jpg and e1.jpg has the tag on its semantic
    # 2.jpg has an annotation with the tag on its semantic
    assert set(get_images(r)) == {"1.jpg", "2.jpg", "e1.jpg"}


@pytest.mark.parametrize(
    ("filter", "expected_pics"),
    [
        # weather = sunny should get us all the pics from sequence_1 + e1
        ("filter=\"semantics.weather\"='sunny'", ["1.jpg", "2.jpg", "3.jpg", "e1.jpg"]),
        ("filter=\"semantics.osm|traffic_sign\" IN ('FR:A1a', 'FR:A15b', 'pouet')", ["e1.jpg", "e3.jpg"]),
        ("filter=\"semantics.hashtags\" = '🥰'", ["2.jpg", "e1.jpg"]),
        ('filter="semantics.hashtags" IS NOT NULL', ["2.jpg", "e1.jpg"]),  # we get all pictures with hashtags
        ("filter=\"semantics.transport_mode\"='bike'", ["1.jpg", "2.jpg", "3.jpg", "e1.jpg", "e2.jpg", "e3.jpg"]),
    ],
)
def test_simple_searchs(client, filter, expected_pics):
    r = client.get(f"/api/search?{filter}")
    # 1.jpg and e1.jpg has the tag on its semantic
    # 2.jpg has an annotation with the tag on its semantic
    assert set(get_images(r)) == set(expected_pics)


def test_combined_search(client, dburl):
    """We can still add the other filters"""
    seq = conftest.getPictureIds(dburl)
    r = client.get(f'/api/search?filter="semantics.osm|traffic_sign"=\'yes\'&collections=["{seq[0].id}"]')
    # 1.jpg and e1.jpg has the tag on its semantic
    # 2.jpg has an annotation with the tag on its semantic
    assert set(get_images(r)) == {"1.jpg", "2.jpg"}

    pic1 = next(p for p in r.json["features"] if p["properties"]["original_file:name"] == "1.jpg")
    assert pic1["properties"]["collection"]["semantics"] == [
        {"key": "camera_support", "value": "bike"},
        {"key": "transport_mode", "value": "bike"},
        {"key": "weather", "value": "sunny"},
    ]
    assert pic1["properties"]["semantics"] == [
        {"key": "osm|highway", "value": "traffic_signals"},
        {"key": "osm|traffic_sign", "value": "yes"},
    ]
    assert pic1["properties"]["annotations"] == []


def test_specific_item_semantics(client, dburl):
    seq = conftest.getPictureIds(dburl)
    r = client.get(f"/api/collections/{seq[0].id}/items/{seq[0].pictures[0].id}")
    assert r.status_code == 200
    assert r.json["properties"]["collection"]["semantics"] == [
        {"key": "camera_support", "value": "bike"},
        {"key": "transport_mode", "value": "bike"},
        {"key": "weather", "value": "sunny"},
    ]
    assert r.json["properties"]["semantics"] == [
        {"key": "osm|highway", "value": "traffic_signals"},
        {"key": "osm|traffic_sign", "value": "yes"},
    ]
    assert r.json["properties"]["annotations"] == []


def test_all_items(client, dburl):
    """For the moment, in the /items endpoint, we don't show the sequence/upload_set semantics (to reduce the response size)
    It could change in the future"""
    seq = conftest.getPictureIds(dburl)
    r = client.get(f"/api/collections/{seq[0].id}/items")
    assert r.status_code == 200
    pic1 = r.json["features"][0]

    assert "collection" not in pic1["properties"]


def test_all_collections(client, dburl):
    r = client.get(f"/api/collections")
    assert r.status_code == 200
    seq1 = next(c for c in r.json["collections"] if c["title"] == "sequence_1")
    assert seq1["semantics"] == [
        {"key": "camera_support", "value": "bike"},
        {"key": "transport_mode", "value": "bike"},
        {"key": "weather", "value": "sunny"},
    ]
    seq2 = next(c for c in r.json["collections"] if c["title"] == "sequence_2")
    assert seq2["semantics"] == [{"key": "camera_support", "value": "hand"}, {"key": "transport_mode", "value": "bike"}]
