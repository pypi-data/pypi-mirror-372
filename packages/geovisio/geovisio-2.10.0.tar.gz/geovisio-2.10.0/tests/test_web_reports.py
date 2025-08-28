from tests import conftest
import pytest
from pathlib import Path
from uuid import UUID


@conftest.SEQ_IMGS
def test_post_report_valid(datafiles, initSequenceApp, dburl, bobAccountID, bobAccountToken):
    with initSequenceApp(datafiles, preprocess=False) as client:
        seqId, picId = conftest.getFirstPictureIds(dburl)

        # Report on single picture
        postJson = {
            "issue": "privacy",
            "picture_id": picId,
            "sequence_id": seqId,
            "reporter_email": "toto@toto.com",
            "reporter_comments": "C'est très embêtant !!1",
        }
        response = client.post("/api/reports", json=postJson)
        assert response.status_code == 200, response.text
        r = response.json
        assert r.get("issue") == "privacy"
        assert r.get("picture_id") == str(picId)
        assert r.get("sequence_id") == str(seqId)
        assert r.get("id") is not None
        assert r.get("status") == "open_autofix"
        assert r.get("reporter_email") is None  # Should not be shown
        assert r.get("reporter_comments") == "C'est très embêtant !!1"

        # Report on whole sequence
        postJson = {
            "issue": "mislocated",
            "sequence_id": seqId,
        }
        response = client.post("/api/reports", json=postJson, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200, response.text
        r = response.json
        assert r.get("issue") == "mislocated"
        assert r.get("picture_id") is None
        assert r.get("sequence_id") == str(seqId)
        assert r.get("id") is not None
        assert r.get("status") == "open"
        assert r.get("reporter_email") is None
        assert r.get("reporter_account_id") == str(bobAccountID)
        assert r.get("reporter_comments") is None


@pytest.mark.parametrize(
    ("issue", "picid", "seqid", "httpcode", "error_msg", "error_details"),
    (
        (
            None,
            None,
            None,
            400,
            "Impossible to create a Report",
            "Input should be 'blur_missing'",
        ),
        ("blur_missing", None, None, 400, "Impossible to create a Report", "Value error, At least one ID between picture_id and"),
        (  # Picture UUID doesn't exist
            "blur_missing",
            "00000000-0000-0000-0000-000000000000",
            None,
            500,
            "Impossible to create a Report",
            None,
        ),
        (  # Sequence UUID doesn't exist
            "blur_missing",
            None,
            "00000000-0000-0000-0000-000000000000",
            500,
            "Impossible to create a Report",
            None,
        ),
    ),
)
def test_post_report_errors_anon(
    client,
    issue,
    picid,
    seqid,
    httpcode,
    error_msg,
    error_details,
):
    postJson = {
        "issue": issue,
        "picture_id": picid,
        "sequence_id": seqid,
    }
    response = client.post("/api/reports", json=postJson)

    assert response.status_code == httpcode, response.text

    if httpcode >= 400:
        assert response.json["message"] == error_msg
        assert response.json["status_code"] == httpcode
        if error_details:
            assert response.json["details"][0]["error"].startswith(error_details)


@conftest.SEQ_IMGS
def test_get_report(app, dburl, defaultAccountToken, bobAccountToken, camilleAccountToken, camilleAccountID):
    with app.app_context():
        # Picture & sequence made by Bob
        pics = [Path(conftest.FIXTURE_DIR) / "1.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        ##########################################################
        # Anonymous report: admin + pic owner can access
        #

        response = client.post(
            "/api/reports",
            json={
                "issue": "privacy",
                "picture_id": picId,
                "sequence_id": seqId,
                "reporter_email": "toto@toto.com",
            },
        )
        assert response.status_code == 200, response.text
        rid = response.json.get("id")
        assert rid is not None

        # Anon request -> 401
        response = client.get(f"/api/reports/{rid}")
        assert response.status_code == 401
        assert response.json["message"] == "Only authenticated users can access reports"

        # Admin request -> 200
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert response.status_code == 200
        assert response.json["id"] == rid
        assert response.json.get("reporter_email") == "toto@toto.com"

        # Picture owner request -> 200
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200
        assert response.json.get("reporter_email") is None

        # Other user request -> 403
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert response.status_code == 403
        assert response.json["message"] == "You're not authorized to access this report"

        ##########################################################
        # Authenticated report: reporter, pic owner & admin can access
        #

        response = client.post(
            "/api/reports",
            json={
                "issue": "privacy",
                "picture_id": picId,
                "sequence_id": seqId,
            },
            headers={"Authorization": f"Bearer {camilleAccountToken()}"},
        )
        assert response.status_code == 200, response.text
        rid = response.json.get("id")
        assert rid is not None

        # Anon request -> 401
        response = client.get(f"/api/reports/{rid}")
        assert response.status_code == 401
        assert response.json["message"] == "Only authenticated users can access reports"

        # Admin request -> 200
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert response.status_code == 200
        assert response.json["id"] == rid
        assert response.json["reporter_account_id"] == str(camilleAccountID)

        # Pic owner request -> 200
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 200
        assert response.json["id"] == rid
        assert response.json["reporter_account_id"] == str(camilleAccountID)

        # Reporter request -> 200
        response = client.get(f"/api/reports/{rid}", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert response.status_code == 200
        assert response.json["id"] == rid
        assert response.json["reporter_account_id"] == str(camilleAccountID)


@pytest.mark.parametrize(
    ("limit", "error"),
    (
        (
            "10000",
            {
                "details": [{"error": "Input should be less than or equal to 1000", "fields": ["limit"], "input": "10000"}],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        (
            "-1",
            {
                "details": [{"error": "Input should be greater than or equal to 0", "fields": ["limit"], "input": "-1"}],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
        (
            "pouet",
            {
                "details": [
                    {
                        "error": "Input should be a valid integer, unable to parse string as an integer",
                        "fields": ["limit"],
                        "input": "pouet",
                    }
                ],
                "message": "Impossible to parse parameters",
                "status_code": 400,
            },
        ),
    ),
)
def test_user_reports_limit(client, bobAccountToken, limit, error):
    """limit cannot exceed 1000"""
    response = client.get(
        f"/api/users/me/reports?limit={limit}",
        headers={"Authorization": f"Bearer {bobAccountToken()}"},
    )
    assert response.status_code == 400, response.text
    assert response.json == error


def _create_report(client, token=None, **kwargs):
    h = {"Authorization": f"Bearer {token}"} if token else {}

    response = client.post(
        "/api/reports",
        json=kwargs,
        headers=h,
    )
    assert response.status_code == 200, response.text
    report_id = response.json["id"]
    assert report_id
    UUID(report_id)  # should be a valid uuid
    return report_id


def test_patch_report_anon(app, dburl, defaultAccountToken, bobAccountToken, bobAccountID, camilleAccountToken):
    with app.app_context():
        # Picture & sequence made by Bob
        pics = [Path(conftest.FIXTURE_DIR) / "1.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        r1 = _create_report(client, token=None, issue="blur_missing", picture_id=picId, reporter_email="toto@toto.com")

        # Try to edit as anon
        response = client.patch(f"/api/reports/{r1}", json={})
        assert response.status_code == 403

        # Try to edit as third-party
        response = client.patch(f"/api/reports/{r1}", json={}, headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert response.status_code == 403
        assert response.json["message"] == "You're not authorized to edit this Report"

        # Try to edit as pic owner
        response = client.patch(
            f"/api/reports/{r1}",
            json={"resolver_comments": "C'est bon c'est corrigé", "status": "closed_solved"},
            headers={"Authorization": f"Bearer {bobAccountToken()}"},
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("Location").endswith(f"/api/reports/{r1}")
        assert response.json["id"] == r1
        assert response.json["issue"] == "blur_missing"
        assert response.json["status"] == "closed_solved"
        assert response.json["picture_id"] == str(picId)
        assert response.json["ts_opened"] is not None
        assert response.json["ts_closed"] is not None
        assert response.json["resolver_account_id"] == str(bobAccountID)

        # Try to edit as admin
        response = client.patch(
            f"/api/reports/{r1}",
            json={"resolver_comments": "En fait non...", "issue": "inappropriate", "status": "waiting"},
            headers={"Authorization": f"Bearer {defaultAccountToken()}"},
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("Location").endswith(f"/api/reports/{r1}")
        assert response.json["id"] == r1
        assert response.json["issue"] == "inappropriate"
        assert response.json["status"] == "waiting"
        assert response.json["picture_id"] == str(picId)
        assert response.json["ts_opened"] is not None
        assert response.json.get("ts_closed") is None
        assert response.json.get("resolver_account_id") is None

        # Edit as pic owner + change to invalid status
        response = client.patch(f"/api/reports/{r1}", json={"status": "open"}, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 400
        assert response.json["message"] == "Impossible to edit the Report"
        assert response.json["details"][0] == {
            "error": "Input should be 'waiting', 'closed_solved' or 'closed_ignored'",
            "fields": ["status"],
            "input": "open",
        }

        # Edit as pic owner + change issue (not authorized)
        response = client.patch(f"/api/reports/{r1}", json={"issue": "copyright"}, headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert response.status_code == 400
        assert response.json["message"] == "Impossible to edit the Report"
        assert response.json["details"][0] == {
            "error": "Value error, issue type can't be changed by non-admin role",
            "fields": [],
            "input": {"editor_role": "owner", "issue": "copyright"},
        }

        # Edit as pic owner + change reporter_email (not authorized)
        response = client.patch(
            f"/api/reports/{r1}", json={"reporter_email": "tata@tata.com"}, headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert response.status_code == 400
        assert response.json["message"] == "Impossible to edit the Report"
        assert response.json["details"][0] == {
            "error": "Value error, reporter email can't be changed by non-admin role",
            "fields": [],
            "input": {"editor_role": "owner", "reporter_email": "tata@tata.com"},
        }


def test_patch_report_authenticated(app, dburl, defaultAccountToken, bobAccountToken, bobAccountID, camilleAccountToken, camilleAccountID):
    with app.app_context():
        # Picture & sequence made by Bob
        pics = [Path(conftest.FIXTURE_DIR) / "1.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        r1 = _create_report(client, token=camilleAccountToken(), issue="blur_missing", picture_id=picId)

        # Try to edit as anon
        response = client.patch(f"/api/reports/{r1}", json={})
        assert response.status_code == 403

        # Try to edit as reporter + unauthorized change
        response = client.patch(
            f"/api/reports/{r1}", json={"issue": "copyright"}, headers={"Authorization": f"Bearer {camilleAccountToken()}"}
        )
        assert response.status_code == 400
        assert response.json["message"] == "Impossible to edit the Report"
        assert response.json["details"][0] == {
            "error": "Value error, issue type can't be changed by non-admin role",
            "fields": [],
            "input": {"editor_role": "reporter", "issue": "copyright"},
        }

        # Edit as reporter
        response = client.patch(
            f"/api/reports/{r1}", json={"status": "closed_solved"}, headers={"Authorization": f"Bearer {camilleAccountToken()}"}
        )
        assert response.status_code == 200, response.text
        assert response.headers.get("Location").endswith(f"/api/reports/{r1}")
        assert response.json["id"] == r1
        assert response.json["issue"] == "blur_missing"
        assert response.json["status"] == "closed_solved"
        assert response.json["picture_id"] == str(picId)
        assert response.json["ts_opened"] is not None
        assert response.json["ts_closed"] is not None
        assert response.json["resolver_account_id"] == str(camilleAccountID)


def test_list_reports(app, dburl, defaultAccountToken, bobAccountToken, bobAccountID):
    with app.app_context():
        # Picture & sequence made by Bob
        pics = [Path(conftest.FIXTURE_DIR) / "1.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        # Report from admin
        r1 = _create_report(client, defaultAccountToken(), issue="copyright", picture_id=picId, sequence_id=seqId)

        # Report from bob
        r2 = _create_report(client, bobAccountToken(), issue="blur_excess", sequence_id=seqId)

        # Report from anon
        r3 = _create_report(client, token=None, issue="blur_missing", picture_id=picId, reporter_email="toto@toto.com")

        # Anon not authorized
        anonReports = client.get("/api/reports")
        assert anonReports.status_code == 403
        anonReports.json["message"] == "You must be admin and authenticated to list reports"

        # Bob not authorized
        bobReports = client.get("/api/reports", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert bobReports.status_code == 403
        bobReports.json["message"] == "You're not authorized to list reports"

        # Get reports seen by Admin
        adminReports = client.get("/api/reports", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 3
        assert [r.get("id") for r in adminReports.json["reports"]] == [r3, r2, r1]

        # Reports seen by Admin with limit
        adminReports = client.get("/api/reports?limit=1", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 1
        assert [r.get("id") for r in adminReports.json["reports"]] == [r3]

        # Reports created by Admin
        adminReports = client.get("/api/reports?filter=reporter='me'", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 1
        assert [r.get("id") for r in adminReports.json["reports"]] == [r1]

        # Reports seen by Admin with autofix
        adminReports = client.get("/api/reports?filter=status='open_autofix'", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 2
        assert [r.get("id") for r in adminReports.json["reports"]] == [r3, r1]

        # Report by Bob seen by Admin
        adminReports = client.get(
            f"/api/reports?filter=reporter='{str(bobAccountID)}'", headers={"Authorization": f"Bearer {defaultAccountToken()}"}
        )
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 1
        assert [r.get("id") for r in adminReports.json["reports"]] == [r2]


def test_user_reports(app, dburl, defaultAccountToken, bobAccountToken, camilleAccountToken):
    with app.app_context():
        # Picture & sequence made by Bob
        pics = [Path(conftest.FIXTURE_DIR) / "1.jpg"]
        client = conftest.app_with_data(app=app, sequences={"seq1": pics}, jwtToken=bobAccountToken())
        seqId, picId = conftest.getFirstPictureIds(dburl)

        # Report from admin
        r1 = _create_report(client, defaultAccountToken(), issue="copyright", picture_id=picId, sequence_id=seqId)

        # Report from bob
        r2 = _create_report(client, bobAccountToken(), issue="blur_excess", sequence_id=seqId)

        # Report from anon
        r3 = _create_report(client, token=None, issue="blur_missing", picture_id=picId, reporter_email="toto@toto.com")

        # Get reports seen by Bob
        bobReports = client.get("/api/users/me/reports/", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert bobReports.status_code == 200, bobReports.text
        assert len(bobReports.json["reports"]) == 3
        assert [r.get("id") for r in bobReports.json["reports"]] == [r3, r2, r1]
        assert bobReports.json["reports"][0].get("reporter_email") is None

        # Get reports seen by Admin
        adminReports = client.get("/api/users/me/reports/", headers={"Authorization": f"Bearer {defaultAccountToken()}"})
        assert adminReports.status_code == 200, adminReports.text
        assert len(adminReports.json["reports"]) == 1
        assert [r.get("id") for r in adminReports.json["reports"]] == [r1]

        # Get reports seen by Camille
        camilleReports = client.get("/api/users/me/reports/", headers={"Authorization": f"Bearer {camilleAccountToken()}"})
        assert camilleReports.status_code == 200, camilleReports.text
        assert len(camilleReports.json["reports"]) == 0

        # Reports seen by Bob with limit
        bobReports = client.get("/api/users/me/reports?limit=1", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert bobReports.status_code == 200, bobReports.text
        assert len(bobReports.json["reports"]) == 1
        assert [r.get("id") for r in bobReports.json["reports"]] == [r3]

        # Reports created by Bob
        bobReports = client.get("/api/users/me/reports?filter=reporter='me'", headers={"Authorization": f"Bearer {bobAccountToken()}"})
        assert bobReports.status_code == 200, bobReports.text
        assert len(bobReports.json["reports"]) == 1
        assert [r.get("id") for r in bobReports.json["reports"]] == [r2]

        # Reports seen by Bob with autofix
        bobReports = client.get(
            "/api/users/me/reports?filter=status='open_autofix'", headers={"Authorization": f"Bearer {bobAccountToken()}"}
        )
        assert bobReports.status_code == 200, bobReports.text
        assert len(bobReports.json["reports"]) == 2
        assert [r.get("id") for r in bobReports.json["reports"]] == [r3, r1]
