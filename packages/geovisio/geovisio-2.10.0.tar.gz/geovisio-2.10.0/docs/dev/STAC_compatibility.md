# Deviation of Panoramax API from STAC API

The Panoramax API is as close as possible to the [SpatioTemporal Asset Catalog API specifications](https://github.com/radiantearth/stac-api-spec). We follow the version _1.0.0_ of this standard. However, the Panoramax API has several added routes or properties that distinguish it from a _pure_ STAC API. They are listed in this documentation.

Note that each route is documented precisely in your API specs ([local](http://localhost:5000/api/docs/swagger), [online](https://panoramax.ign.fr/api/docs/swagger)). This page only list **summarized differences** with the standard.

# Metadata

## Landing page (`GET /api`)

### Data extent

The spatial extent of available data is set in `extent` property, in a similar fashion to a [collection extent](https://github.com/radiantearth/stac-api-spec/blob/v1.0.0/stac-spec/collection-spec/collection-spec.md#extent-object).

### Custom links

The `links` section has other specific entries:

- `rel=data & type=application/rss+xml`: link to a RSS feed for getting recently uploaded sequences
- `rel=xyz & type=application/vnd.mapbox-vector-tile`: link to a pattern URL for fetching vector tiles
- `rel=xyz-style & type=application/json`: link to a [MapLibre JSON Style](https://maplibre.org/maplibre-style-spec/)
- `rel=collection-preview & type=image/jpeg`: link to a pattern URL to download a thumbnail of a sequence
- `rel=item-preview & type=image/jpeg`: link to a pattern URL to download a picture thumbnail
- `rel=users`: link to the list of registered users
- `rel=user-info`: link to the detail of a user
- `rel=user-search`: link to the user search API
- `rel=user-xyz & type=application/vnd.mapbox-vector-tile`: link to a pattern URL for fetching vector tiles of a specific user
- `rel=user-xyz-style & type=application/json`: link to a [MapLibre JSON Style](https://maplibre.org/maplibre-style-spec/) of a specific user's vector tiles
- `rel=report & type=application/json`: link to the report API (to post a new report)

## API Configuration (`GET /api/configuration`)

This route doesn't exist in STAC, and is used here to provide information about API configuration (is authentication enabled, what is picture license).

# Sequences

## List of sequences (`GET /api/collections`)

- Custom query parameters:
  - `filter` for filtering using a _Common Query Language_ expression (inspired by [Collection Search STAC extension](https://github.com/stac-api-extensions/collection-search))
    - a special case of filter is the ability to display deleted collections with `filter=status='deleted'`. It's especially useful for crawling system to know that they also need to delete the collections.
  - `created_before` and `created_after` (which are deprecated)

## List of pictures in a sequence (`GET /api/collections/:collectionId/items`)

- Custom query parameters `startAfterRank` and `withPicture`
- No properties `numberMatched` and `numberReturned` in response

### Semantic tags

Key/value semantic tags can be added to a sequence, and can be retrieved inside the `semantic` object of the response.

# Pictures

## Picture metadata (`GET /api/collections/:collectionId/items/:itemId`)

### Response status

According to processing status, HTTP response code can be 102 (under process) or 200 (ready). If picture is under process, some of its assets or metadata can be partial or not available at the moment.

### Custom properties

Many properties are added in the response (for clients not able to read info outside of GeoJSON `properties` object):

- `datetimetz`
- `geovisio:image`
- `geovisio:producer`
- `geovisio:status`
- `geovisio:sorted-by`
- `geovisio:upload-software`
- `geovisio:length_km`
- `geovisio:thumbnail`
- `geovisio:rank_in_collection`
- `original_file:size`
- `original_file:name`
- `panoramax:horizontal_pixel_density`
- `quality:horizontal_accuracy`

Note: `original_file:size` is similar to the size defined by the STAC extension [file](https://github.com/stac-extensions/file), but it cannot be associated to an asset, since the original file has no associated asset (since it will be blurred).

### Tiled assets

360° pictures are split into smaller tiles, we rely on [tiled-assets extension](https://stac-extensions.github.io/tiled-assets/v1.0.0/schema.json) to describe this, but tile matrix definition is not based on a classic spatial reference system.

### Custom links

Links associated to a picture are extended to provide more information, particularly on surrounding pictures.

- Links `rel=prev/next` (previous and next picture in same sequence), which embeds additional properties:
  - `id`: picture UUID
  - `geometry`: GeoJSON representation of picture location
- Links `rel=related` (pictures in other sequences nearby)
  - `id`: picture UUID
  - `geometry`: GeoJSON representation of picture location
  - `datetime`: picture capture datetime (ISO format)

### Semantic tags

Key/value semantic tags can be added to pictures, and can be retrieved inside the `properties.semantics` object of the response.

## Picture search (`GET & POST /api/search`)

No properties `numberMatched` and `numberReturned` are returned in responses.

# Sequences & pictures management

Contrarily to classic STAC API, Panoramax API offer to its users the ability to send and manage their own pictures and sequences. This is done through supplementary API routes:

- `POST /api/collections`
- `PATCH /api/collections/:collectionId`
- `DELETE /api/collections/:collectionId`
- `GET /api/collections/:collectionId/geovisio_status`
- `POST /api/collections/:collectionId/items`
- `PATCH /api/collections/:collectionId/items/:itemId`
- `DELETE /api/collections/:collectionId/items/:itemId`

Note that this is inspired from [Transaction STAC API extension](https://github.com/stac-api-extensions/transaction), but differs in the fact that collections are also possible to create by users, not only items.

# Users and authentication

The following routes are out of STAC-scope and allows to handle users and authentication:

- `GET /api/users/me`
- `GET /api/users/:userId/catalog`
- `GET /api/users/me/catalog`
- `GET /api/users/:userId/collection`
- `GET /api/users/me/collection`
- `GET /api/users/me/tokens`
- `GET /api/users/me/tokens/:tokenId`
- `DELETE /api/users/me/tokens/:tokenId`
- `POST /api/auth/tokens/generate`
- `GET /api/auth/tokens/:tokenId/claim`

# Map data

Picture and sequences metadata are offered through classic vector tiles at various routes:

- MapLibre JSON Styles
  - `GET /api/map/style.json` for all users
  - `GET /api/users/:userId/map/style.json` for a specific user tiles
  - `GET /api/users/me/map/style.json` for authenticated user tiles
- Vector tiles URL
  - `GET /api/map/:z/:x/:y.mvt` for all users tiles
  - `GET /api/users/:userId/map/:z/:x/:y.mvt` for a specific user tiles
  - `GET /api/users/me/map/:z/:x/:y.mvt` for authenticated user tiles

# Reports

The report routes are used to get user feedback on pictures & sequences issues, and are out of STAC-scope:

- `GET /api/reports`
- `POST /api/reports`
- `GET /api/reports/:id`
- `PATCH /api/reports/:id`
- `GET /api/users/me/reports`

# Annotations

Annotations are used to add semantic on part of a picture, and are out of STAC-scope:

- `GET /api/collections/:collectionId/items/:itemId/annotations` to list all annotations for a picture
- `GET /api/collections/:collectionId/items/:itemId/annotations/:annotationId` to get a specific annotation
- `POST /api/collections/:collectionId/items/:itemId/annotations` to create an annotation

# Aliases

Contrary to STAC, in Panoramax, an item (picture) ID is unique, so we added some aliases to ease integrations

* `GET /api/collections/:collectionId/items/:itemId` is equivalent to `GET /api/pictures/:itemId`
* `GET /api/collections/:collectionId/items/:itemId/annotations` is equivalent to `GET /api/pictures/:itemId/annotations`
* `POST /api/collections/:collectionId/items/:itemId/annotations` is equivalent to `POST /api/pictures/:itemId/annotations`
* `GET /api/collections/:collectionId/items/:itemId/annotations/:annotationId` is equivalent to `GET /annotations/:annotationId`
* `PATCH /api/collections/:collectionId/items/:itemId/annotations/:annotationId` is equivalent to `PATCH /annotations/:annotationId`
