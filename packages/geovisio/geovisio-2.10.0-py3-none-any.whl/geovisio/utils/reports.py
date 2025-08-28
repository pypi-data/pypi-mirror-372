from enum import Enum
from uuid import UUID
from typing import Optional, List
from typing_extensions import Self
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from geovisio.utils import cql2, db
from geovisio.errors import InvalidAPIUsage
from flask import current_app
from psycopg.sql import SQL
from psycopg.rows import class_row


class ReportType(Enum):
    blur_missing = "blur_missing"
    blur_excess = "blur_excess"
    inappropriate = "inappropriate"
    privacy = "privacy"
    picture_low_quality = "picture_low_quality"
    mislocated = "mislocated"
    copyright = "copyright"
    other = "other"


class ReportStatus(Enum):
    open = "open"
    open_autofix = "open_autofix"
    waiting = "waiting"
    closed_solved = "closed_solved"
    closed_ignored = "closed_ignored"


class Report(BaseModel):
    """A Report is a problem reported from a third-party about a picture or a sequence."""

    id: UUID
    issue: ReportType
    status: ReportStatus
    picture_id: Optional[UUID]
    sequence_id: Optional[UUID]
    ts_opened: datetime
    ts_closed: Optional[datetime]
    reporter_account_id: Optional[UUID]
    reporter_email: Optional[str]
    resolver_account_id: Optional[UUID]
    reporter_comments: Optional[str]
    resolver_comments: Optional[str]

    model_config = ConfigDict(use_enum_values=True, ser_json_timedelta="float")

    def for_public(self) -> Self:
        """Report version for public display (without report email and admin comments)"""
        return Report(
            id=self.id,
            issue=self.issue,
            status=self.status,
            picture_id=self.picture_id,
            sequence_id=self.sequence_id,
            ts_opened=self.ts_opened,
            ts_closed=self.ts_closed,
            reporter_account_id=self.reporter_account_id,
            reporter_email=None,
            resolver_account_id=self.resolver_account_id,
            reporter_comments=self.reporter_comments,
            resolver_comments=None,
        )


class Reports(BaseModel):
    reports: List[Report]


def get_report(id: UUID) -> Optional[Report]:
    """Get the Report corresponding to the ID"""
    db_report = db.fetchone(
        current_app,
        SQL("SELECT * FROM reports WHERE id = %(id)s"),
        {"id": id},
        row_factory=class_row(Report),
    )

    return db_report


def is_picture_owner(report: Report, account_id: UUID):
    """Check if given account is owner of picture concerned by report"""

    isOwner = False
    if report.picture_id is not None:
        concernedPic = db.fetchone(
            current_app,
            SQL("SELECT id FROM pictures WHERE id = %(id)s AND account_id = %(uid)s"),
            {"id": report.picture_id, "uid": account_id},
        )
        isOwner = concernedPic is not None
    elif report.sequence_id is not None:
        concernedSeq = db.fetchone(
            current_app,
            SQL("SELECT id FROM sequences WHERE id = %(id)s AND account_id = %(uid)s"),
            {"id": report.sequence_id, "uid": account_id},
        )
        isOwner = concernedSeq is not None
    return isOwner


REPORT_FILTER_TO_DB_FIELDS = {
    "status": "r.status",
    "reporter": "reporter_account_id",
    "owner": "COALESCE(p.account_id, s.account_id)",
}


def _parse_filter(filter: Optional[str]) -> SQL:
    """
    Parse a filter string and return a SQL expression

    >>> _parse_filter('')
    SQL('TRUE')
    >>> _parse_filter(None)
    SQL('TRUE')
    >>> _parse_filter("status = \'open\'")
    SQL("(r.status = \'open\')")
    >>> _parse_filter("status IN (\'open_autofix\', \'waiting\')")
    SQL("r.status IN (\'open_autofix\', \'waiting\')")
    >>> _parse_filter("reporter = \'me\'")
    SQL('(reporter_account_id = %(account_id)s)')
    >>> _parse_filter("owner = \'me\'")
    SQL('(COALESCE(p.account_id, s.account_id) = %(account_id)s)')
    >>> _parse_filter("status IN (\'open\', \'open_autofix\', \'waiting\') AND (owner = \'me\' OR reporter = \'me\')")
    SQL("(r.status IN (\'open\', \'open_autofix\', \'waiting\') AND ((COALESCE(p.account_id, s.account_id) = %(account_id)s) OR (reporter_account_id = %(account_id)s)))")
    """
    if not filter:
        return SQL("TRUE")

    return cql2.parse_cql2_filter(filter, REPORT_FILTER_TO_DB_FIELDS)


def list_reports(account_id: UUID, limit: int = 100, filter: Optional[str] = None, forceAccount: bool = True) -> Reports:
    filter_sql = _parse_filter(filter)
    if forceAccount:
        filter_sql = SQL(" ").join(
            [SQL("(COALESCE(p.account_id, s.account_id) = %(account_id)s OR reporter_account_id = %(account_id)s) AND "), filter_sql]
        )

    l = db.fetchall(
        current_app,
        SQL(
            """
        SELECT
            r.*,
            COALESCE(p.account_id, s.account_id) AS owner_account_id
        FROM reports r
        LEFT JOIN pictures p ON r.picture_id = p.id
        LEFT JOIN sequences s ON r.sequence_id = s.id
        WHERE {filter}
        ORDER BY ts_opened DESC
        LIMIT %(limit)s
        """
        ).format(filter=filter_sql),
        {"account_id": account_id, "limit": limit},
        row_factory=class_row(Report),
    )

    return Reports(reports=l)
