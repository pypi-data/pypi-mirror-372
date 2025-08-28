# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Before _1.6.0_, [Viewer](https://gitlab.com/panoramax/clients/web-viewer) was embed in this repository, so this changelog also includes Viewer features until the split.

## [Unreleased]

## [2.10.0] - 2025-08-27

### Added

- Added 2 new parameters on creating/updating an upload set: `no_split` to create only 1 sequence from the upload set pictures and `no_deduplication` not to remove pictures too close from each other.
- Add an `updated` field in all the items's responses.
- Add an `sortby` parameter in search to sort the results (and it can use the new `updated` field).
- Add a way to generate a new token for the current user (via `POST /api/users/me/tokens`).
- Added route aliases to get annotations. 
  * The route `/api/annotations/<uuid:annotationId>` is now an alias of `/api/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations/<uuid:annotationId>`
  * The route `/api/picture/<uuid:pictureId>` is now an alias of `/api/collections/<uuid:collectionId>/items/<uuid:itemId>`
  * The route to create an annotation `/api/picture/<uuid:pictureId>/annotations` is now an alias of `/api/collections/<uuid:collectionId>/items/<uuid:itemId>/annotations`
- Add a way to attach semantic tags to upload sets. Those tags will be transferred to all the collections associated to the upload set. This makes it possible to add semantic tags directly at the upload, without waiting for all the associated collections to be created.
- Add a `relative_heading` parameter to the `/api/upload_sets/:id` route (for `POST` and `PATCH`), to update the relative heading of the upload set. If a `relative_heading` is set on the upload set, it will be applied when computeing the heading of all the associated collections.

### Changed

- Changed the default to split an upload set in several collection, by default we split when a picture is separated from the previous one by 5 minutes or 100 m. This default can be configured by each instance, and overridden for each upload set.
- Changed the default to remove capture duplicates in an upload set, by default we remove pictures less than 1m appart like before and with less than 60° (was 30°). This default can be configured by each instance (by updating the `configurations` table), and overridden for each upload set.
- Posting an empty JSON while patching a picture (`/api/collections/:cid/items/:id`) will now return a 304 instead of a 200.
- update lots of dependencies

### Fixed

- Deleting an unkown upload set now returns a 404 instead of a 500.
- Fix a bug when reorienting a sequence with a single picture would crash the website.
- It's now possible to remove the last semantic from an annotation and add one again when calling `POST /api/collections/:cid/items/:id/annotations` for a shape that already exists.
- Now, if the blurring api rotate a side oriented picture, its size and exif orientation are updated accordingly.

## [2.9.0] - 2025-05-12

### Added

- Add a new configuration `PICTURE_PROCESS_NB_RETRIES` to tell the number of times a job will be retried if there is a `RecoverableProcessException` during process (like if the blurring api is not reachable). Defaults to 5 like before.
- Add a way to search on semantic tags in `/api/search` endpoint with a CQL2 filter like `filter="semantics.some_key"='some_value'`.
- Add a `API_REGISTRATION_IS_OPEN` setting in the API to tell the federation that account can (or not) be created directly on the instance. Defaults to `false`.
- Added field `geovisio:rank_in_collection` to pictures metadata to get the rank of the picture in the collection in `/api/collections/:cid/items/:id` / `/api/collections/:cid/items` and `/api/search` responses. This makes it easier to use the `startAfterRank` parameter to paginate through pictures in collections..
- Handle semantics returned by the blurring API, and automatically add annotations on the pictures with semantic tags on the detected objects..
- Add a new async job `read_metadata` to read the metadata of pictures. This job can read or not the file (depending on the `read_file` boolean in the job's `args` field). This is usefull to update metadata when the geopic-tag-reader library is updated.

### Fixed

- Fix the pagination links when many sequences had the exact same creation date on `/api/collections`.
- Migration `20240409_01_jnhra-pictures-grid.sql` was not working from empty database.
- When asking for collections list as CSV format, API was sending `Content-Type: text/html` instead of `text/csv` in response.
- Fix a sql error on `/api/users/me/collection` when using PostgreSQL <= 13.
- Fix a bug causing a 500 when filtering collections with no updates
- Fix a bug where the collection geometry was not recomputed after a sort.

### Changed

- Change the way the coefficients are computed for the grid, compute the mean only over squares with flat (or 360°) pictures.
- Update lot of dependencies (Flask, psycopg, pillow, sentry, ...)

## [2.8.1] - 2025-03-13

### Added

- Add a way to know the role and permission of the logged user in `/api/users/me`.
- Add the ability to update an upload set parameters through a `PATCH` on `/api/upload_sets/:id`.
- Add a debug endpoint `/api/debug_headers` that can be handy when setting a new instance to check if the proxies are correctly setting the headers.
- Add the ability to add annotations to a part of a picture, with semantic tags associated (through `/api/collections/:id/items/:id/annotations`).

### Fixed

- Fix a bug where dispatching several time the same upload set would not cleanup unused sequences.
- Fix a bug where the relative heading parameter was not correctly validated on null values.

### Changed

- Only display `tos_accepted` field in `/api/users/me` if ToS are mandatory.

## [2.8.0] - 2025-02-10

### Added

- Add the ability to export a user's collections in a CSV file by either providing a `format` query parameter or with the `Accept: text/csv` header. The CSV export is not limited to the first 1000 collections as the JSON API.
- More metadata can be defined for the API in `API_SUMMARY` environment variable: contact email and geographical coverage
- Add the ability to blur again a picture/sequence, by calling the `/api/collections/:id/prepare`/`/api/collections/:id/items/:id/prepare` endpoints.
- Add the ability to change a picture's capture time, latitude and longitude using the PATCH `/api/collections/:id/items/:id` route.
- Add the number of collection to the endpoint `/api/users/:id/collection`
- Add _pages_ management to handle legal mentions and terms of service storage in database. New routes `/api/pages` allow to create, list, delete these pages in several languages.
- In vector tiles, pictures have a new `first_sequence` property for an easier access to sequence UUID.
- Add a way to add tags on pictures and sequences, using the PATCH `/api/collections/:id/items/:id` and `/api/collections/:id` routes.
- Add a way for a user to restrict the collaborative editing of its pictures' metadata. This is done by setting the `collaborative_metadata` field of the user in the authenticated API endpoint `/api/users/me` to `false`. If not set, the instance's `collaborative_metadata` default value is used. If set to `true`, anyone with an account can update the heading / position of a pictures, and the `relative_heading` of a whole sequence.
- Add a CLI command to set the role of an account: `flask user <ACCOUNT_ID_OR_NAME> --set-role <ROLE>` (and the user can be created if not exist with the `--create` flag).
- Add a way to accept the terms of service for a user.

### Changed

- We can now view the files of an upload set as anonymous, without needing to be authenticated. It's because this does not contain any sensitive information (file name, md5, size, ...), not the picture in itself.
- Cameras generic metadata (sensor width, GPS accuracy) are now stored in GeoPicture Tag Reader code instead of a `cameras` table in API database.
- Mark the `/api/users/<uuid:userId>/catalog` route as deprecated, in favor of `/api/users/<uuid:userId>/collection` that supports more filtering/sorting parameters and return more information.
- `/api/users/me/collection` is no longer a HTTP 302 redirect to `/api/users/:userId/collection`, but returns directly the collection of the user.
- The user `elysee` in the example docker compose `docker-compose-full.yml` is now created with the role `admin`.
- If the instance is configured without an explicit `API_DEFAULT_COLLABORATIVE_METADATA_EDITING` settigs, pictures' metadata will be editable by any one with an account.
- If the instance is configured with an explicit `API_ENFORCE_TOS_ACCEPTANCE` setting, the instance will not accept pictures if the user has not accepted the terms of service.

### Fixed

- Fix the upload set dispatch in cases where a picture was not linked to a file (due to a bug at upload time, also fixed). Also retry the dispatch job if it fails.
- List of user collection CSV export was failing for some collections.
- Null Unicode character in EXIF fields was breaking picture insertion in database (commonly found in XPComment field).
- Handle limit parameter in `/api/users/me/catalog` route.
- Doc for vector tiles was not up-to-date (missing properties and old zoom level values).

## [2.7.1] - 2024-11-15

### Added

- Routes returning items/pictures have the `pers:interior_orientation/sensor_array_dimensions` property set, letting users know about original picture dimensions (width/height).
- Add number and coefficient of 360° pictures to the pictures grid. This will makes it possible to display a grid of only 360° pictures.
- Add `missing_fields` list to the `/api/upload_sets/:id/files` response detailling the missing fields from a rejected uploaded picture.
- Details about picture quality are now offered for display and filtering:
  - In sequences and pictures routes: `quality:horizontal_accuracy` for GPS position precision (in meters), `panoramax:horizontal_pixel_density` for pixel density on horizon (px/FOV degree).
  - In vector tiles: `gps_accuracy` and `h_pixel_density` (for **sequences and pictures** layers, not available on grid layer)
- In vector tiles style, a new metadata property `panoramax:fields` lists all available properties in each layer (pictures, sequences, grid). This will allow easier compatibility checks in web viewer.
- Translations in Spanish 🇪🇸 and Hungarian 🇭🇺.

### Changed

- In vector tiles, grid layer is now returning circles instead of polygons. Map style is also adapted for a smoother transition on low zooms (for a heatmap-like effect).
- More EXIF tags are stripped out of database, to reduce used disk space: all keys containing hexadecimal sub-keys are removed (like `Exif.Sony.0x1234`). These fields are still available in original pictures files. A database migration removes them from existing pictures stock in your database (and could possibly take a bit of time to run...). After migration, you may want to run a little `VACUUM` to reclaim disk space.
- Add number and coefficient of 360° pictures to the pictures grid. This will makes it possible to display a grid of only 360° pictures.
- Change the way deleted pictures/upload_sets are handled, objects are removed from the database sooner than before, without needing a flag to tell that the underlying files needed deletion.

### Fixed

- The rejection reason of duplicate files is now `file_duplicate` instead of `invalid_metadata`.
- Fix a bug when loading a picture with a focal length of 0.

## [2.7.0] - 2024-10-10

⚠️ The minimal supported Python version is now 3.10. Note that you can run it with newer python versions as some might bring better performance. ⚠

### Added

- The API and picture workers now use connection pool to reduce the load on the database and improve the performances. The connection pool can be configured using `DB_MIN_CNX`/`DB_MAX_CNX`.
- Add a way to use Gunicorn instead of waitress as WSGI server. Gunicorn can use processes instead of threads, which can result in better performance for high load usage.
- The ID of the associated accounts are now returned in the STAC response in an `id` field in the `providers` field.
- Add a whole new way of uploading pictures, using the new `/api/upload_sets` APIs. The pictures added to the uploaded will be dispatched to one or more collection on completion.
- You can create and manage _Reports_ (issues with pictures or sequences) through `/api/reports` routes. Reports can be created anonymously or by authenticated users, can automatically hide faulty pictures or sequences, and be tracked over time for statistics. **Note** that reports management (beyond creation, which can be done through _web viewer_) is only available through HTTP API as now, no CLI or front-end is offered as now.
- You can create and manage _Excluded areas_ (areas where people should not upload pictures) through `/api/configuration/excluded_areas` and `/api/users/me/excluded_areas` routes. Excluded areas can be defined for everyone, or by user, for fine management. **Note** that this is only manageable through HTTP API, no CLI or front-end is offered as now.
- An user account can be marked with an `admin` role in database to enable some features (access to all reports, edit excluded areas).
- Support of cropped panorama, with new values in `pers:interior_orientation` in picture properties: `visible_area`, `sensor_array_dimensions` following [proposed definition in STAC](https://github.com/stac-extensions/perspective-imagery/issues/10).
- Routes `/api` and `/api/configuration` return API version in a `geovisio_version` attribute (example: `2.6.0-12-ab12cd34`).
- Routes returning collections display a `geovisio:upload-software` property showing which client has been used to create the collection (for meta-catalog statistics).
- Handle user agent `GeoVisioCli` and `PanoramaxCli` as the same `cli` software.

### Changed

- Flask session has been set to `permanent`, thus the session cookie will have the lifetime defined by `FLASK_PERMANENT_SESSION_LIFETIME` (default to 7 days).
- Reject duplicates pictures (same md5). A configuration `API_ACCEPT_DUPLICATE` can make the instance accepts duplicates as before.
- The background jobs have been changed, it should be transparent for the administrator, but they now rely on the new `job_queue` table, and can handle more types of async jobs.
- More metadata can be set on API (name, description, logo and main color) in `API_SUMMARY` setting. This is served through `/api/configuration` and `/api` routes for client-side display.
- Maximum authorized distance between two consecutive pictures in a same segment of a sequence is now 75 meters (distance at 135km/h during two seconds). This only changes map rendering, to avoid sequences cuts over motorways.
- Sequences and Upload Sets creation now stores `User-Agent` HTTP requests headers.
- Minimal required PostGIS version is now 3.4 with PostgreSQL 12.
- Almost all database queries now have a statement timeout (default to 5mn).
- Updated Geopic Tag Reader to 1.3.0 to solve various issues related to pictures timestamps.
- In vector tiles style, `interpolate-hcl` expression for grid colouring has been replaced into `interpolate` for broader compatibility with QGIS versions.
- A new `geovisio:length_km` property is available on `/api/collections/:id`, `/api/users/:id/collection` and `/api/users/me/collection` route, giving the length of sequence in kilometers.
- ⚠️ The docker images are now `panoramax/api` instead of `geovisio/api`.

### Fixed

- RSS feed was producing invalid viewer links (missing coordinates) since sequences are represented as MultiLineString in database.
- Fix a bug where we could add pictures to an already deleted sequence.
- Fix a bug where the `pictures_grid` view was refreshed too frequently (and the computation can be expensive for the database).

### Removed

- The `test-api-conformance.sh` are now regular python tests
- Removed on-the-fly JPEG to WebP conversion (too slow). WebP might do an unexpected come-back in the future 😉
- The list of users has been removed from the API entrypoint (`/`) as the list is ever growning, but it can still be accessed through the `/users` endpoint.

## [2.6.0] - 2024-05-17

⚠️ Important Note: This version add several quite long migrations. After the migration are run, you should run as a database administrator:

```sql
VACUUM FULL pictures, sequences;
```

or use a tool like [pg_repack](https://github.com/reorg/pg_repack) to remove dead tuples and save lot's of space.

Note that the vacuum will hold an exclusive lock whereas pg_repack will not.

⚠️ Important Note ⚠️ : This new versions uses postgres [`session_replication_role`](https://www.postgresql.org/docs/current/runtime-config-client.html) for non blocking migrations. This means that the users used to connect to the database must either have superuser privilege, or if postgres version is >= 15, you can grant the permission to the user with:

```psql
GRANT SET ON PARAMETER session_replication_role TO you_user;
```

### Added

- API routes returning items embed original datetime with timezone information in a new property `datetimetz`.
- New routes offering [MapLibre Style JSON files](https://maplibre.org/maplibre-style-spec/) for each vector tile endpoint (`/api/map/style.json`, `/api/users/me/map/style.json` and `/api/users/:userId/map/style.json`). This will allow more flexibility in offered vector tiles zoom levels and features against clients. These routes are advertised in API landing page with `xyz-style` and `user-xyz-style` links.
- A new configuration `DB_CHECK_SCHEMA` to tell GeoVisio not to check the database schema on startup, use only if you know you'll not use GeoVisio before updating its schema.
- Pictures metadata now embed pitch & roll information (`pers:pitch` and `pers:roll` fields).
- A new configuration `PICTURE_PROCESS_REFRESH_CRON` tell the background workers when to refresh the database stats (they execute the `flask db refresh` command).

### Changed

- All sequences geometries have been updated to be split if pictures were too far apart (linked to change done in [this MR](https://gitlab.com/panoramax/server/api/-/merge_requests/244)).
- Vector tiles from zoom 0 to 5 now offers a grid of available pictures (instead of simplified sequences). They are computed on-demand, so you may want to run `flask db refresh` once a day to keep them up-to-date.
- Doc and links to match the Gitlab organization rename from GeoVisio to Panoramax.

### Fixed

- Migration to change LineString sequence geometry into MultiLinestring was not compatible with older PostGIS version, making Docker image not able to migrate populated sequences tables from 2.4 to 2.5.
- Route `/api/collections/:cid/geovisio_status` was returning non-empty list of items when no pictures was yet associated to the sequence.
- Improve `/api/collections/:cid/geovisio_status` performance for big sequences.
- Improve performance of big sequences deletion in database.

### Removed

- All binary exif fields are removed from the database. This should save quite a lot of database storage.

## [2.5.0] - 2024-03-07

### Added

- Picture search route (`/api/search`) now allows to look for a place that should be visible in pictures. This allows to find pictures for illustrating a POI page. This is done using `place_position`, `place_distance` and `place_fov_tolerance` parameters.
- Route `PATCH /api/collections/:id` has new parameters for editing in a single shot all pictures in a sequence:
  - `relative_heading`: to change all picture headings based on sequence movement track
  - `sortby`: to change the property used to sort pictures in the sequence (GPS date, file date or file name, either ascending or descending order).
- Route `PATCH /api/collections/:col_id/items/:id` has a new parameter for editing a picture's heading.
- Add 2 new tables `pictures_changes` and `sequences_changes` to track updates on `pictures` and `sequences`. Those tables are not yet exposed via an http API.

### Changed

- Updated Geopic Tag Reader to version 1.0.5
- Variable `DB_URL` is not set by default on the Dockerfile anymore, a real value must be given.
- Do not persist binary exif fields. The most notable one is `MakerNote` that took ~15% of the database storage.
- Pictures's are now displayed from zoom level 15 in the tiles to lower the tile's size.
- Collection geometries are now stored as multilinestrings, and split if pictures are too far apart.

### Fixed

- Pytest path in CI for Docker image release.
- When searching collections with a bounding box (in `/api/collections` or `/api/users/:id/collection`), a real intersection is done in the search (before, only the bounding box of the collection was considered).
- Permission problems in Dockerfile when writing to `/data/geovisio`

## [2.4.0] - 2024-01-31

### Added

- Some routes to know information about the users:
  - `/api/users/` to list them
  - `/api/users/search` to search for a user
  - `/api/users/:id` to have information about a given user
- Route `/api/users/{id}/map/{z}/{x}/{y}.{format}` to get user specific information. Those tiles will contains user specific information, even at higher zoom.

### Changed

- Pagination filters are now contained in a `page` query parameter. It should not affect users that should use `next`/`prev`/`first`/`last` links directly, but this should fix some pagination corner cases.
- When searching items with a geometry or bounding box, search items are now sorted by their proximity to the center of the geometry/bounding box.
- Add pagination links to `/api/users/:id/catalog` when needed

### Fixed

- Some requests were failing if a `charset` option was defined in `Content-Type`, as JSON type was not properly .recognized (thanks to Louis Fredice Njako Molom for reporting).
- Improve `/api/search` performance when searching with a bbox (or on a large collection).
- Tiles from `/api/map/{z}/{x}/{y}.{format}` no longer returns user specific information (like hidden pictures/sequences), even for authenticated users.
- Change default limit on the `/api/search` endpoint, from 10 000 to 10.

## [2.3.1] - 2024-01-16

### Added

- Basic `Cache-Control` headers, only setting `public` or `private` for the moment.
- `original_file:size` and `original_file:name` in an item's response's `properties`
- User collection list (`/api/users/:id/collection`) now also supports search with `bbox`, as proposed in [STAC _Collection Search_ extension](https://github.com/stac-api-extensions/collection-search).

### Changed

- Docker container work directory is now `/opt/geovisio`.
- Docker compose file with blurring is lighter, to for easier maintenance.
- Update [geo-picture-tag-reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) to [1.0.3 version](https://gitlab.com/panoramax/server/geo-picture-tag-reader/-/tags/1.0.3).

### Removed

- Tests in Docker are removed, tests can be run locally and are automatically run through repository CI.
- `docker-compose-auth.yml` file, as it is now redundant with `docker-compose-full.yml` (as blurring is separated in a lighter compose file).

## [2.3.0] - 2023-11-30

### Added

- Performance and crash metrics can be sent now to a Sentry server.
- (Almost) full list of picture EXIF tags are shown in `properties.exif` field in API routes returning STAC items. Some keys are skipped because of their low added-value and wide size (maker notes, long binary fields).
- On route `POST /api/collections/:cid/items`, new `override_Exif.*` and `override_Xmp.*` parameters are available to manually define EXIF or XMP tags to override in picture metadata. You can pass any valid [Exiv2](https://exiv2.org/metadata.html) EXIF/XMP tag in query parameters.
- A documentation about [STAC API and GeoVisio API differences](./docs/80_STAC_Compatibility.md).
- Sequences can be filtered by their last update time with `GET /api/collections?filter=...` parameter (uses _Common Query Language_ expression). Deleted sequences can also be show using the `filter` `status` (`filter=status='deleted'`).
- Picture processing will now be retried (10 times) in case the blurring API fails.
- Sequence title can be updated through `PATCH /api/collections/:id` route.

### Changed

- Picture EXIF tags are now stored in database following the [Exiv2](https://exiv2.org/metadata.html) naming scheme. A database migration that could take some time (up to half an hour) is offered to update existing metadata in running instances.
- Upgrade Swagger to 5.9
- Fix a deadlock in the database when a picture is deleted while a worker is preparing it.
- Sequences last updated date corresponds to either last edit of sequence itself or any pictures it embeds.
- Surrounding pictures are listed in details of a single picture (`GET /api/collections/:collectionId/items/:itemId`), as `rel=related` links.
- User detailed catalog (`/api/users/:userId/collection`) now offers paginated and filterable results for its `child` links. Query parameter are `filter, limit, sortby`.
- Tag reader library update to 1.0.2 to fix various fractions value issues.
- `API_MAIN_PAGE` and `API_VIEWER_PAGE` environment variables can now also take a full URL to use instead of default API front-end pages. Useful if you're using a third-party front-end to keep RSS links consistent.

### Fixed

- Tag reader dependency was incorrectly evaluated in pyproject.

### Deprecated

- Parameters `created_before` and `created_after` in `GET /api/collections` route, in favor of `filter` parameter.

## [2.2.0] - 2023-10-10

### Changed

- [GeoPic Tag Reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) updated to 0.4.1 to embed stronger checks on picture coordinates.

### Fixed

- If a picture was having invalid coordinates in its EXIF tags, geometry in database was landing outside of WGS84 bounding box, and `GET /api` returned an invalid spatial extent. API now limits returned bounding box to maximum authorized value for WGS84 projection.

### Added

- a new route: `/api/users/:id/collection` that returns a collection of all the users's collections (can also be accessed with `/api/users/me/collection` with authentication). It's similar to `/api/users/:id/catalog` but with more metadata since a STAC collection is an enhanced STAC catalog.

## [2.1.1] - 2023-09-05

### Added

- On picture upload, some metadata can be passed through HTTP request parameters instead of being read from picture file EXIF tags. Available metadata overrides are: GPS coordinates, capture time and picture type. This allows API clients to handle a wider set of input files (for example GeoPackage, CSV, Shapefile...) without needing to insert all information into picture file.
- To make API compatible with a broader range of clients, the `GET /api/collections/{collectionId}/items` route has new metadata in its `properties` field (`geovisio:producer`, `geovisio:image`, `geovisio:thumbnail`). These properties are duplicated regarding STAC standard (which puts them directly at _Feature_ level) to allow compatibility with clients which only reads metadata from `properties` field (like uMap or QGIS).
- A favicon is shown in default API pages.
- A RSS feed is now offered to list recently uploaded collections, it can be accessed through `GET /api/collections?format=rss` (or with `Accept: application/rss+xml` HTTP request header).
- Collections list (`/api/collections`) now also supports search with `bbox` and `datetime` parameters, as proposed in [STAC _Collection Search_ extension](https://github.com/stac-api-extensions/collection-search).

### Changed

- The Docker compose file `docker-compose-full.yml` now embeds [GeoVisio Website](https://gitlab.com/panoramax/server/website), available on `localhost:3000`.

### Fixed

- Database migration `20230720_01_EyQ0e-sequences-summary` was having a failing SQL request, causing invalid computed sequence metadata being present in database.
- Search parameters `collections` and `ids` for `/api/search` route where not correctly handled when passed through `POST` JSON body.

## [2.1.0] - 2023-07-20

### Added

- A way to customize the picture's license. If none is set, the pictures's license is considered to be proprietary.
- A new route `PATCH /api/collections/:cid` is offered to change visibility of a sequence
- A way to call the vector tiles as an authenticated user. It is mainly used to be able to see objects only visible for this user.
- A `hidden` property in the vector tiles, to mark a sequence or picture as only visible for the owner of this sequence or picture. If the property is not set, the object is visible by all
- A new route `DELETE /api/collections/:cid` is offered to delete a collection. The deletion is done asynchronously.
- A new route `DELETE /api/collections/:cid/items/:id` is offered to delete a picture
- [OpenAPI](https://swagger.io/specification/) conformance tests are now automatically run through `tests/test_api_conformance.sh` script
- [Support of pagination](https://github.com/radiantearth/stac-api-spec/tree/main/ogcapi-features#item-pagination) for `GET /api/collections/:cid/items` API route (`first, last, prev, next` relation types)
  - also support a `?withPicture=:picture_id` query paramater to ask for a page with a specific picture in it
- Add a `flask sequences reorder` subcommand to reorder all or some sequences using the picture's datetime.
- [Support of pagination](https://github.com/radiantearth/stac-api-spec/blob/master/ogcapi-features/README.md#collection-pagination) for `GET /api/collections` API route (`first, last, prev, next` relation types), with a default limit to 100 sequences retrieved per call
- Add 2 optional parameters to the `GET /api/collections` api: `created_after`/`created_before` used to filter the collection by their creation date.
- New properties available in vector tiles for sequences (account ID, camera model, picture type, capture day) and pictures (account ID, camera model, picture type).

### Changed

- Docker compose files now use `latest` API image instead of `develop`
- In default pages (`/` and `/viewer.html`), web viewer version is now synced to current API version instead of develop
- Algorithm used for generating smaller versions of pictures changed from _NEAREST_ to _HAMMING_ for better results
- API documentation and specifications moved to `/api/docs/swagger` and `/api/docs/specs.json`, and with improved readability of their content
- Now heading are recomputed if set to 0 because some camera use this value by default
- Hidden pictures will now always be served through the API to be able to check permissions.

### Fixed

- Raw picture bytes are sent to blurring API instead of Pillow-based version, avoiding various issues (too large files, missing EXIF)
- Docker-compose files are now compatible with MacOS (replaced `network_mode: host` to use a more classic approach)
- Some CORS HTTP headers were missing in API responses to allow client send credentials

## [2.0.2] - 2023-06-08

### Added

- [STAC extension "stats"](https://github.com/stac-extensions/stats) is used on routes `/collections` and `/collections/:id` to add number of items contained in given collection (property `stats:items.count`).
- A new route `PATCH /api/collections/:cid/items/:id` is offered to change visibility of a picture
- A new route `GET /api/collections/:cid/thumbnail.jpg` is offered to get the thumbnail of the first visible picture of a collection
- API landing page (`/api`) better advertises its capabilities:
  - [Web Map Links](https://github.com/stac-extensions/web-map-links) STAC extension is used for vector tiles availability.
  - Custom-defined links `item-preview` and `collection-preview` offer a template URL to have direct access to a thumbnail for either a sequence or a single picture.
- A `geovisio:status` field is added in various API responses (mainly in `/api/collections/:col_id/items` and `/api/collections/:col_id/items/:item_id`) to know if a picture is visible or not. This is mainly useful when retrieving your own sequences and pictures as an authenticated user.
- In vector tiles, in pictures layer, list of sequences associated to a picture is made available in its properties as `sequences` array.

### Changed

- Improved deployment docs
- API route `/users/:userId/catalog/` changes:
  - It sends different results according if you're looking for your own catalog as an authenticated user, or if you're looking to another user catalog. Your own catalog embeds all sequences, others catalogs only display publicly-available sequences.
  - It embeds more properties in a link to child sequence: title, ID, items count, start/end date

### Fixed

- Even if not necessary anymore (with the introduction of user tokens), API was checking if `OAUTH_PROVIDER` was set if you wanted to enable `API_FORCE_AUTH_ON_UPLOAD`.

## [2.0.1] - 2023-05-24

### Added

- Added a `/api/configuration` endpoint with the API configuration. This endpoint is meant to provided easy frontend configuration.
- Support of Bearer token authorization. This should improve API authentication when a browser is not available, for example in usage with the [CLI](https://gitlab.com/panoramax/clients/cli).
- The HTTP response header `Access-Control-Expose-Headers` is added to STAC response to allow web browser using the `Location` header.
- Add API routes to generate a claimable token. By default, it's not associated to any account (created by a `POST` on `/api/auth/tokens/generate`). To be usable, this token needs to be associated to an account via a authenticated call on `/api/auth/tokens/<uuid:token_id>/claim`. This offers a nicer authentication flow on the CLI.
- Add an API route to revoke a token, a `DELETE` on `/api/users/me/tokens/<uuid:token_id>`

### Changed

- Blur picture is called with a `keep=1` URL query parameter (for a coming migration to [SGBlur](https://github.com/cquest/sgblur)) to keep original unblurred parts on blur API side.
- [GeoPic Tag Reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader) updated to 0.1.0 : more EXIF tags are supported for date, heading, GPS coordinates. Also, warnings issued by reader are stored in GeoVisio API database.
- All sources have been moved from `./server/src` to `./geovisio` (thanks to [Nick Whitelegg](https://gitlab.com/nickw1)). Thus, sources are now imported as `import geovisio` instead of `import src`.

### Fixed

- Standard-definition pictures now embeds full EXIF tags from original picture
- Docker compose files were failing if some services were just a bit too long to start

## [2.0.0] - 2023-04-28

### Added

- Add [Providers](https://github.com/radiantearth/stac-api-spec/blob/main/stac-spec/item-spec/common-metadata.md#provider-object) to stac items and collections to have information about the account owning the collection/item
- Add the capability to require a login before creating a sequence and uploading pictures to it
- Add a `/api/users/me` route to get logged in user information, and a `/api/users/me/catalog` to get the catalog of the logged in user.
- Some background picture processes can be run using `flask picture-worker`. Those workers can run on a different server than the API
- Server settings to limit maximum threads: `PICTURE_PROCESS_THREADS_LIMIT`. Set to -1 to use all available threads, 0 to have no background threads at all (use this is you want another server running `flask picture-worker`)
- Added the collection's status in the `/geovisio_status` route.
- Use the python logger instead of print. The logging level can be changed with the `LOG_LEVEL` environment variable.
- The picture upload API route offers a `isBlurred=true` form parameter to skip blurring picture (if it is already blurred by author)
- All read EXIF metadata from pictures is stored in `pictures` tables in a `exif` column
- Filesystem storage can be also configured into 3 different variables for a more flexible storage: `FS_TMP_URL`, `FS_PERMANENT_URL`, `FS_DERIVATES_URL`
- STAC API responses gives `created` time for sequences and pictures (when it was imported), and `updated` time for sequences (last edit time)

### Changed

- Move auth apis from `/auth` to `/api/auth`.
- Docker image moved to [`geovisio/api`](https://hub.docker.com/r/geovisio/api) (was previously `panieravide/geovisio`)
- After the OAuth process launched by `/api/auth/login`, we are redirected to the home page
- Pictures blurring is now **externalized** : GeoVisio API calls a third-party _blurring API_ (which is [available as a part of the whole GeoVisio stack](https://gitlab.com/panoramax/server/blurring)) instead of relying on internal scripts. This allows more flexible deployments. This changes settings like `BLUR_STRATEGY` which becomes `BLUR_URL`.
- Reading of EXIF tags from pictures is now done by a separated library called [Geopic Tag Reader](https://gitlab.com/panoramax/server/geo-picture-tag-reader).
- Pictures derivates are now (again) stored in JPEG format. API still can serve images in both JPEG or WebP formats, but with improved performance if using JPEG
- Thumbnail image is always generated, no matter of `DERIVATES_STRATEGY` value, for better performance on viewer side
- When picture blurring is enabled, original uploaded image is not stored, only blurred version is kept
- Change several environement variables to ensure coherence (but the retrocompatibility has been maintained)
  - `BLUR_URL` => `API_BLUR_URL`
  - `VIEWER_PAGE` => `API_VIEWER_PAGE`
  - `MAIN_PAGE` => `API_MAIN_PAGE`
  - `LOG_LEVEL` => `API_LOG_LEVEL`
  - `FORCE_AUTH_ON_UPLOAD` => `API_FORCE_AUTH_ON_UPLOAD`
  - `DERIVATES_STRATEGY` => `PICTURE_PROCESS_DERIVATES_STRATEGY`
  - `OIDC_URL` => `OAUTH_OIDC_URL`
  - `CLIENT_ID` => `OAUTH_CLIENT_ID`
  - `CLIENT_SECRET` => `OAUTH_CLIENT_SECRET`
  - `NB_PROXIES` => `INFRA_NB_PROXIES`
- Commands `flask set-sequences-heading` and `flask cleanup` now takes in input sequences IDs instead of sequences folder names
- Command `flask cleanup` offers to delete original images, and can't delete blur masks anymore (as they are not used anymore)
- The python files are now directly in the working directory of the docker image, no longer in a `./server` sub directory. It should be transparent for most users though.

### Fixed

- Tests were failing when using PySTAC 1.7.0 due to unavaible `extra_fields['id']` on links
- EXIF tags filled with blank spaces or similar characters were not handled as null, causing unnecessary errors on pictures processing (issues [#65](https://gitlab.com/panoramax/server/api/-/issues/65) and [#66](https://gitlab.com/panoramax/server/api/-/issues/66))
- Make sure picture EXIF orientation is always used and applied ([#71](https://gitlab.com/panoramax/server/api/-/issues/71))
- Updates on DB table `pictures` and deletes on DB table `sequences_pictures` now updates `sequences.geom` column automatically

### Removed

- Removed `SERVER_NAME` from configuration. This parameter was used for url generation, but was causing problems in some cases (cf. [related issue](https://gitlab.com/panoramax/server/api/-/issues/48))
- Removed `BACKEND_MODE` from configuration. This parameter was only used in docker/kubernetes context and can be changed from a environment variable to an argument.
- Removed the `process-sequences` and `redo-sequences` flask's targets. All pictures upload now pass through the API, and the easiest way to do this is to use [geovisio cli](https://gitlab.com/panoramax/clients/cli).
- Removed the `fill-with-mock-data` Flask command
- Pictures and sequences file paths are removed from database (all storage is based on picture ID)

## [1.5.0] - 2023-02-10

### Added

- Viewer sets [various hash URL parameters](./docs/22_Client_URL_settings.md) to save map position, picture ID, focused element and viewer position
- The pictures and sequences are now linked to an account. When importing the sequence, pictures and sequences are either associated to the instance's default account or to the provided `account-name` in the metadata.txt file (cf [documentation](./docs/12_Pictures_storage.md#metadatatxt-configuration-file))
- New index in database for pictures timestamps (to speed up temporal queries)
- API offers an `extent` property in its landing page (`/api/` route), defining spatio-temporal extent of available data (in the same format as [STAC Collection extent](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#extent-object)). Note that this is **not STAC-standard**, it may evolve following [ongoing discussions](https://github.com/radiantearth/stac-spec/issues/1210).
- Documentation to [deploy GeoVisio API on Scalingo](./docs/10_Install_Scalingo.md)
- Authentication handling using an external OAuth2 provider. See the [external identity provider documentation](./docs/12_External_Identity_Providers.md) and [Api usage documentation](./docs/16_Using_API.md#authentication)
- Refactor docker-compose files. Removal of the docker-compose-dev.yaml (integrated in the main docker-compose.yml file), and add of several other docker-compose files in the [docker/](./docker/) directory.

### Changed

- Viewer displays picture date when picture is focused instead of static text "GeoVisio"
- Conformance of API against STAC specifications is improved:
  - List of conformance URLs is more complete
  - Collection temporal extent is always returned in UTC timezone
  - Summaries of some fields are provided in collections
  - Links in collections have now titles
  - Empty fields are now not returned at all, instead of returned with `null` values
  - Content types for GeoJSON routes are now set precisely
  - Providers list is set to an empty array for collections
  - Listing of all users catalogs in main catalog (landing)
  - `/search` route supports `POST` HTTP method

### Fixed

- Some picture metadata fields were duplicated in database (existing both as standalone columns and in `metadata` field), now `metadata` only contains info not existing in other columns.
- More robust testing of `None` values for server settings

### Removed

- The configuration cannot be stored in a `config.py` file anymore, either use environment variables, or install [python-dotenv](https://github.com/theskumar/python-dotenv) (it's in the requirements-dev.txt file) and persist the variables in either the default `.env` file or a custom `*.env` file (like `prod.env`) and pass this file to flask with the `--env-file` (or `-e`) option.

```bash
flask --env-file prod.env run
```

- The `TEST_DB_URL` environment variable is no longer available for the tests, replaced by the standard `DB_URL`

## [1.4.1] - 2023-02-01

### Fixed

- Improve checks to avoid failures due to invalid `WEBP_METHOD` parameter

## [1.4.0] - 2023-01-04

**About upgrading from versions <= 1.3.1** : many changes have been done on storage and settings during pictures import, to avoid issues you may do a full re-import of your pictures and sequences. This can be done with following command (to adapt according to your setup):

```bash
cd server/
FLASK_APP="src" flask cleanup
FLASK_APP="src" flask process-sequences
```

### Added

- Home and viewer pages can be changed using `MAIN_PAGE` and `VIEWER_PAGE` settings (thanks to Nick Whitelegg)
- Docker compose file for local development (in complement of existing file which uses pre-built Docker image)
- Explicitly document that database should be in UTF-8 encoding (to avoid [binary string issues with Psycopg](https://www.psycopg.org/psycopg3/docs/basic/adapt.html#strings-adaptation))
- Server tests can be run through Docker
- API can serve pictures in both JPEG and WebP formats
- Viewer now supports WebP assets, and are searched for in priority
- Mock images and sequences can be generated for testing with `fill-mock-data` server command (thanks to Antoine Desbordes)
- Viewer map updates automatically URL hash part with a `map` string
- API map tiles offers a `sequences` layer for display sequences paths
- Database migrations are handled with the [Yoyo migrations framework](https://ollycope.com/software/yoyo/latest/)

### Changed

- Derivates picture files are now by default generated on-demand on first API request. Pre-processing of derivates (old method) can be enabled using `DERIVATES_STRATEGY=PREPROCESS` setting when calling `process-sequences` command.
- Internal storage format for pictures is now WebP, offering same quality with reduce disk usage.
- If not set, `SERVER_NAME` defaults to `localhost.localdomain:5000`
- Reduced size of Docker image by limiting YOLOv6 repository download and removing unused torchaudio dependency
- Server dependencies are now separated in 3 pip requirements files for faster CI: `requirements.txt`, `requirements-dev.txt` and `requirements-blur.txt`
- During sequences processing, ready pictures can be shown and queried even if whole sequences is not ready yet
- Improved CLI commands documentation (which appears using `FLASK_APP="src" flask --help`)
- Heading in pictures metadata is now optional, and is set relatively to sequence movement path if missing
- New CLI command `set-sequences-heading` allows user to manually change heading values
- Viewer supports STAC items not having `view:azimuth` property defined
- All documentation files are now in `docs/` folder, with better readability and consistency

### Fixed

- Some sequences names were bytestring instead of string, causing some STAC API calls to fail
- YOLOv6 release number is now fixed in code to avoid issues in downloaded models
- Docker-compose files explicitly wait for PostgreSQL database to be ready to prevent random failures
- With `COMPROMISE` blur strategies, image not needing blurring failed
- URL to API documentation written without trailing `/` was not correctly handled
- Pictures with partial camera metadata are now correctly handled

### Removed

- No progressive JPEG is used anymore for classic (non-360°) HD pictures.

## [1.3.1] - 2022-08-03

### Added

- A cleaner progress bar (tqdm) is used for progress of sequences processing
- Picture heading is also read from `PoseHeadingDegrees` XMP EXIF tag

### Changed

- Pictures derivates folder is renamed from `gvs_derivates` to `geovisio_derivates` for better readability
- Sequences folder can skip processing if their name starts with either `ignore_`, `gvs_` or `geovisio_`
- Status of pictures and sequences is now visible in real-time in database (instead of one transaction commited at the end of single sequence processing)

### Fixed

- Add version in docker-compose file for better compatibility

## [1.3.0] - 2022-07-20

### Added

- Support of flat / non-360° pictures in viewer and server
- List of contributors and special thanks in readme
- Introduced changelog file (the one you're reading 😁)
- Allow direct access to MapLibre GL map object in viewer using `getMap`
- Allow passing all MapLibre GL map settings through viewer using `options.map` object

### Changed

- Pictures blurring now offers several strategies (`BLUR_STRATEGY` setting) and better performance (many thanks to Albin Calais)
- Viewer has a wider zoom range
- Separate stages for building viewer and server in Dockerfile (thanks to Pascal Rhod)

### Fixed

- Test pictures had some corrupted EXIF tags (related to [JOSM issue](https://josm.openstreetmap.de/ticket/22211))

## [1.2.0] - 2022-06-07

### Added

- A demonstration page is available, showing viewer and code examples
- A map is optionally available in viewer to find pictures more easily
- New API route for offering vector tiles (for map) : `/api/map/<z>/<x>/<y>.mvt`
- GeoVisio now has a logo

### Changed

- Improved Dockerfile :
  - Both server and viewer are embed
  - Add list of available environment variables
  - Remove need for a config file
  - A Docker compose file is offered for a ready-to-use GeoVisio with database container
- Server processing for sequences pre-render all derivates versions of pictures to limit I/O with remote filesystems
- Viewer displays a default picture before a real picture is loaded
- Documentation is more complete

### Fixed

- Reading of negative lat/lon coordinates from EXIF tags

## [1.1.0] - 2022-05-09

### Added

- Support of [STAC API scheme](https://github.com/radiantearth/stac-api-spec) for both server and viewer
- New environment variables for database to allow set separately hostname, port, username... : `DB_PORT`, `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME`

### Changed

- All API routes are prefixed with `/api`

### Removed

- `/sequences` API routes, as they are replaced by STAC compliant routes named `/collections`
- Some `/pictures` API routes, as they are replaced by STAC compliant routes named `/collections/<id>/items`

## [1.0.0] - 2022-03-22

### Added

- Server scripts for processing 360° pictures and loading into database
- Support of various filesystems (hard disk, FTP, S3 Bucket...) using PyFilesystem
- API offering sequences, pictures (original, thumbnail and tiled) and various metadata
- Blurring of people, cars, trucks, bus, bicycles on pictures
- Viewer based on Photo Sphere Viewer automatically calling API to search and retrieve pictures
- Dockerfile for easy server setup

[Unreleased]: https://gitlab.com/panoramax/server/api/-/compare/2.10.0...develop
[2.10.0]: https://gitlab.com/panoramax/server/api/-/compare/2.9.0...2.10.0
[2.9.0]: https://gitlab.com/panoramax/server/api/-/compare/2.8.1...2.9.0
[2.8.1]: https://gitlab.com/panoramax/server/api/-/compare/2.8.0...2.8.1
[2.8.0]: https://gitlab.com/panoramax/server/api/-/compare/2.7.1...2.8.0
[2.7.1]: https://gitlab.com/panoramax/server/api/-/compare/2.7.0...2.7.1
[2.7.0]: https://gitlab.com/panoramax/server/api/-/compare/2.6.0...2.7.0
[2.6.0]: https://gitlab.com/panoramax/server/api/-/compare/2.5.0...2.6.0
[2.5.0]: https://gitlab.com/panoramax/server/api/-/compare/2.4.0...2.5.0
[2.4.0]: https://gitlab.com/panoramax/server/api/-/compare/2.3.1...2.4.0
[2.3.1]: https://gitlab.com/panoramax/server/api/-/compare/2.3.0...2.3.1
[2.3.0]: https://gitlab.com/panoramax/server/api/-/compare/2.2.0...2.3.0
[2.2.0]: https://gitlab.com/panoramax/server/api/-/compare/2.1.1...2.2.0
[2.1.1]: https://gitlab.com/panoramax/server/api/-/compare/2.1.0...2.1.1
[2.1.0]: https://gitlab.com/panoramax/server/api/-/compare/2.0.2...2.1.0
[2.0.1]: https://gitlab.com/panoramax/server/api/-/compare/2.0.0...2.0.1
[2.0.0]: https://gitlab.com/panoramax/server/api/-/compare/1.5.0...2.0.0
[1.5.0]: https://gitlab.com/panoramax/server/api/-/compare/1.4.1...1.5.0
[1.4.1]: https://gitlab.com/panoramax/server/api/-/compare/1.4.0...1.4.1
[1.4.0]: https://gitlab.com/panoramax/server/api/-/compare/1.3.1...1.4.0
[1.3.1]: https://gitlab.com/panoramax/server/api/-/compare/1.3.0...1.3.1
[1.3.0]: https://gitlab.com/panoramax/server/api/-/compare/1.2.0...1.3.0
[1.2.0]: https://gitlab.com/panoramax/server/api/-/compare/1.1.0...1.2.0
[1.1.0]: https://gitlab.com/panoramax/server/api/-/compare/1.0.0...1.1.0
[1.0.0]: https://gitlab.com/panoramax/server/api/-/commits/1.0.0
