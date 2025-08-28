from flask import current_app, request, Blueprint, url_for
from flask_babel import gettext as _
from uuid import UUID
from enum import Enum
from typing import Optional
from typing_extensions import Self
from pydantic import BaseModel, ConfigDict, ValidationError, model_validator, Field
from psycopg.rows import class_row
from psycopg.sql import SQL, Identifier, Literal
from geovisio.utils import db, auth
from geovisio.utils.reports import Report, ReportType, get_report, list_reports, is_picture_owner
from geovisio.utils.params import validation_error
from geovisio.errors import InvalidAPIUsage, InternalError


bp = Blueprint("reports", __name__, url_prefix="/api")


class ReportCreationParameter(BaseModel):
    """Parameters used to create a Report"""

    issue: ReportType
    """Nature of the issue you want to report"""

    picture_id: Optional[UUID] = None
    """The ID of the picture concerned by this report. You should either set picture_id or sequence_id."""

    sequence_id: Optional[UUID] = None
    """The ID of the sequence concerned by this report. You should either set picture_id or sequence_id. If no picture_id is set, report will concern the whole sequence."""

    reporter_email: Optional[str] = None
    """The reporter email, optional but can be useful to get an answer or if precisions are necessary."""

    reporter_comments: Optional[str] = None
    """Optional details about the issue."""

    model_config = ConfigDict(use_attribute_docstrings=True)

    @model_validator(mode="after")
    def check_ids(self) -> Self:
        if self.picture_id is None and self.sequence_id is None:
            raise ValueError("At least one ID between picture_id and sequence_id must be set")
        return self


def create_report(params: ReportCreationParameter, accountId: Optional[UUID]) -> Report:
    params_as_dict = params.model_dump(exclude_none=True) | {"reporter_account_id": accountId}

    fields = [SQL(f) for f in params_as_dict.keys()]  # type: ignore (we can ignore psycopg types there as we control those keys since they are the attributes of UploadSetCreationParameter)
    values = [SQL(f"%({f})s") for f in params_as_dict.keys()]  # type: ignore

    return db.fetchone(
        current_app,
        SQL("INSERT INTO reports({fields}) VALUES({values}) RETURNING *").format(
            fields=SQL(", ").join(fields), values=SQL(", ").join(values)
        ),
        params_as_dict,
        row_factory=class_row(Report),
    )


@bp.route("/reports", methods=["POST"])
def postReport():
    """
    Create a new report

    Note that this call can be authenticated to make report associated to your account.
    ---
    tags:
        - Reports
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostReport'
    responses:
        200:
            description: the Report metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioReport'
    """

    if request.is_json and request.json is not None:
        try:
            params = ReportCreationParameter(**request.json)
        except ValidationError as ve:
            raise InvalidAPIUsage(_("Impossible to create a Report"), payload=validation_error(ve))
    else:
        raise InvalidAPIUsage(_("Parameter for creating a Report should be a valid JSON"), status_code=415)

    account = auth.get_current_account()
    account_id = UUID(account.id) if account is not None else None

    try:
        report = create_report(params, account_id)
    except Exception as e:
        raise InternalError(_("Impossible to create a Report"), status_code=500, payload={"details": str(e)})

    return (
        report.for_public().model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/json",
        },
    )


@bp.route("/reports/<uuid:report_id>", methods=["GET"])
def getReport(report_id):
    """Get an existing Report

    Note that you can only retrieve reports related to your account:
      - Reports you created
      - Reports made by others on your pictures/sequences

    Accounts with admin role can retrieve any report.
    ---
    tags:
        - Reports
    parameters:
        - name: report_id
          in: path
          description: ID of the Report to retrieve
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the Report metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioReport'
    """

    account = auth.get_current_account()

    if account is None:
        raise InvalidAPIUsage(_("Only authenticated users can access reports"), status_code=401)

    report = get_report(report_id)
    if report is None:
        raise InvalidAPIUsage(_("Report doesn't exist"), status_code=404)

    # Check if user is legimitate to access report
    if not account.can_check_reports():  # Is admin ?
        if str(report.reporter_account_id) == account.id:  # Is reporter ?
            report = report.for_public()
        elif is_picture_owner(report, account.id):  # Is owner of concerned picture/sequence ?
            report = report.for_public()
        else:  # Is going home 😂
            raise InvalidAPIUsage(_("You're not authorized to access this report"), status_code=403)

    return report.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


class ReportStatusEdit(Enum):
    waiting = "waiting"
    closed_solved = "closed_solved"
    closed_ignored = "closed_ignored"


class UserReportRole(Enum):
    reporter = "reporter"
    owner = "owner"
    admin = "admin"


class EditReportParameter(BaseModel):
    """Parameters to edit a report details"""

    issue: Optional[ReportType] = None
    """Nature of the issue"""
    status: Optional[ReportStatusEdit] = None
    """New report status"""
    reporter_email: Optional[str] = None
    """Email of the person who created the issue"""
    resolver_comments: Optional[str] = None

    # Context for validation
    editor_role: Optional[UserReportRole] = Field(None, exclude=True)

    @model_validator(mode="before")
    def check_rights(cls, values):
        status = values.get("status")
        editor_role = UserReportRole(values.get("editor_role"))
        issue = values.get("issue")
        reporter_email = values.get("reporter_email")
        resolver_comments = values.get("resolver_comments")

        if status:
            if editor_role is None:
                raise ValueError("status can't be changed by anonymous role")
            elif editor_role == UserReportRole.reporter and status == ReportStatusEdit.closed_ignored:
                raise ValueError("status can't be 'closed_ignored' for reporter")

        if issue and editor_role != UserReportRole.admin:
            raise ValueError("issue type can't be changed by non-admin role")

        if reporter_email and editor_role != UserReportRole.admin:
            raise ValueError("reporter email can't be changed by non-admin role")

        if resolver_comments and editor_role not in [UserReportRole.owner, UserReportRole.admin]:
            raise ValueError("resolver comments can't be changed by reporter")

        return values


def edit_report(report: Report, params: EditReportParameter, accountId: Optional[UUID]) -> Report:
    params_as_dict = params.model_dump(exclude=["editor_role"], exclude_none=True)
    if params.status in [ReportStatusEdit.closed_ignored, ReportStatusEdit.closed_solved]:
        params_as_dict["resolver_account_id"] = accountId

    changes = SQL(", ").join([SQL("{c} = {v}").format(c=Identifier(c), v=Literal(v)) for c, v in params_as_dict.items()])
    return db.fetchone(
        current_app,
        SQL("UPDATE reports SET {changes} WHERE id = %(id)s RETURNING *").format(changes=changes),
        {"id": report.id},
        row_factory=class_row(Report),
    )


@bp.route("/reports/<uuid:report_id>", methods=["PATCH"])
@auth.login_required_with_redirect()
def editReport(account, report_id):
    """Edit an existing Report

    Only a limited set of edits are available:
      - Reports you created: set "status" to waiting/closed_solved
      - Reports on your pictures: set "status" to waiting/closed_solved/closed_ignored, edit "resolver_comments"
      - If you're admin: you can do anything you like 😄
    ---
    tags:
        - Reports
    parameters:
        - name: report_id
          in: path
          description: ID of the Report
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchReport'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the Report metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioReport'
    """

    report = get_report(report_id)
    if report is None:
        raise InvalidAPIUsage(_("Report doesn't exist"), status_code=404)

    # Who is trying to edit ?
    who = None
    if account.can_check_reports():
        who = UserReportRole.admin
    elif str(report.reporter_account_id) == account.id:
        who = UserReportRole.reporter
    elif is_picture_owner(report, account.id):
        who = UserReportRole.owner
    else:
        raise InvalidAPIUsage(_("You're not authorized to edit this Report"), status_code=403)

    # Parse parameters
    if request.is_json and request.json is not None:
        try:
            params = EditReportParameter(**request.json, editor_role=who.value)
        except ValidationError as ve:
            raise InvalidAPIUsage(_("Impossible to edit the Report"), payload=validation_error(ve))
    else:
        raise InvalidAPIUsage(_("Parameter for editing the Report should be a valid JSON"), status_code=415)

    # Edit
    report = edit_report(report, params, account.id)
    if who != UserReportRole.admin:
        report = report.for_public()

    return (
        report.model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/json",
            "Access-Control-Expose-Headers": "Location",  # Needed for allowing web browsers access Location header
            "Location": url_for("reports.getReport", _external=True, report_id=report.id),
        },
    )


class ListReportsParameter(BaseModel):
    """Parameters used to list user's reports"""

    account_id: UUID
    limit: int = Field(default=100, ge=0, le=1000)
    filter: Optional[str] = "status IN ('open', 'open_autofix', 'waiting') AND (reporter = 'me' OR owner = 'me')"
    """Filter to apply to the list of reports. The filter should be a valid SQL WHERE clause"""


@bp.route("/reports", methods=["GET"])
@auth.login_required_with_redirect()
def listReports(account):
    """List reports

    This route is only available for admins, to see your own reports, use /api/users/me/reports route instead.
    ---
    tags:
        - Reports
    parameters:
        - $ref: '#/components/parameters/GeoVisioReports_filter'
        - name: limit
          in: query
          description: limit to the number of reports to retrieve
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 100
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the Report metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioReports'
    """
    try:
        params = request.args.copy()
        if "filter" not in params:
            params["filter"] = "status IN ('open', 'open_autofix', 'waiting')"
        params = ListReportsParameter(account_id=UUID(account.id), **params)
    except ValidationError as ve:
        raise InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    if not account.can_check_reports():
        raise InvalidAPIUsage(_("You're not authorized to list reports"), status_code=403)

    reports = list_reports(account_id=params.account_id, limit=params.limit, filter=params.filter, forceAccount=False)

    return reports.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/users/me/reports", methods=["GET"])
@auth.login_required_with_redirect()
def listUserReports(account):
    """List reports associated to current user

    This concerns reports you created, as long as reports on your pictures or sequences.
    ---
    tags:
        - Reports
    parameters:
        - $ref: '#/components/parameters/GeoVisioUserReports_filter'
        - name: limit
          in: query
          description: limit to the number of reports to retrieve
          required: true
          schema:
            type: integer
            minimum: 1
            maximum: 100
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the Report metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioReports'
    """
    try:
        params = ListReportsParameter(account_id=UUID(account.id), **request.args)
    except ValidationError as ve:
        raise InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    reports = list_reports(account_id=params.account_id, limit=params.limit, filter=params.filter)

    if not account.can_check_reports():
        reports.reports = [r.for_public() for r in reports.reports]

    return reports.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}
