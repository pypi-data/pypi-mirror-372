import psycopg
import re
from pystac import Catalog
from geovisio import stac

from . import conftest


def test_landing(client):
    response = client.get("/api/")
    data = response.json

    assert response.status_code == 200
    assert data["type"] == "Catalog"
    ctl = Catalog.from_dict(data)
    assert len(ctl.links) > 0
    assert ctl.title == "Panoramax"
    assert ctl.description == "The open source photo mapping solution"
    assert ctl.id == "geovisio"
    assert ctl.extra_fields.get("extent") == {"spatial": {"bbox": [[-180, -90, 180, 90]]}}
    assert ctl.extra_fields.get("contacts") == [{"name": "Panoramax", "emails": [{"value": "panoramax@panoramax.fr"}]}]
    assert re.match(r"^\d+\.\d+\.\d+(-\d+-[a-zA-Z0-9]+)?$", ctl.extra_fields.get("geovisio_version"))
    assert ctl.get_links("self")[0].get_absolute_href() == "http://localhost:5000/api/"
    assert ctl.get_links("xyz")[0].get_absolute_href() == "http://localhost:5000/api/map/{z}/{x}/{y}.mvt"
    assert ctl.get_links("xyz-style")[0].get_absolute_href() == "http://localhost:5000/api/map/style.json"
    assert ctl.get_links("user-xyz")[0].get_absolute_href() == "http://localhost:5000/api/users/{userId}/map/{z}/{x}/{y}.mvt"
    assert ctl.get_links("user-xyz-style")[0].get_absolute_href() == "http://localhost:5000/api/users/{userId}/map/style.json"
    assert ctl.get_links("collection-preview")[0].get_absolute_href() == "http://localhost:5000/api/collections/{id}/thumb.jpg"
    assert ctl.get_links("item-preview")[0].get_absolute_href() == "http://localhost:5000/api/pictures/{id}/thumb.jpg"
    assert ctl.get_links("data", "application/json")[0].get_absolute_href() == "http://localhost:5000/api/collections"
    assert ctl.get_links("data", "application/rss+xml")[0].get_absolute_href() == "http://localhost:5000/api/collections?format=rss"
    assert ctl.get_links("report", "application/json")[0].get_absolute_href() == "http://localhost:5000/api/reports"


@conftest.SEQ_IMGS
def test_landing_extent(datafiles, initSequenceApp, dburl):
    with initSequenceApp(datafiles, preprocess=False) as client:
        response = client.get("/api/")
        data = response.json

        assert response.status_code == 200
        assert data["type"] == "Catalog"
        ctl = Catalog.from_dict(data)
        assert len(ctl.links) > 0

        assert len(ctl.extra_fields["extent"]["temporal"]["interval"]) == 1
        assert len(ctl.extra_fields["extent"]["temporal"]["interval"][0]) == 2
        assert re.match(r"^2021-07-29T", ctl.extra_fields["extent"]["temporal"]["interval"][0][0])
        assert re.match(r"^2021-07-29T", ctl.extra_fields["extent"]["temporal"]["interval"][0][1])
        assert ctl.extra_fields["extent"]["spatial"] == {
            "bbox": [[1.9191854000091553, 49.00688934326172, 1.919199824333191, 49.00697708129883]]
        }

        # Mess up pictures coordinates
        with psycopg.connect(dburl) as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    WITH uc(rank, lon, lat) AS (
                        SELECT 1, -182, -92
                        UNION SELECT 2, -182, 92
                        UNION SELECT 3, 182, 92
                        UNION SELECT 4, 182, -92
                    ),
                    ucid AS (
                        SELECT p.id, ST_Point(uc.lon, uc.lat) AS geom
                        FROM pictures p
                        JOIN sequences_pictures sp ON p.id = sp.pic_id
                        JOIN uc ON sp.rank = uc.rank
                    )
                    UPDATE pictures
                    SET geom = ucid.geom
                    FROM ucid
                    WHERE ucid.id = pictures.id;
                """
                )
                conn.commit()

                data = client.get("/api/").json
                ctl = Catalog.from_dict(data)
                bbox = ctl.extra_fields["extent"]["spatial"]["bbox"][0]
                assert bbox[0] >= -180
                assert bbox[0] <= 180

                assert bbox[1] >= -90
                assert bbox[1] <= 90

                assert bbox[2] >= -180
                assert bbox[2] <= 180
                assert bbox[0] <= bbox[2]

                assert bbox[3] >= -90
                assert bbox[3] <= 90
                assert bbox[1] <= bbox[3]


def test_conformance(client):
    response = client.get("/api/conformance")
    data = response.json

    assert response.status_code == 200
    assert data["conformsTo"] == stac.CONFORMANCE_LIST


def test_no_license_main_endpoint(no_license_app_client):
    response = no_license_app_client.get("/api")
    assert response.status_code < 400

    # there should not be a license link since we do not know the license
    rels = [l for l in response.json["links"] if l["rel"] == "license"]
    assert not rels


def test_defined_license_main_endpoint(client):
    response = client.get("/api")
    assert response.status_code < 400

    # there should not be a license link since we do not know the license
    rels = [l for l in response.json["links"] if l["rel"] == "license"]
    assert len(rels) == 1
    l = rels[0]
    assert l == {
        "href": "https://raw.githubusercontent.com/DISIC/politique-de-contribution-open-source/master/LICENSE",
        "rel": "license",
        "title": "License for this object (etalab-2.0)",
    }


@conftest.SEQ_IMGS
def test_user_catalog(datafiles, initSequenceApp, defaultAccountID):
    with initSequenceApp(datafiles, preprocess=False) as client:
        # Get user ID
        response = client.get(f"/api/users/{str(defaultAccountID)}/catalog")
        data = response.json
        userName = "Default account"
        assert response.status_code == 200
        assert data["type"] == "Catalog"
        ctl = Catalog.from_dict(data)
        assert len(ctl.links) > 0
        assert ctl.title == userName + "'s sequences"
        assert ctl.id == f"user:{defaultAccountID}"
        assert ctl.description == "List of all sequences of user " + userName
        assert ctl.extra_fields.get("extent") is None
        assert ctl.get_links("self")[0].get_absolute_href() == f"http://localhost:5000/api/users/{str(defaultAccountID)}/catalog/"

        # Check links
        for link in ctl.get_links("child"):
            assert link.title is not None
            assert link.extra_fields["id"] is not None
            assert link.get_absolute_href() == "http://localhost:5000/api/collections/" + link.extra_fields["id"]
            assert link.extra_fields["extent"]["temporal"] == {"interval": [["2021-07-29T09:16:54+00:00", "2021-07-29T09:17:02+00:00"]]}
            assert link.extra_fields["stats:items"]["count"] == 5
