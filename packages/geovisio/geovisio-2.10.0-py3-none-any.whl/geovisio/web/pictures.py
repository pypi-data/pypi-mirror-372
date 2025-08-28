from flask import Blueprint, current_app
from geovisio import utils, errors
from flask import redirect
from flask_babel import gettext as _
import logging

bp = Blueprint("pictures", __name__, url_prefix="/api/pictures")

log = logging.getLogger(__name__)


@bp.route("/<uuid:pictureId>/hd.<format>")
def getPictureHD(pictureId, format):
    """Get picture image (high-definition)
    ---
    tags:
        - Pictures
    parameters:
        - name: pictureId
          in: path
          description: ID of picture to retrieve
          required: true
          schema:
            type: string
        - name: format
          in: path
          description: Wanted format for output image (for the moment only jpg)
          required: true
          schema:
            type: string
    responses:
        200:
            description: High-definition
            content:
                image/jpeg:
                    schema:
                        type: string
                        format: binary
    """

    utils.pictures.checkFormatParam(format)

    fses = current_app.config["FILESYSTEMS"]
    metadata = utils.pictures.checkPictureStatus(fses, pictureId)

    external_url = utils.pictures.getPublicHDPictureExternalUrl(pictureId, format)
    if external_url and metadata["status"] == "ready":
        return redirect(external_url)

    try:
        picture = fses.permanent.openbin(utils.pictures.getHDPicturePath(pictureId))
    except:
        raise errors.InvalidAPIUsage(_("Unable to read picture on filesystem"), status_code=500)

    return utils.pictures.sendInFormat(picture, "jpeg", format)


@bp.route("/<uuid:pictureId>/sd.<format>")
def getPictureSD(pictureId, format):
    """Get picture image (standard definition)
    ---
    tags:
        - Pictures
    parameters:
        - name: pictureId
          in: path
          description: ID of picture to retrieve
          required: true
          schema:
            type: string
        - name: format
          in: path
          description: Wanted format for output image (for the moment only jpg)
          required: true
          schema:
            type: string
    responses:
        200:
            description: Standard definition (width of 2048px)
            content:
                image/jpeg:
                    schema:
                        type: string
                        format: binary
    """
    utils.pictures.checkFormatParam(format)

    fses = current_app.config["FILESYSTEMS"]
    metadata = utils.pictures.checkPictureStatus(fses, pictureId)

    external_url = utils.pictures.getPublicDerivatePictureExternalUrl(pictureId, format, "sd.jpg")
    if external_url and metadata["status"] == "ready":
        return redirect(external_url)

    try:
        picture = fses.derivates.openbin(utils.pictures.getPictureFolderPath(pictureId) + "/sd.jpg")
    except:
        raise errors.InvalidAPIUsage(_("Unable to read picture on filesystem"), status_code=500)

    return utils.pictures.sendInFormat(picture, "jpeg", format)


@bp.route("/<uuid:pictureId>/thumb.<format>")
def getPictureThumb(pictureId, format):
    """Get picture thumbnail
    ---
    tags:
        - Pictures
    parameters:
        - name: pictureId
          in: path
          description: ID of picture to retrieve
          required: true
          schema:
            type: string
        - name: format
          in: path
          description: Wanted format for output image (for the moment only jpg)
          required: true
          schema:
            type: string
    responses:
        200:
            description: 500px wide ready-for-display image
            content:
                image/jpeg:
                    schema:
                        type: string
                        format: binary
    """
    return utils.pictures.sendThumbnail(pictureId, format)


@bp.route("/<uuid:pictureId>/tiled/<col>_<row>.<format>")
def getPictureTile(pictureId, col, row, format):
    """Get picture tile
    ---
    tags:
        - Pictures
    parameters:
        - name: pictureId
          in: path
          description: ID of picture to retrieve
          required: true
          schema:
            type: string
        - name: col
          in: path
          description: Tile column ID
          required: true
          schema:
            type: number
        - name: row
          in: path
          description: Tile row ID
          required: true
          schema:
            type: number
        - name: format
          in: path
          description: Wanted format for output image (for the moment only jpg)
          required: true
          schema:
            type: string
    responses:
        200:
            description: Tile image (size depends of original image resolution, square with side size around 512px)
            content:
                image/jpeg:
                    schema:
                        type: string
                        format: binary
    """

    utils.pictures.checkFormatParam(format)

    fses = current_app.config["FILESYSTEMS"]

    metadata = utils.pictures.checkPictureStatus(fses, pictureId)
    external_url = utils.pictures.getPublicDerivatePictureExternalUrl(pictureId, format, f"tiles/{col}_{row}.jpg")
    if external_url and metadata["status"] == "ready":
        return redirect(external_url)

    picPath = f"{utils.pictures.getPictureFolderPath(pictureId)}/tiles/{col}_{row}.jpg"

    if metadata["type"] == "flat":
        raise errors.InvalidAPIUsage(_("Tiles are not available for flat pictures"), status_code=404)

    try:
        col = int(col)
    except:
        raise errors.InvalidAPIUsage(_("Column parameter is invalid, should be an integer"), status_code=404)

    if col < 0 or col >= metadata["cols"]:
        raise errors.InvalidAPIUsage(_("Column parameter is invalid"), status_code=404)

    try:
        row = int(row)
    except:
        raise errors.InvalidAPIUsage(_("Row parameter is invalid, should be an integer"), status_code=404)

    if row < 0 or row >= metadata["rows"]:
        raise errors.InvalidAPIUsage(_("Row parameter is invalid"), status_code=404)

    try:
        picture = fses.derivates.openbin(picPath)
    except:
        raise errors.InvalidAPIUsage(_("Unable to read picture on filesystem"), status_code=500)

    return utils.pictures.sendInFormat(picture, "jpeg", format)


@bp.route("/<uuid:pictureId>")
def getPictureById(pictureId):
    """Get picture's STAC definition.

    It's the non-stac alias to the `/api/collections/<collectionId>/items/<itemId>` endpoint (but you don't need to know the collection ID here).
    ---
    tags:
        - Pictures
    parameters:
        - name: pictureId
          in: path
          description: ID of the picture (called item in STAC) to retrieve
          required: true
          schema:
            type: string
    responses:
        102:
            description: the picture (which is still under process)
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
        200:
            description: the wanted picture
            content:
                application/geo+json:
                    schema:
                        $ref: '#/components/schemas/GeoVisioItem'
    """
    from geovisio.web.items import getCollectionItem

    return getCollectionItem(collectionId=None, itemId=pictureId)
