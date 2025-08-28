from geovisio.web import collections, items, prepare, users, utils, upload_set, reports, excluded_areas, pages, annotations
from geovisio.utils import (
    upload_set as upload_set_utils,
    reports as reports_utils,
    excluded_areas as excluded_areas_utils,
    annotations as annotations_utils,
)
from importlib import metadata
import re


API_CONFIG = {
    "openapi": "3.1.0",
    "paths": {
        "/api/docs/specs.json": {
            "get": {
                "summary": "The OpenAPI 3 specification for this API",
                "tags": ["Metadata"],
                "responses": {
                    "200": {
                        "description": "JSON file documenting API routes",
                        "content": {"application/json": {"schema": {"$ref": "https://spec.openapis.org/oas/3.0/schema/2021-09-28"}}},
                    }
                },
            }
        },
        "/api/docs/swagger": {
            "get": {
                "summary": "The human-readable API documentation",
                "tags": ["Metadata"],
                "responses": {"200": {"description": "API Swagger", "content": {"text/html": {}}}},
            }
        },
    },
    "components": {
        "securitySchemes": {
            "bearerToken": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"},
            "cookieAuth": {"type": "apiKey", "in": "cookie", "name": "session"},
        },
        "schemas": {
            "STACLanding": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/core/openapi.yaml#/components/schemas/landingPage"},
            "STACConformance": {"$ref": "http://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/confClasses.yaml"},
            "STACCatalog": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/core/openapi.yaml#/components/schemas/catalog"},
            "STACCollections": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/collections/openapi.yaml#/components/schemas/collections"
            },
            "STACCollection": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/collections/openapi.yaml#/components/schemas/collection"
            },
            "STACProvider": {
                # We cannot reference the STACProvider from the STAC spec because it is defined in an array, so this is a copy of the definition
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"description": "The name of the organization or the individual.", "type": "string"},
                    "description": {
                        "description": "Multi-line description to add further provider information such as processing details for processors and producers, hosting details for hosts or basic contact information.\n\n[CommonMark 0.29](http://commonmark.org/) syntax MAY be used for rich text representation.",
                        "type": "string",
                    },
                    "roles": {
                        "description": "Roles of the provider.\n\nThe provider's role(s) can be one or more of the following\nelements:\n\n* licensor: The organization that is licensing the dataset under\n  the license specified in the collection's license field.\n* producer: The producer of the data is the provider that\n  initially captured and processed the source data, e.g. ESA for\n  Sentinel-2 data.\n* processor: A processor is any provider who processed data to a\n  derived product.\n* host: The host is the actual provider offering the data on their\n  storage. There should be no more than one host, specified as last\n  element of the list.",
                        "type": "array",
                        "items": {"type": "string", "enum": ["producer", "licensor", "processor", "host"]},
                    },
                    "url": {
                        "description": "Homepage on which the provider describes the dataset and publishes contact information.",
                        "type": "string",
                        "format": "url",
                    },
                },
            },
            "STACCollectionItems": {
                # The following link is the one that should be used, but is broken due to geometryCollectionGeoJSON definition
                # "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/featureCollectionGeoJSON"
                # So using instead copy/pasta version
                "type": "object",
                "required": ["type", "features"],
                "properties": {
                    "type": {"type": "string", "enum": ["FeatureCollection"]},
                    "features": {
                        "type": "array",
                        "items": {"$ref": "#/components/schemas/STACItem"},
                    },
                    "links": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/links"
                    },
                    "timeStamp": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/timeStamp"
                    },
                    "numberMatched": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/numberMatched"
                    },
                    "numberReturned": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/numberReturned"
                    },
                },
            },
            "STACItem": {
                # The following link is the one that should be used, but is broken due to geometryCollectionGeoJSON definition
                # "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/item"
                # So using instead copy/pasta version
                "type": "object",
                "description": "A GeoJSON Feature augmented with foreign members that contain values relevant to a STAC entity",
                "required": ["stac_version", "id", "type", "geometry", "bbox", "links", "properties", "assets"],
                "properties": {
                    "type": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/itemType"
                    },
                    "geometry": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/pointGeoJSON"
                    },
                    "properties": {"type": "object", "nullable": "true"},
                    "stac_version": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/stac_version"
                    },
                    "stac_extensions": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/stac_extensions"
                    },
                    "id": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/itemId"
                    },
                    "links": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/links"
                    },
                    "properties": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/properties"
                    },
                    "assets": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/ogcapi-features/openapi.yaml#/components/schemas/assets"
                    },
                },
            },
            "STACExtent": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/collections/openapi.yaml#/components/schemas/extent"},
            "STACExtentTemporal": {
                "type": "object",
                "properties": {
                    "temporal": {
                        "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/collections/openapi.yaml#/components/schemas/extent/properties/temporal"
                    },
                },
            },
            "STACStatsForItems": {"$ref": "https://stac-extensions.github.io/stats/v0.2.0/schema.json#/definitions/stats_for_items"},
            "STACStatsForCollections": {
                "$ref": "https://stac-extensions.github.io/stats/v0.2.0/schema.json#/definitions/stats_for_collections"
            },
            "STACLinks": {
                "type": "object",
                "properties": {
                    "links": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/collections/openapi.yaml#/components/schemas/links"}
                },
            },
            "STACItemSearchBody": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/schemas/searchBody"
            },
            "MapLibreStyleJSON": {
                "type": "object",
                "description": """MapLibre Style JSON, see https://maplibre.org/maplibre-style-spec/ for reference.

Source ID is either \"geovisio\" or \"geovisio_{userId}\".

Layers ID are \"geovisio_grid\", \"geovisio_sequences\" and \"geovisio_pictures\", or with user UUID included (\"geovisio_{userId}_sequences\" and \"geovisio_{userId}_pictures\").

Note that you may not rely only on these ID that could change through time.
""",
                "properties": {
                    "version": {"type": "integer", "example": 8},
                    "name": {"type": "string", "example": "GeoVisio Vector Tiles"},
                    "metadata": {
                        "type": "object",
                        "properties": {
                            "panoramax:fields": {
                                "type": "object",
                                "description": "Available properties per layer (layer: [field1, field2...])",
                            }
                        },
                    },
                    "sources": {
                        "type": "object",
                        "properties": {
                            "geovisio": {
                                "type": "object",
                                "properties": {
                                    "type": {"type": "string", "example": "vector"},
                                    "minzoom": {"type": "integer", "example": "0"},
                                    "maxzoom": {"type": "integer", "example": "15"},
                                    "tiles": {"type": "array", "items": {"type": "string"}},
                                },
                            }
                        },
                    },
                    "layers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "source": {"type": "string"},
                                "source-layer": {"type": "string"},
                                "type": {"type": "string"},
                                "paint": {"type": "object"},
                                "layout": {"type": "object"},
                            },
                        },
                    },
                },
            },
            "GeoVisioLanding": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACLanding"},
                    {
                        "type": "object",
                        "properties": {
                            "extent": {"$ref": "#/components/schemas/STACExtent"},
                            "geovisio_version": {
                                "type": "string",
                                "description": "The GeoVisio API version number",
                                "example": "2.6.0-12-ab12cd34",
                            },
                        },
                    },
                ]
            },
            "GeoVisioCatalog": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACCatalog"},
                    {
                        "type": "object",
                        "properties": {
                            "links": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["href", "rel"],
                                    "properties": {
                                        "stats:items": {"$ref": "#/components/schemas/STACStatsForItems"},
                                        "extent": {"$ref": "#/components/schemas/STACExtentTemporal"},
                                        "geovisio:status": {"$ref": "#/components/schemas/GeoVisioCollectionStatus"},
                                    },
                                },
                            }
                        },
                    },
                ]
            },
            "PreparationParameter": prepare.PreparationParameter.model_json_schema(
                ref_template="#/components/schemas/PreparationParameter/$defs/{model}", mode="serialization"
            ),
            "GeovisioPostToken": {
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "optional description of the token"},
                },
            },
            "GeoVisioPostUploadSet": upload_set.UploadSetCreationParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPostUploadSet/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUploadSet": upload_set_utils.UploadSet.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUploadSet/$defs/{model}", mode="serialization"
            ),
            "GeoVisioAddToUploadSet": upload_set.AddFileToUploadSetParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioAddToUploadSet/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUploadSets": upload_set_utils.UploadSets.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUploadSets/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUploadSetFile": upload_set_utils.UploadSetFile.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUploadSetFile/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUploadSetFiles": upload_set_utils.UploadSetFiles.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUploadSetFiles/$defs/{model}", mode="serialization"
            ),
            "UploadSetUpdateParameter": upload_set.UploadSetUpdateParameter.model_json_schema(
                ref_template="#/components/schemas/UploadSetUpdateParameter/$defs/{model}", mode="serialization"
            ),
            "GeoVisioCollectionOfCollection": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACCollection"},
                    {
                        "type": "object",
                        "properties": {
                            "geovisio:length_km": {"$ref": "#/components/schemas/GeoVisioLengthKm"},
                            "links": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "required": ["href", "rel"],
                                    "properties": {
                                        "stats:items": {"$ref": "#/components/schemas/STACStatsForItems"},
                                        "stats:collections": {"$ref": "#/components/schemas/STACStatsForCollections"},
                                        "extent": {"$ref": "#/components/schemas/STACExtentTemporal"},
                                        "geovisio:status": {"$ref": "#/components/schemas/GeoVisioCollectionStatus"},
                                        "geovisio:length_km": {"$ref": "#/components/schemas/GeoVisioLengthKm"},
                                        "created": {
                                            "type": "string",
                                            "format": "date-time",
                                            "description": "Upload date of the collection",
                                        },
                                        "updated": {
                                            "type": "string",
                                            "format": "date-time",
                                            "description": "Update date of the collection",
                                        },
                                    },
                                },
                            },
                        },
                    },
                ]
            },
            "GeoVisioCSVCollections": {
                "type": "string",
                "description": f"""CSV file containing the collections.

The CSV headers will be:
* id: ID of the collection
* status: Status of the collection
* name: Name of the collection (its title)
* created: Creation date of the collection
* updated: Last update date of the collection
* capture_date: Computed capture date of the collection (date of its first picture)
* minimum_capture_time: Capture datetime of the first picture
* maximum_capture_time: Capture datetime of the last picture
* min_x: Minimum X coordinate of the bounding box of the collection
* min_y: Minimum Y coordinate of the bounding box of the collection
* max_x: Maximum X coordinate of the bounding box of the collection
* max_y: Maximum Y coordinate of the bounding box of the collection
* nb_pictures: Number of pictures in the collection
* length_km: Total length of the collection in kilometers
* computed_h_pixel_density: Horizontal pixel density of the pictures in the collection, if all pictures have the same one
* computed_gps_accuracy: GPS accuracy of the pictures in the collection, if all pictures have the same one

""",
            },
            "GeoVisioCollections": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACCollections"},
                    {"$ref": "#/components/schemas/STACLinks"},
                    {
                        "type": "object",
                        "properties": {"collections": {"type": "array", "items": {"$ref": "#/components/schemas/GeoVisioCollection"}}},
                    },
                ]
            },
            "GeoVisioCollectionsRSS": {
                "type": "object",
                "xml": {"name": "rss"},
                "required": ["version", "channel"],
                "properties": {
                    "version": {"type": "string", "example": "2.0", "xml": {"attribute": True}},
                    "channel": {
                        "type": "object",
                        "required": ["title", "link", "description", "generator", "docs"],
                        "properties": {
                            "title": {"type": "string"},
                            "link": {"type": "string", "format": "uri"},
                            "description": {"type": "string"},
                            "language": {"type": "string"},
                            "lastBuildDate": {"type": "string"},
                            "generator": {"type": "string"},
                            "docs": {"type": "string", "format": "uri"},
                            "image": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string", "format": "uri"},
                                    "title": {"type": "string"},
                                    "link": {"type": "string", "format": "uri"},
                                },
                            },
                            "item": {"type": "array", "items": {"$ref": "#/components/schemas/GeoVisioItemRSS"}},
                        },
                    },
                },
            },
            "GeoVisioProvider": {
                # In geovisio, Provider have an additional optional ID
                "allOf": [
                    {"$ref": "#/components/schemas/STACProvider"},
                    {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                        },
                    },
                ]
            },
            "GeoVisioCollection": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACCollection"},
                    {
                        "type": "object",
                        "properties": {
                            "stats:items": {"$ref": "#/components/schemas/STACStatsForItems"},
                            "geovisio:status": {"$ref": "#/components/schemas/GeoVisioCollectionStatus"},
                            "geovisio:sorted-by": {"$ref": "#/components/schemas/GeoVisioCollectionSortedBy"},
                            "geovisio:upload-software": {"$ref": "#/components/schemas/GeoVisioCollectionUploadSoftware"},
                            "geovisio:length_km": {"$ref": "#/components/schemas/GeoVisioLengthKm"},
                            "quality:horizontal_accuracy": {"type": "number", "title": "Estimated GPS position precision (in meters)"},
                            "quality:horizontal_accuracy_type": {
                                "type": "string",
                                "title": "Estimation process for GPS precision",
                                "example": "95% confidence interval",
                            },
                            "providers": {
                                "type": "array",
                                "items": {
                                    "$ref": "#/components/schemas/GeoVisioProvider",
                                },
                            },
                            "summaries": {
                                "type": "object",
                                "properties": {
                                    "panoramax:horizontal_pixel_density": {
                                        "type": "array",
                                        "title": "Number of pixels on horizon per field of view degree (as a list with a single value for STAC conformance)",
                                        "items": {"type": "integer", "minimum": 0},
                                    },
                                },
                            },
                        },
                    },
                ]
            },
            "GeoVisioCollectionImportStatus": {
                "type": "object",
                "properties": {
                    "status": {"$ref": "#/components/schemas/GeoVisioCollectionStatus"},
                    "items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "status": {"$ref": "#/components/schemas/GeoVisioItemStatus"},
                                "processing_in_progress": {"type": "boolean"},
                                "rank": {"type": "integer"},
                                "nb_errors": {"type": "integer"},
                                "process_error": {"type": "string"},
                                "processed_at": {"type": "string", "format": "date-time"},
                            },
                        },
                    },
                },
            },
            "GeoVisioPostCollection": {
                "type": "object",
                "properties": {"title": {"type": "string", "description": "The sequence title"}},
            },
            "GeoVisioPatchCollection": collections.PatchCollectionParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPatchCollection/$defs/{model}", mode="serialization"
            ),
            "GeoVisioCollectionItems": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACCollectionItems"},
                    {"$ref": "#/components/schemas/STACLinks"},
                    {
                        "type": "object",
                        "properties": {"features": {"type": "array", "items": {"$ref": "#/components/schemas/GeoVisioItem"}}},
                    },
                ]
            },
            "GeoVisioItem": {
                "allOf": [
                    {"$ref": "#/components/schemas/STACItem"},
                    {
                        "type": "object",
                        "properties": {
                            "properties": {
                                "type": "object",
                                "properties": {
                                    "datetimetz": {
                                        "type": "string",
                                        "format": "date-time",
                                        "title": "Date & time of the picture (when it was captured).",
                                    },
                                    "datetimetz": {
                                        "type": "string",
                                        "format": "date-time",
                                        "title": "Date & time of the picture (when it was captured) with original timezone information",
                                    },
                                    "created": {
                                        "type": "string",
                                        "format": "date-time",
                                        "title": "Date & time of picture upload",
                                    },
                                    "updated": {
                                        "type": "string",
                                        "format": "date-time",
                                        "title": "Date & time of picture's metadata update",
                                    },
                                    "geovisio:status": {"$ref": "#/components/schemas/GeoVisioItemStatus"},
                                    "geovisio:producer": {"type": "string"},
                                    "geovisio:image": {"type": "string", "format": "uri"},
                                    "geovisio:thumbnail": {"type": "string", "format": "uri"},
                                    "geovisio:rank_in_collection": {
                                        "type": "integer",
                                        "minimum": 1,
                                        "title": "Rank of the picture in its collection.",
                                    },
                                    "original_file:size": {"type": "integer", "minimum": 0, "title": "Size of the original file, in bytes"},
                                    "original_file:name": {"type": "string", "title": "Original file name"},
                                    "panoramax:horizontal_pixel_density": {
                                        "type": "integer",
                                        "minimum": 0,
                                        "title": "Number of pixels on horizon per field of view degree",
                                    },
                                    "quality:horizontal_accuracy": {
                                        "type": "number",
                                        "title": "Estimated GPS position precision (in meters)",
                                    },
                                },
                            }
                        },
                    },
                ],
            },
            "GeoVisioItemRSS": {
                "type": "object",
                "required": ["title", "link", "description", "author", "pubDate", "point"],
                "properties": {
                    "title": {"type": "string"},
                    "link": {"type": "string", "format": "uri"},
                    "description": {"type": "string"},
                    "author": {"type": "string"},
                    "pubDate": {"type": "string"},
                    "enclosure": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "format": "uri", "xml": {"attribute": True}},
                            "length": {"type": "integer", "xml": {"attribute": True}},
                            "type": {"type": "string", "xml": {"attribute": True}},
                        },
                    },
                    "guid": {"type": "string", "format": "uri"},
                    "point": {"type": "string", "xml": {"namespace": "http://www.georss.org/georss", "prefix": "georss"}},
                    "encoded": {"type": "string", "xml": {"namespace": "http://purl.org/rss/1.0/modules/content/", "prefix": "content"}},
                },
            },
            "GeoVisioPostItem": {
                "type": "object",
                "patternProperties": {
                    r"override_(Exif|Xmp)\..+": {
                        "type": "string",
                        "description": "An EXIF or XMP tag to use instead of existing one in picture file metadata. The query name can be any valid Exiv2 property name.",
                    }
                },
                "properties": {
                    "position": {"type": "integer", "description": "Position of picture in sequence (starting from 1)"},
                    "picture": {
                        "type": "string",
                        "format": "binary",
                        "description": "Picture to upload",
                    },
                    "isBlurred": {
                        "type": "string",
                        "description": "Is picture blurred. If set to 'true', the server will not apply the face blurring algorithm but will publish the image as it is",
                        "enum": ["true", "false", "null"],
                        "default": "false",
                    },
                    "override_capture_time": {
                        "type": "string",
                        "format": "date-time",
                        "description": "datetime when the picture was taken. It will change the picture's metadata with this datetime. It should be an iso 3339 formatted datetime (like '2017-07-21T17:32:28Z')",
                    },
                    "override_latitude": {
                        "type": "number",
                        "format": "double",
                        "description": "latitude of the picture in decimal degrees (WGS84 / EPSG:4326). It will change the picture's metadata with this latitude.",
                    },
                    "override_longitude": {
                        "type": "number",
                        "format": "double",
                        "description": "longitude of the picture in decimal degrees (WGS84 / EPSG:4326). It will change the picture's metadata with this longitude.",
                    },
                },
            },
            "GeoVisioItemSearchBody": {
                "description": "The search criteria",
                "type": "object",
                "allOf": [
                    {"$ref": "#/components/schemas/STACItemSearchBody"},
                    {
                        "type": "object",
                        "properties": {
                            "place_position": {
                                "description": "Geographical coordinates (lon,lat) of a place you'd like to have pictures of. Returned pictures are either 360° or looking in direction of wanted place.",
                                "type": "string",
                                "pattern": r"-?\d+\.\d+,-?\d+\.\d+",
                            },
                            "place_distance": {
                                "description": "Distance range (in meters) to search pictures for a particular place (place_position). Default range is 3-15. Only used if place_position parameter is defined.",
                                "type": "string",
                                "pattern": r"\d+-\d+",
                            },
                            "place_fov_tolerance": {
                                "type": "integer",
                                "minimum": 2,
                                "maximum": 180,
                                "description": """
Tolerance on how much the place should be centered in nearby pictures:

 * A lower value means place have to be at the very center of picture
 * A higher value means place could be more in picture sides

Value is expressed in degrees (from 2 to 180, defaults to 30°), and represents the acceptable field of view relative to picture heading. Only used if place_position parameter is defined.

Example values are:

 * <= 30° for place to be in the very center of picture
 * 60° for place to be in recognizable human field of view
 * 180° for place to be anywhere in a wide-angle picture

Note that this parameter is not taken in account for 360° pictures, as by definition a nearby place would be theorically always visible in it.
""",
                            },
                            "sortby": {
                                "description": """Define the sort order of the results of a search. 
Sort order is defined based on preceding '+' (asc) or '-' (desc).

By default we sort to get the last updated pictures first.

Available properties are:
* `ts`: capture datetime of the picture
* `updated`: sort by updated datetime of the picture
* `id`: us the picture ID for sort
""",
                                "default": "-updated",
                                "type": "string",
                            },
                        },
                    },
                ],
            },
            "GeoVisioPatchItem": items.PatchItemParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPatchItem/$defs/{model}", mode="serialization"
            ),
            "GeoVisioCollectionStatus": {"type": "string", "enum": ["ready", "broken", "preparing", "waiting-for-process"]},
            "GeoVisioLengthKm": {"type": "number", "description": "Total length of sequence (in kilometers)"},
            "GeoVisioCollectionSortedBy": {
                "description": """
Define the pictures sort order of the sequence. Null by default, and can be set via the collection PATCH.
Sort order is defined based on preceding '+' (asc) or '-' (desc).

Available properties are:
* `gpsdate`: sort by GPS datetime
* `filedate`: sort by the camera-generated capture date. This is based on EXIF tags `Exif.Image.DateTimeOriginal`, `Exif.Photo.DateTimeOriginal`, `Exif.Image.DateTime` or `Xmp.GPano.SourceImageCreateTime` (in this order).
* `filename`: sort by the original picture file name
""",
                "type": "string",
                "enum": ["+gpsdate", "-gpsdate", "+filedate", "-filedate", "+filename", "-filename"],
            },
            "GeoVisioCollectionUploadSoftware": {
                "type": "string",
                "enum": ["unknown", "other", "website", "cli", "mobile_app"],
                "description": "Simplified name of software used to create this collection",
            },
            "GeoVisioItemStatus": {
                "type": "string",
                "enum": ["ready", "broken", "waiting-for-process"],
            },
            "GeoVisioPostReport": reports.ReportCreationParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPostReport/$defs/{model}", mode="serialization"
            ),
            "GeoVisioPatchReport": reports.EditReportParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPatchReport/$defs/{model}", mode="serialization"
            ),
            "GeoVisioReport": reports_utils.Report.model_json_schema(
                ref_template="#/components/schemas/GeoVisioReport/$defs/{model}", mode="serialization"
            ),
            "GeoVisioReports": reports_utils.Reports.model_json_schema(
                ref_template="#/components/schemas/GeoVisioReports/$defs/{model}", mode="serialization"
            ),
            "GeoVisioExcludedArea": excluded_areas_utils.ExcludedAreaFeature.model_json_schema(
                ref_template="#/components/schemas/GeoVisioExcludedArea/$defs/{model}", mode="serialization"
            ),
            "GeoVisioExcludedAreas": excluded_areas_utils.ExcludedAreaFeatureCollection.model_json_schema(
                ref_template="#/components/schemas/GeoVisioExcludedAreas/$defs/{model}", mode="serialization"
            ),
            "GeoVisioExcludedAreaCreateFeature": excluded_areas.ExcludedAreaCreateFeature.model_json_schema(
                ref_template="#/components/schemas/GeoVisioExcludedAreaCreateFeature/$defs/{model}", mode="serialization"
            ),
            "GeoVisioExcludedAreaCreateCollection": excluded_areas.ExcludedAreaCreateCollection.model_json_schema(
                ref_template="#/components/schemas/GeoVisioExcludedAreaCreateCollection/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUserList": {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "$ref": "#/components/schemas/GeoVisioUser",
                        },
                    },
                },
            },
            "GeoVisioUserConfiguration": users.UserConfiguration.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUserConfiguration/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUser": users.UserInfo.model_json_schema(
                ref_template="#/components/schemas/GeoVisioUser/$defs/{model}", mode="serialization"
            ),
            "GeoVisioUserAuth": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "format": "uuid"},
                    "name": {"type": "string"},
                    "oauth_provider": {"type": "string"},
                    "oauth_id": {"type": "string"},
                },
            },
            "GeoVisioUserSearch": {
                "type": "object",
                "properties": {
                    "features": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {"type": "string"},
                                "id": {"type": "string", "format": "uuid"},
                                "links": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {"href": {"type": "string"}, "ref": {"type": "string"}, "type": {"type": "string"}},
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "GeoVisioPageName": {"type": "string", "enum": ["end-user-license-agreement", "terms-of-service"]},
            "GeoVisioPageSummary": pages.PageSummary.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPageSummary/$defs/{model}", mode="serialization"
            ),
            "GeoVisioConfiguration": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string", "description": "User-readable server name, in user language"},
                            "langs": {
                                "type": "object",
                                "additionalProperties": "string",
                                "description": "Translated names as lang -> value object",
                                "default": {"en": "GeoVisio"},
                            },
                        },
                    },
                    "description": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string", "description": "User-readable server description, in user language"},
                            "langs": {
                                "type": "object",
                                "additionalProperties": "string",
                                "description": "Translated descriptions as lang -> value object",
                                "default": {"en": "The open source photo mapping solution"},
                            },
                        },
                    },
                    "geo_coverage": {
                        "type": "object",
                        "properties": {
                            "label": {
                                "type": "string",
                                "description": "Instance geographical coverage for pictures uploads, in user language",
                            },
                            "langs": {
                                "type": "object",
                                "additionalProperties": "string",
                                "description": "Translated descriptions as lang -> value object",
                                "default": {"en": "Worldwide\nThe picture can be sent from anywhere in the world."},
                            },
                        },
                    },
                    "logo": {
                        "default": "https://gitlab.com/panoramax/gitlab-profile/-/raw/main/images/logo.svg",
                        "format": "uri",
                        "maxLength": 2083,
                        "minLength": 1,
                        "title": "Logo",
                        "type": "string",
                    },
                    "color": {"default": "#bf360c", "format": "color", "title": "Color", "type": "string"},
                    "email": {"default": "panoramax@panoramax.fr", "format": "email", "title": "Contact email", "type": "string"},
                    "auth": {
                        "type": "object",
                        "properties": {
                            "user_profile": {"type": "object", "properties": {"url": {"type": "string"}}},
                            "enabled": {"type": "boolean"},
                            "registration_is_open": {
                                "type": "boolean",
                                "description": "If true, users can create their own account on the instance. Only used for reference in the federation for the moment",
                            },
                            "enforce_tos_acceptance": {"type": "boolean"},
                        },
                        "required": ["enabled"],
                    },
                    "license": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string", "description": "SPDX id of the license"},
                            "url": {"type": "string"},
                        },
                        "required": ["id"],
                    },
                    "geovisio_version": {
                        "type": "string",
                        "description": "The GeoVisio API version number",
                        "example": "2.6.0-12-ab12cd34",
                    },
                    "defaults": {
                        "type": "object",
                        "properties": {
                            "collaborative_metadata": {
                                "type": "integer",
                                "description": "If `true`, the pictures's metadata will be, by default, editable by all users.",
                            },
                            "split_distance": {
                                "type": "integer",
                                "description": "Maximum distance between two pictures to be considered in the same sequence (in meters). If both split_distance and split_time are None, no split will occur by default.",
                            },
                            "split_time": {
                                "type": "integer",
                                "description": "Maximum time interval between two pictures to be considered in the same sequence. If both split_distance and split_time are None, no split will occur by default.",
                            },
                            "duplicate_distance": {
                                "type": "integer",
                                "description": "Maximum distance between two pictures to be considered as duplicates (in meters). If both duplicate_distance andduplicate_rotation are None, no deduplication will occur by default.",
                            },
                            "duplicate_rotation": {
                                "type": "integer",
                                "description": "Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees).",
                            },
                        },
                        "required": ["collaborative_metadata", "duplicate_distance", "duplicate_rotation", "split_distance", "split_time"],
                    },
                },
                "required": ["auth"],
            },
            "GeoVisioTokens": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "description": {"type": "string"},
                        "generated_at": {"type": "string"},
                        "links": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"href": {"type": "string"}, "ref": {"type": "string"}, "type": {"type": "string"}},
                            },
                        },
                    },
                },
            },
            "GeoVisioEncodedToken": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "description": {"type": "string"},
                    "generated_at": {"type": "string"},
                    "jwt_token": {
                        "type": "string",
                        "description": "this jwt_token will be needed to authenticate future queries as Bearer token",
                    },
                },
            },
            "JWTokenClaimable": {
                "allOf": [
                    {"$ref": "#/components/schemas/GeoVisioEncodedToken"},
                    {
                        "type": "object",
                        "properties": {
                            "links": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "href": {"type": "string"},
                                        "ref": {"type": "string"},
                                        "type": {"type": "string"},
                                    },
                                },
                            }
                        },
                    },
                ]
            },
            "GeoVisioError": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The error message"},
                    "status_code": {"type": "integer", "description": "The HTTP status code"},
                    "payload": {"type": "object", "description": "The error payload"},
                },
            },
            "GeoVisioAnnotation": annotations_utils.Annotation.model_json_schema(
                ref_template="#/components/schemas/GeoVisioAnnotation/$defs/{model}", mode="serialization"
            ),
            "GeoVisioPostAnnotation": annotations.AnnotationPostParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPostAnnotation/$defs/{model}", mode="serialization"
            ),
            "GeoVisioPatchAnnotation": annotations.AnnotationPatchParameter.model_json_schema(
                ref_template="#/components/schemas/GeoVisioPatchAnnotation/$defs/{model}", mode="serialization"
            ),
        },
        "parameters": {
            "STAC_bbox": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/bbox"},
            "STAC_intersects": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/intersects"
            },
            "STAC_datetime": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/datetime"
            },
            "STAC_limit": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/limit"},
            "STAC_ids": {"$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/ids"},
            "STAC_collectionsArray": {
                "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/parameters/collectionsArray"
            },
            "STAC_collections_limit": {
                "name": "limit",
                "in": "query",
                "description": "Estimated number of collections that should be present in response. Defaults to 100. Note that response can contain a bit more or a bit less entries due to internal mechanisms.",
                "required": False,
                "schema": {"type": "integer", "minimum": 1, "maximum": 1000},
            },
            "STAC_collections_filter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering sequences.

Allowed properties are:
 * "created": upload date
 * "updated": last edit date
 * "status": status of the sequence. Can either be "ready" (for collections ready to be served) or "deleted"  for deleted collection. By default, only the "ready" collections will be shown.

Usage doc can be found here: https://docs.geoserver.org/2.23.x/en/user/tutorials/cql/cql_tutorial.html

Examples:

* updated >= '2023-12-31'

* updated BETWEEN '2018-01-01' AND '2023-12-31'

* created <= '2023-01-01' AND updated >= '2018-01-01'
""",
                "required": False,
                "schema": {"type": "string"},
            },
            "tiles_filter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering tiles.

Allowed properties are:
 * "status": status of the sequence. Can either be "ready" (for collections ready to be served) or "hidden" for hidden collections. By default, only the "ready" collections will be shown.

Usage doc can be found here: https://docs.geoserver.org/2.23.x/en/user/tutorials/cql/cql_tutorial.html
""",
                "required": False,
                "schema": {"type": "string"},
            },
            "GeoVisio_place_position": {
                "name": "place_position",
                "in": "query",
                "required": False,
                "description": "Geographical coordinates (lon,lat) of a place you'd like to have pictures of. Returned pictures are either 360° or looking in direction of wanted place.",
                "schema": {"type": "string", "pattern": r"-?\d+\.\d+,-?\d+\.\d+"},
            },
            "GeoVisio_place_distance": {
                "name": "place_distance",
                "in": "query",
                "required": False,
                "description": "Distance range (in meters) to search pictures for a particular place (place_position). Default range is 3-15. Only used if place_position parameter is defined.",
                "schema": {"type": "string", "pattern": r"\d+-\d+", "default": "3-15"},
            },
            "GeoVisio_place_fov_tolerance": {
                "name": "place_fov_tolerance",
                "in": "query",
                "description": """
Tolerance on how much the place should be centered in nearby pictures:

 * A lower value means place have to be at the very center of picture
 * A higher value means place could be more in picture sides

Value is expressed in degrees (from 2 to 180, defaults to 30°), and represents the acceptable field of view relative to picture heading. Only used if place_position parameter is defined.

Example values are:

 * <= 30° for place to be in the very center of picture
 * 60° for place to be in recognizable human field of view
 * 180° for place to be anywhere in a wide-angle picture

Note that this parameter is not taken in account for 360° pictures, as by definition a nearby place would be theorically always visible in it.
""",
                "required": False,
                "schema": {"type": "integer", "minimum": 2, "maximum": 180, "default": 30},
            },
            "GeoVisioSearchSortedBy": {
                "name": "sortby",
                "in": "query",
                "description": """Define the sort order of the results of a search. 
Sort order is defined based on preceding '+' (asc) or '-' (desc).

By default we sort to get the last updated pictures firstn (-updated).

Available properties are:
* `ts`: capture datetime of the picture
* `updated`: sort by updated datetime of the picture
* `id`: us the picture ID for sort
""",
                "required": False,
                "schema": {
                    "type": "string",
                },
            },
            "searchCQL2_filter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering search results.

Only works for semantic search for the moment.

The attributes must start with "semantics." and formated like "semantics.some_key"='some_value'.

Note: it's important for the attribute to be quoted (`"`) and the value to around simple quotes (`'`) to avoid issues with CQL2 parsing.

For the moment only equality (`=`) and list (`IN`) filters are supported. We do not support searching for multiple different tags at once with an `AND` operator (for example, `"semantics.traffic_sign"='yes' AND "semantics.colour"='red'` __will not work__). We suggest to filter data on your side, after retrieving by the main attribute depending on your interest.

To search for any values of a semantic tag, use `semantics.some_key IS NOT NULL` (case matter here).

Examples:

* "semantics.osm|traffic_sign"='yes'
* "semantics.osm|traffic_sign" IS NOT NULL'
* "semantics.osm|amenity" IN ('bench', 'whatever') OR "semantics.osm|traffic_sign"='yes'
""",
                "required": False,
                "schema": {
                    "type": "string",
                },
            },
            "GeoVisioReports_filter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering reports.

Allowed properties are:
 * status: 'open', 'open_autofix', 'waiting', 'closed_solved', 'closed_ignored'
 * reporter: 'me', user account ID or unset
 * owner: 'me', user account ID or unset

Usage doc can be found here: https://docs.geoserver.org/2.23.x/en/user/tutorials/cql/cql_tutorial.html

Examples:

* status IN ('open', 'open_autofix', 'waiting') AND (reporter = 'me' OR owner = 'me')

By default, we only show open or waiting reports, sorted by descending creation date.
""",
                "required": False,
                "schema": {
                    "type": "string",
                    "default": "status IN ('open', 'open_autofix', 'waiting') AND (reporter = 'me' OR owner = 'me')",
                },
            },
            "GeoVisioUserReports_filter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering reports.

Allowed properties are:
 * status: 'open', 'open_autofix', 'waiting', 'closed_solved', 'closed_ignored'
 * reporter: 'me' or unset
 * owner: 'me' or unset

Usage doc can be found here: https://docs.geoserver.org/2.23.x/en/user/tutorials/cql/cql_tutorial.html

Examples:

* status IN ('open', 'open_autofix', 'waiting') AND (reporter = 'me' OR owner = 'me')

By default, we only show open or waiting reports concerning you, sorted by descending creation date.
""",
                "required": False,
                "schema": {
                    "type": "string",
                    "default": "status IN ('open', 'open_autofix', 'waiting') AND (reporter = 'me' OR owner = 'me')",
                },
            },
            "UploadSetFilter": {
                "name": "filter",
                "in": "query",
                "description": """
A CQL2 filter expression for filtering upload sets.

Allowed properties are:
 * completed: TRUE or FALSE
 * dispatched: TRUE or FALSE

Usage doc can be found here: https://docs.geoserver.org/2.23.x/en/user/tutorials/cql/cql_tutorial.html

Examples:

* 'completed = TRUE AND dispatched = FALSE'

By default, we only show non dispatched upload sets.
If you want all the upload sets, you need to set an empty filter or a filter that matches everything.
""",
                "required": False,
                "schema": {"type": "string", "default": "completed=FALSE AND dispatched = FALSE"},
            },
            "OGC_sortby": {
                "name": "sortby",
                "in": "query",
                "required": False,
                "description": """
Define the sort order based on given property. Sort order is defined based on preceding '+' (asc) or '-' (desc).

Available properties are: "created", "updated", "datetime".

Default sort is "-created".
""",
                "schema": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "string",
                        "pattern": "[+|-]?[A-Za-z_].*",
                    },
                },
            },
        },
        "responses": {
            "STAC_search": {
                "description": "the items list",
                "content": {
                    "application/geo+json": {
                        "schema": {
                            "$ref": f"https://api.stacspec.org/v{utils.STAC_VERSION}/item-search/openapi.yaml#/components/schemas/itemCollection"
                        }
                    }
                },
            },
        },
    },
    "specs": [
        {
            "endpoint": "swagger",
            "route": "/api/docs/specs.json",
        }
    ],
    "swagger_ui": True,
    "specs_route": "/api/docs/swagger",
    "swagger_ui_bundle_js": "//unpkg.com/swagger-ui-dist@5.9/swagger-ui-bundle.js",
    "swagger_ui_standalone_preset_js": "//unpkg.com/swagger-ui-dist@5.9/swagger-ui-standalone-preset.js",
    "jquery_js": "//unpkg.com/jquery@2.2.4/dist/jquery.min.js",
    "swagger_ui_css": "//unpkg.com/swagger-ui-dist@5.9/swagger-ui.css",
}
AUTHOR_RGX = re.compile(r"(?P<Name>.*) \<(?P<Email>.*)\>")


def getApiInfo():
    """Return API metadata parsed from pyproject.toml"""
    apiMeta = metadata.metadata("geovisio")

    # url is formatted like 'Home, <url>
    url = apiMeta["Project-URL"].split(",")[1].rstrip()
    # there can be several authors, but we only display the first one in docs
    author = apiMeta["Author-email"].split(",")[0]
    m = AUTHOR_RGX.match(author)
    if not m:
        raise Exception("Impossible to find email in pyproject")
    name = m.group("Name")
    email = m.group("Email")

    return {
        "title": apiMeta["Name"],
        "version": apiMeta["Version"],
        "description": apiMeta["Description"],
        "contact": {"name": name, "url": url, "email": email},
    }


def getApiDocs():
    """Returns API documentation object for Swagger"""

    return {
        "info": getApiInfo(),
        "tags": [
            {"name": "Metadata", "description": "API metadata"},
            {"name": "Sequences", "description": "Collections of pictures"},
            {"name": "Pictures", "description": "Geolocated images"},
            {"name": "Map", "description": "Tiles for web map display"},
            {
                "name": "Upload",
                "description": "Sending pictures & sequences",
                "externalDocs": {"url": "https://docs.panoramax.fr/api/api/api/#upload"},
            },
            {"name": "Editing", "description": "Modifying pictures & sequences"},
            {"name": "Semantics", "description": "Panoramax semantics"},
            {"name": "Reports", "description": "Report issues with pictures & sequences"},
            {"name": "Excluded Areas", "description": "Areas where pictures cannot be uploaded"},
            {"name": "Users", "description": "Account management"},
            {"name": "Auth", "description": "User authentication"},
            {"name": "Configuration", "description": "Various settings"},
        ],
    }
