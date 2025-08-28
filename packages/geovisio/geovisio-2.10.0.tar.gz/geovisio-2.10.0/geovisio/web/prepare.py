from flask import current_app, request, url_for, Blueprint
from geovisio import errors
from geovisio.utils import auth
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from psycopg.sql import SQL
from flask_babel import gettext as _
from pydantic import BaseModel, ConfigDict, ValidationError

from geovisio.utils.params import validation_error

bp = Blueprint("prepare", __name__, url_prefix="/api")


class PreparationParameter(BaseModel):
    """Parameters used control the behaviour of the preparation process"""

    skip_blurring: bool = False
    """If true, the picture will not be blurred again"""

    def as_sql(self):
        return Jsonb({"skip_blurring": self.skip_blurring}) if self.skip_blurring else None

    model_config = ConfigDict(use_attribute_docstrings=True)


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>/prepare", methods=["POST"])
def prepareItem(collectionId, itemId, account=None):
    """Ask for preparation of a picture. The picture will be blurred if needed, and derivates will be generated.
    ---
    tags:
        - Pictures
    parameters:
        - name: collectionId
          in: path
          description: ID of collection
          required: true
          schema:
            type: string
        - name: itemId
          in: path
          description: ID of item
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/PreparationParameter'
    responses:
        202:
            description: Empty response for the moment, but later we might return a way to track the progress of the preparation
            content:
                application/json:
                    schema:
                        type: object
    """
    try:
        params = PreparationParameter(**(request.json if request.is_json else {}))
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    with current_app.pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            account = auth.get_current_account()
            accountId = account.id if account else None

            record = cursor.execute(
                SQL(
                    """SELECT 1 
FROM pictures p
JOIN sequences_pictures sp ON p.id = sp.pic_id
WHERE
    p.id = %(pic)s
    AND sp.seq_id = %(seq)s
    AND (p.account_id = %(acc)s OR p.status != 'hidden')"""
                ),
                {"pic": itemId, "seq": collectionId, "acc": accountId},
            ).fetchone()

            if not record:
                raise errors.InvalidAPIUsage(
                    _("Picture %(p)s wasn't found in database", p=itemId),
                    status_code=404,
                )

            cursor.execute(
                SQL("INSERT INTO job_queue(picture_id, task, args) VALUES (%(pic)s, 'prepare', %(args)s)"),
                {"pic": itemId, "args": params.as_sql()},
            )

    # run background task to prepare the picture
    current_app.background_processor.process_pictures()  # type: ignore

    return {}, 202, {"Content-Type": "application/json"}


@bp.route("/collections/<uuid:collectionId>/prepare", methods=["POST"])
def prepareCollection(collectionId, account=None):
    """Ask for preparation of all the pictures of a collection. The pictures will be blurred if needed, and derivates will be generated.
    ---
    tags:
        - Sequences
    parameters:
        - name: collectionId
          in: path
          description: ID of collection
          required: true
          schema:
            type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/PreparationParameter'
    responses:
        202:
            description: Empty response for the moment, but later we might return a way to track the progress of the preparation
            content:
                application/json:
                    schema:
                        type: object
    """
    try:
        params = PreparationParameter(**(request.json if request.is_json else {}))
    except ValidationError as ve:
        raise errors.InvalidAPIUsage(_("Impossible to parse parameters"), payload=validation_error(ve))

    with current_app.pool.connection() as conn:
        with conn.cursor(row_factory=dict_row) as cursor:
            account = auth.get_current_account()
            accountId = account.id if account else None

            record = cursor.execute(
                SQL(
                    """SELECT 1 
FROM sequences
WHERE
    id = %(seq)s
    AND (account_id = %(acc)s OR status != 'hidden')"""
                ),
                {"seq": collectionId, "acc": accountId},
            ).fetchone()

            if not record:
                raise errors.InvalidAPIUsage(
                    _("Collection %(c)s wasn't found in database", c=collectionId),
                    status_code=404,
                )

            cursor.execute(
                SQL(
                    """INSERT INTO job_queue(picture_id, task, args) 
SELECT pic_id, 'prepare', %(args)s
FROM sequences_pictures
WHERE seq_id = %(seq)s"""
                ),
                {"seq": collectionId, "args": params.as_sql()},
            )

    # run background task to prepare the picture
    current_app.background_processor.process_pictures()  # type: ignore

    return {}, 202, {"Content-Type": "application/json"}
