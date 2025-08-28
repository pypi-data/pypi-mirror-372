from uuid import UUID
import datetime
from geovisio.utils.reports import Report, ReportStatus, ReportType


def test_Report_for_public():
    r = Report(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        issue=ReportType.copyright,
        status=ReportStatus.closed_ignored,
        picture_id=UUID("00000000-0000-0000-0000-00000000aaaa"),
        sequence_id=UUID("00000000-0000-0000-0000-00000000bbbb"),
        ts_opened=datetime.datetime(2024, 1, 1),
        ts_closed=datetime.datetime(2024, 1, 2),
        reporter_account_id=UUID("00000000-0000-0000-0000-00000000cccc"),
        reporter_email="toto@toto.com",
        resolver_account_id=UUID("00000000-0000-0000-0000-00000000dddd"),
        reporter_comments="C'est pas bien !!",
        resolver_comments="Je m'en fiche",
    )
    rpub = r.for_public()
    assert rpub.id == UUID("00000000-0000-0000-0000-000000000000")
    assert rpub.issue == ReportType.copyright.value
    assert rpub.status == ReportStatus.closed_ignored.value
    assert rpub.picture_id == UUID("00000000-0000-0000-0000-00000000aaaa")
    assert rpub.sequence_id == UUID("00000000-0000-0000-0000-00000000bbbb")
    assert rpub.ts_opened == datetime.datetime(2024, 1, 1)
    assert rpub.ts_closed == datetime.datetime(2024, 1, 2)
    assert rpub.reporter_account_id == UUID("00000000-0000-0000-0000-00000000cccc")
    assert rpub.resolver_account_id == UUID("00000000-0000-0000-0000-00000000dddd")
    assert rpub.reporter_comments == "C'est pas bien !!"

    assert rpub.reporter_email is None
    assert rpub.resolver_comments is None
