from typing import List, Optional
from geovisio.utils import auth, db
from geovisio.utils.annotations import (
    AnnotationCreationParameter,
    creation_annotation,
    get_annotation,
    update_annotation,
    InputAnnotationShape,
)
from geovisio.utils.tags import SemanticTagUpdate
from geovisio.web.utils import accountIdOrDefault
from geovisio.utils.params import validation_error
from geovisio import errors
from pydantic import BaseModel, ValidationError, Field
from uuid import UUID
from flask import Blueprint, current_app, request, url_for
from flask_babel import gettext as _


bp = Blueprint("annotations", __name__, url_prefix="/api")


class AnnotationPostParameter(BaseModel):
    shape: InputAnnotationShape
    """Shape defining the annotation.
The annotation shape is either a full geojson geometry or only a bounding box (4 floats).

The coordinates should be given in pixel, starting from the bottom left of the picture.

Note that the API will always output geometry as geojson geometry (thus will transform the bbox into a polygon).
"""

    semantics: List[SemanticTagUpdate] = Field(default_factory=list)
    """Semantic tags associated to the annotation"""


@bp.route("/pictures/<uuid:itemId>/annotations", methods=["POST"])
@auth.login_required()
def postAnnotationNonStacAlias(itemId, account):
    """Create an annotation on a picture.

    The geometry can be provided as a bounding box (a list of 4 integers, minx, miny, maxx, maxy) or as a geojson geometry.
    All coordinates must be in pixel, starting from the top left of the picture.

    If an annotation already exists on the picture with the same shape, it will be used.

    The is an alias to the `/api/collections/<collectionId>/items/<itemId>/annotations` endpoint (but you don't need to know the collection ID here).
    ---
    tags:
        - Editing
        - Semantics
    parameters:
        - name: itemId
          in: path
          description: ID of item to retrieve
          required: true
          schema:
              type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostAnnotation'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
    """

    account_id = UUID(accountIdOrDefault(account))

    pic = db.fetchone(
        current_app,
        "SELECT 1 FROM pictures WHERE id = %(pic)s",
        {"pic": itemId},
    )
    if not pic:
        raise errors.InvalidAPIUsage(_("Picture %(p)s wasn't found in database", p=itemId), status_code=404)

    if request.is_json and request.json is not None:
        try:
            post_params = AnnotationPostParameter(**request.json, account_id=account_id, picture_id=itemId)
        except ValidationError as ve:
            raise errors.InvalidAPIUsage(_("Impossible to create an annotation"), payload=validation_error(ve))
    else:
        raise errors.InvalidAPIUsage(_("Parameter for creating an annotation should be a valid JSON"), status_code=415)

    creation_params = AnnotationCreationParameter(
        account_id=account_id, picture_id=itemId, shape=post_params.shape, semantics=post_params.semantics
    )

    with db.conn(current_app) as conn:
        annotation = creation_annotation(creation_params, conn)

        return (
            annotation.model_dump_json(exclude_none=True),
            200,
            {
                "Content-Type": "application/json",
                "Access-Control-Expose-Headers": "Location",  # Needed for allowing web browsers access Location header
                "Location": url_for("annotations.getAnnotationById", _external=True, annotationId=annotation.id),
            },
        )


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations", methods=["POST"])
@auth.login_required()
def postAnnotation(collectionId, itemId, account):
    """Create an annotation on a picture.

    The geometry can be provided as a bounding box (a list of 4 integers, minx, miny, maxx, maxy) or as a geojson geometry.
    All coordinates must be in pixel, starting from the top left of the picture.

    If an annotation already exists on the picture with the same shape, it will be used.
    ---
    tags:
        - Editing
        - Semantics
    parameters:
        - name: collectionId
          in: path
          description: ID of collection to retrieve
          required: true
          schema:
              type: string
        - name: itemId
          in: path
          description: ID of item to retrieve
          required: true
          schema:
              type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPostAnnotation'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
    """
    return postAnnotationNonStacAlias(itemId=itemId, account=account)


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations/<uuid:annotationId>", methods=["GET"])
def getAnnotation(collectionId, itemId, annotationId):
    """Get an annotation

    Note that this is the same route as `/api/annotations/<uuid:annotationId>` but you need to know the picture's and collection's IDs.
    ---
    tags:
        - Semantics
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
        - name: annotationId
          in: path
          description: ID of annotation
          required: true
          schema:
              type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
    """
    with db.conn(current_app) as conn:

        annotation = get_annotation(conn, annotationId)
        if not annotation or annotation.picture_id != itemId:
            raise errors.InvalidAPIUsage(_("Annotation %(p)s not found", p=itemId), status_code=404)

        return annotation.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/annotations/<uuid:annotationId>", methods=["GET"])
def getAnnotationById(annotationId):
    """Get an annotation.

    This is the same route as `/api/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations/<uuid:annotationId>` but you don't need to know the picture's and collection's IDs.

    ---
    tags:
        - Semantics
    parameters:
        - name: annotationId
          in: path
          description: ID of annotation
          required: true
          schema:
              type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
    """
    with db.conn(current_app) as conn:
        annotation = get_annotation(conn, annotationId)
        if not annotation:
            raise errors.InvalidAPIUsage(_("Annotation %(p)s not found", p=annotationId), status_code=404)

        return annotation.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


class AnnotationPatchParameter(BaseModel):
    """Parameters used to update an annotation"""

    semantics: Optional[List[SemanticTagUpdate]] = None
    """Tags to update on the annotation. By default each tag will be added to the annotation's tags, but you can change this behavior by setting the `action` parameter to `delete`.

    If you want to replace a tag, you need to first delete it, then add it again.

    Like:
[
    {"key": "some_key", "value": "some_value", "action": "delete"},
    {"key": "some_key", "value": "some_new_value"}
]
    """


@bp.route("/annotations/<uuid:annotationId>", methods=["PATCH"])
@auth.login_required()
def patchAnnotationNonStacAlias(annotationId, account):
    """Patch an annotation

    Note that if the annotation has no associated tags anymore, it will be deleted.

    Note that is an alias to the `/api/collections/<collectionId>/items/<itemId>/annotations/<annotationId>` endpoint (but you don't need to know the collection/item ID here).
    ---
    tags:
        - Semantics
    parameters:
        - name: annotationId
          in: path
          description: ID of annotation
          required: true
          schema:
              type: string
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/components/schemas/GeoVisioPatchAnnotation'
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
        204:
            description: The annotation was empty, it has been correctly deleted
    """
    if request.is_json and request.json is not None:
        try:
            params = AnnotationPatchParameter(**request.json)
        except ValidationError as ve:
            raise errors.InvalidAPIUsage(_("Impossible to patch annotation, invalid parameters"), payload=validation_error(ve))
    else:
        raise errors.InvalidAPIUsage(_("Parameter for updating an annotation should be a valid JSON"), status_code=415)

    with db.conn(current_app) as conn:

        annotation = get_annotation(conn, annotationId)
        if not annotation:
            raise errors.InvalidAPIUsage(_("Annotation %(p)s not found", p=annotationId), status_code=404)

        a = update_annotation(annotation, params.semantics, account.id)
        if a is None:
            return "", 204
        return a.model_dump_json(exclude_none=True), 200, {"Content-Type": "application/json"}


@bp.route("/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations/<uuid:annotationId>", methods=["PATCH"])
@auth.login_required()
def patchAnnotation(collectionId, itemId, annotationId, account):
    """Patch an annotation

    Note that if the annotation has no associated tags anymore, it will be deleted.

    Note that is the an alias to the `/api/annotations/<annotationId>` endpoint (but you need to know the collection/item ID here).
    ---
    tags:
        - Semantics
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
        - name: annotationId
          in: path
          description: ID of annotation
          required: true
          schema:
              type: string
    security:
        - bearerToken: []
        - cookieAuth: []
    responses:
        200:
            description: the annotation metadata
            content:
                application/json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioAnnotation'
        204:
            description: The annotation was empty, it has been correctly deleted
    """
    return patchAnnotationNonStacAlias(annotationId=annotationId, account=account)
