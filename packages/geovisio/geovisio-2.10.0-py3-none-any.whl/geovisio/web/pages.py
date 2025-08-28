from flask import current_app, request, url_for, Blueprint
from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List
from geovisio.utils import db, auth
from geovisio.utils.link import Link, make_link
from geovisio.errors import InvalidAPIUsage
from flask_babel import gettext as _
from psycopg.sql import SQL

bp = Blueprint("pages", __name__, url_prefix="/api")


class PageName(Enum):
    end_user_license_agreement = "end-user-license-agreement"
    terms_of_service = "terms-of-service"
    end_user_license_agreement_summary = "end-user-license-agreement-summary"


class PageLanguage(BaseModel):
    """A specific language for the page"""

    language: str
    """The language (as ISO 639-2 code)"""

    links: List[Link]
    """Link to page content"""


class PageSummary(BaseModel):
    """Page summary"""

    name: PageName
    """Page name"""
    languages: List[PageLanguage]
    """Available translations"""

    model_config = ConfigDict(use_attribute_docstrings=True)


def check_page_name(v: str) -> PageName:
    try:
        return PageName(v)
    except ValueError:
        raise InvalidAPIUsage(_("Page name is not recognized"), status_code=400)


@bp.route("/pages/<page>", methods=["GET"])
def getPageLanguages(page):
    """List available languages for a single page
    ---
    tags:
        - Configuration
    parameters:
        - name: page
          in: path
          description: Page name
          required: true
          schema:
            $ref: '#/components/schemas/GeoVisioPageName'
    responses:
        200:
            description: the languages list
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioPageSummary'
    """

    name = check_page_name(page)
    langs = [d[0] for d in db.fetchall(current_app, SQL("SELECT lang FROM pages WHERE name = %(name)s"), {"name": name.value})]

    # If page doesn't exist yet, send empty list of languages
    if langs is None or len(langs) == 0:
        langs = []

    summary = PageSummary(
        name=name,
        languages=[PageLanguage(language=l, links=[make_link(rel="self", route="pages.getPage", page=name.value, lang=l)]) for l in langs],
    )

    return (
        summary.model_dump_json(exclude_none=True),
        200,
        {
            "Content-Type": "application/json",
        },
    )


@bp.route("/pages/<page>/<lang>", methods=["GET"])
def getPage(page, lang):
    """Get page HTML content for a certain language
    ---
    tags:
        - Configuration
    parameters:
        - name: page
          in: path
          description: Page name
          required: true
          schema:
            $ref: '#/components/schemas/GeoVisioPageName'
        - name: lang
          in: path
          description: Language ISO 639-2 code
          required: true
          schema:
            type: string
    responses:
        200:
            description: the HTML content for this page
            content:
                text/html:
                    schema:
                        type: string
    """

    page = check_page_name(page)
    page_content = db.fetchone(
        current_app,
        SQL("SELECT content FROM pages WHERE name = %(name)s AND lang = %(lang)s"),
        {"name": page.value, "lang": lang},
    )

    if page_content is None:
        raise InvalidAPIUsage(_("Page not available in language %(l)s", l=lang), status_code=404)

    return (
        page_content[0],
        200,
        {
            "Content-Type": "text/html",
        },
    )


@bp.route("/pages/<page>/<lang>", methods=["POST", "PUT"])
@auth.login_required()
def postPage(page, lang, account):
    """Save HTML content for a certain language of a page.

    This call is only available for account with admin role.
    ---
    tags:
        - Configuration
    parameters:
        - name: page
          in: path
          description: Page name
          required: true
          schema:
            $ref: '#/components/schemas/GeoVisioPageName'
        - name: lang
          in: path
          description: Language ISO 639-2 code
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    requestBody:
        content:
            text/html:
                schema:
                    type: string
    responses:
        200:
            description: Successfully saved
    """

    name = check_page_name(page)

    if not account.can_edit_pages():
        raise InvalidAPIUsage(_("You must be logged-in as admin to edit pages"), 403)
    if request.content_type != "text/html":
        raise InvalidAPIUsage(_("Page content must be HTML (with " "Content-Type: text/html" " header set)"), 400)

    with db.execute(
        current_app,
        SQL(
            """
INSERT INTO pages (name, lang, content)
VALUES (%(name)s, %(lang)s, %(content)s)
ON CONFLICT (name, lang) DO UPDATE SET content=EXCLUDED.content
        """
        ),
        {"name": name.value, "lang": lang, "content": request.get_data(as_text=True)},
    ) as res:
        if not res.rowcount:
            raise InvalidAPIUsage(_("Could not update page content"), 500)

    return "", 200


@bp.route("/pages/<page>/<lang>", methods=["DELETE"])
@auth.login_required()
def deletePage(page, lang, account):
    """Delete HTML content for a certain language of a page.

    This call is only available for account with admin role.
    ---
    tags:
        - Configuration
    parameters:
        - name: page
          in: path
          description: Page name
          required: true
          schema:
            $ref: '#/components/schemas/GeoVisioPageName'
        - name: lang
          in: path
          description: Language ISO 639-2 code
          required: true
          schema:
            type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: Successfully deleted
    """

    name = check_page_name(page)

    if not account.can_edit_pages():
        raise InvalidAPIUsage(_("You must be logged-in as admin to edit pages"), 403)

    with db.execute(
        current_app, SQL("DELETE FROM pages WHERE name = %(name)s AND lang = %(lang)s"), {"name": name.value, "lang": lang}
    ) as res:
        if res.rowcount == 0:
            raise InvalidAPIUsage(_("Page not available in language %(l)s", l=lang), status_code=404)
        elif not res.rowcount:
            raise InvalidAPIUsage(_("Could not delete page content"), 500)

    return "", 200
