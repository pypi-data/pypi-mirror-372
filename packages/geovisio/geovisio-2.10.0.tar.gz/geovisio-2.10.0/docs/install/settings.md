# Available API settings

Panoramax API is highly configurable. All configuration is achieved through environment variables.

## Passing environment variables

### As :material-bash: bash environment variables

You can pass them directly as environment variables:

=== ":simple-python: Python package"

    ```bash
    DB_URL="postgres://gvs:gvspwd@db/geovisio" FS_URL=/data/geovisio flask <command>
    ```

=== "🍽️ Waitress"

    For a production API using waitress, it's the same classic way to give environment variables
    ```bash
    DB_URL="postgres://gvs:gvspwd@db/geovisio" FS_URL=/data/geovisio python3 -m waitress --call 'geovisio:create_app'
    ```

=== "🦄 Gunicorn"

    For a production API using [Gunicorn](https://gunicorn.org/), it's the same classic way to give environment variables
    ```bash
    DB_URL="postgres://gvs:gvspwd@db/geovisio" FS_URL=/data/geovisio gunicorn 'geovisio:create_app()'
    ```

=== ":simple-docker: Docker"

    ```bash
    docker run -e DB_URL="postgres://gvs:gvspwd@db/geovisio" -e FS_URL=/data/geovisio panoramax/api:latest <command>
    ```

=== ":simple-docker: :gear: Docker Compose"

    For Docker Compose, edit the docker compose file and add/update/remove the needed variables on the API or background worker service.

    ``` yaml hl_lines="5-6"
    services:
        api:
            image: panoramax/api:latest
            environment:
                DB_URL: postgres://gvs:gvspwd@db/geovisio
                FS_URL: /data/geovisio
    ```

### :octicons-file-16: .env file

You can also persist those environment variables in a `.env` file.

All tools below will load a file named `.env` if found and if you want to name it differently, you can have your `my_config.env` file and pass it to the API.

=== ":simple-python: Python package"

    ```bash
    flask --env-file my_config.env <command>
    ```

=== "🍽️ Waitress"

    For a production API using waitress, you can wrap it with [python-dotenv](https://github.com/theskumar/python-dotenv).

    ```bash
    dotenv --file my_config.env run waitress-serve --port 5000 --call geovisio:create_app
    ```

=== "🦄 Gunicorn"

    For a production API using [Gunicorn](https://gunicorn.org/), you can wrap it with [python-dotenv](https://github.com/theskumar/python-dotenv).

    ```bash
    dotenv --file my_config.env run gunicorn -b :5000 'geovisio:create_app()'
    ```

=== ":simple-docker: Docker"

    ```bash
    docker run --env-file my_config.env panoramax/api:latest <command>
    ```

## Mandatory parameters

The following parameters must always be defined, otherwise Geovisio will not run.

!!! note
They are automatically set-up when using **Docker compose** install.

- `DB_URL` : [connection string](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) to access the PostgreSQL database. You can alternatively use a set of `DB_PORT`, `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` parameters to configure database access.
- **Filesystem URLs** : to set where all kind of files can be stored. You have two alternatives here. Note that all the following variables use the [PyFilesystem format](https://docs.pyfilesystem.org/en/latest/openers.html) (example: `/path/to/pic/dir` for disk storage, `s3://mybucket/myfolder?endpoint_url=https%3A%2F%2Fs3.fr-par.scw.cloud&region=fr-par` for S3 storage)
  - **Single filesystem** (for simple deployments) : `FS_URL`. In that case, the API will create automatically three subdirectories there (`tmp`, `permanent` and `derivates`).
  - **Separate filesystems** (for large scale deployments) : you have then to set 3 filesystems URLs
    - `FS_TMP_URL` : temporary storage for pictures waiting for blurring (if blur is enabled and necessary for a given picture)
    - `FS_PERMANENT_URL` : definitive storage of original, high-definition, eventually blurred pictures
    - `FS_DERIVATES_URL` : cache storage for serving pictures derivates (thumbnail, tiles, standard-definition version)

## Optional parameters

### :octicons-info-16: Metadata

More information about your organization and API can be set through `API_SUMMARY` parameter. This must be set as JSON following this structure:

```json
{
  "name": { "en": "My server", "fr": "Mon serveur" },
  "description": {
    "en": "This is where I serve pictures",
    "fr": "C'est ici que je propose des photos"
  },
  "geo_coverage": {
    "en": "Europe\nWe only accept pictures in Europe",
    "fr": "Europe\nNous n'acceptons que des photos en Europe"
  },
  "logo": "https://myserver.net/resources/logo.svg",
  "color": "#ff0000",
  "email": "your.best@email.net"
}
```

- `name`: the short name of the server. This is a list of translated names (key is a [ISO 639 language code](https://www.iso.org/iso-639-language-code), with at least `en` defined).
- `description`: a longer description label for the server. This is a list of translated labels (key is a [ISO 639 language code](https://www.iso.org/iso-639-language-code), with at least `en` defined).
- `geo_coverage`: a description of the geographical area where pictures are accepted. You can set it as a two-line label (short version and longer version), and follows the translated label syntax (key is a [ISO 639 language code](https://www.iso.org/iso-639-language-code), with at least `en` defined).
- `logo`: an URL to a SVG file representing the logo of your organization.
- `color`: a HTML-compatible color code (hexadecimal, RGB, HSL, standardized color name...).
- `email`: a public email for contact.

??? tip "Defining a multiline json in :simple-docker: :gear: docker compose"

    Since docker compose uses [YAML](https://fr.wikipedia.org/wiki/YAML), it's quite easy to write a multiline json variable using the `>-` syntax (to remove all new lines).

    ```json
    services:
    api:
        # some definitions of the service
        environment:
            API_SUMMARY: >-
                {
                    "name": {"en": "My server", "fr": "Mon serveur"},
                    "description": {"en": "This is where I serve pictures", "fr": "C'est ici que je propose des photos"},
                    "geo_coverage": {"en": "Europe\nWe only accept pictures in Europe", "fr": "Europe\nNous n'acceptons que des photos en Europe"},
                    "logo": "https://myserver.net/resources/logo.svg",
                    "color": "#ff0000",
                    "email": "your.best@email.net"
                }
    ```

    You can check [the example docker compose file](https://gitlab.com/panoramax/server/api/-/blob/develop/docker/full-osm-auth/docker-compose.yml) for a real example

To improve the reference in the federation, it is possible to also add:

- `API_REGISTRATION_IS_OPEN`: if `true`, users can create their own account directly on the instance. It is only used for reference in the federation for the moment, to tell that people can contribute directly to the instance. Defaults to `false`.

### External serving of pictures files

For performance, it might be handy to serve the pictures by another mean. It's especially true for S3-based storage, where we can save some time and API resources by serving the pictures directly from S3. One could also imagine serving the pictures through an Nginx web server or equivalent:

- `API_PERMANENT_PICTURES_PUBLIC_URL`: External accessible URL for the permanent pictures (the main HD pictures).
- `API_DERIVATES_PICTURES_PUBLIC_URL`: External accessible URL for the derivates pictures.

If you set those parameters, the given pictures location will be returned by the STAC API in collections and search results. Also, `/api/pictures/:id/:kind` routes will redirect to the external URL.

The pictures must be accessible through those URLs, and stored in the same way as Panoramax API does.

For example if `FS_PERMANENT_URL` has been set to `s3://geovisio:SOME_VERY_SECRET_KEY@panoramax-pulic/main-pictures?endpoint_url=http%3A%2F%2Flocalhost:9090`, `API_PERMANENT_PICTURES_PUBLIC_URL` needs to be set to `http://localhost:9090/panoramax-public/main-pictures` (notice the `main-pictures` sub directory in both variables).
If only `FS_URL` has been set, the sub directory needs to be specified too (it's `/permanent` for permanent pictures and `/derivates` for the derivates).

For the moment `API_DERIVATES_PICTURES_PUBLIC_URL` is only possible if all the derivates are pregenerated (`PICTURE_PROCESS_DERIVATES_STRATEGY=PREPROCESS`).

**S3 particularity**

For S3-based storage, the easiest way is to set the bucket used for permanent pictures (and derivates if you also want them) to public read.

This can be done with a command like (if `geovisio-storage-public` is the bucket):

```bash
aws s3api put-bucket-acl --bucket geovisio-storage-public --acl public-read
```

Note: This ACL can also be set on bucket creation.

In minio the command is:

```bash
mc anonymous set download myminio/geovisio-storage-public;
```

### ⚖️ Picture's license

- `API_PICTURES_LICENSE_SPDX_ID`: [SPDX](https://spdx.org) id of the picture's license. If none is set, the pictures's license is considered to be `proprietary`.
- `API_PICTURES_LICENSE_URL`: url to the license.

Only 1 license can be defined per Panoramax instance, and the API will always link the returned pictures to their license.

The instance's license can also be seen in landing page (`/api`), in a `link` with the relation type `license`, as defined by [STAC specification](https://github.com/radiantearth/stac-spec/blob/master/collection-spec/collection-spec.md#license). It can also be accessed through the `/api/configuration` route.

Both those parameters should be either not defined or defined together.

Note: [Panoramax](https://panoramax.fr/) advise the license to either be:

- [etalab-2.0](https://www.etalab.gouv.fr/licence-ouverte-open-licence/)
- [CC-BY-SA-4.0](https://spdx.org/licenses/CC-BY-SA-4.0.html)

### Picture processing

- `API_BLUR_URL` : URL of the blurring API to use. Keep empty for disabling picture blur. See [blur documentation](./deep_dive/blur_api.md) for more info.
- `PICTURE_PROCESS_DERIVATES_STRATEGY` : sets if picture derivates versions should be pre-processed (value `PREPROCESS` to generate all derivates during `process-sequences`) or created on-demand at user query (value `ON_DEMAND` by default to generate at first API call needing the picture).
- `PICTURE_PROCESS_THREADS_LIMIT`: limit the number of thread used to process pictures ([more details in Pictures processing doc](./deep_dive/pictures_processing.md)). Values are: -1 for as many threads as CPU can handle, 0 to disable processing (to run in a separate worker), positive integer for a fixed amount of thread.
- `PICTURE_PROCESS_REFRESH_CRON`: [Cron](https://en.wikipedia.org/wiki/Cron) syntax to tell the background workers when to refresh the database stats (they execute the `flask db refresh` command). Defaults to `"0 2 * * *"` which is every night at 2 PM.
- `PICTURE_PROCESS_NB_RETRIES`: Number of times a job will be retryed if there is a `RecoverableProcessException` during process (like if the blurring api is not reachable). Defaults to 5.
- `PICTURE_PROCESS_KEEP_UNBLURRED_PARTS`: if set to `true`, ask the blurring API to store the unblurred parts of the pictures. Those parts cannot be used without the `blurring_id` returned by the blurring API (no context is kept appart of this id by the blurring API). This can be useful if some blurring was wrongly done, and you want to unblur the pictures. This mechanism is not yet completely implemented by current SGBlur API though.

### :simple-flask: Flask parameters

All [Flask's parameters](https://flask.palletsprojects.com/en/3.0.x/config/#builtin-configuration-values) can be set by prefixing them with `FLASK_`.

Some notables parameters that a production instance will want to set are:

- `FLASK_SECRET_KEY`: [Flask's secret key](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY). A secret key used among other things for securely signing the session cookie. For production should be provided with a long random string as stated in flask's documentation.
- `FLASK_PERMANENT_SESSION_LIFETIME`: [Flask's cookie lifetime](https://flask.palletsprojects.com/en/3.0.x/config/#PERMANENT_SESSION_LIFETIME), number of second before a cookie is invalided (and thus time before the user should log in again). Default is 7 days.
- `FLASK_SESSION_COOKIE_DOMAIN`: [Flask's cookie domain](https://flask.palletsprojects.com/en/3.0.x/config/#SESSION_COOKIE_DOMAIN), should be set to the domain of the instance.
- `FLASK_SESSION_COOKIE_HTTPONLY`: Contrary to flask, default to `true` since Panoramax Website needs it in order to allow front-end to read dynamically the authentication cookie. You can set to it to `false` if you're not planning on using a Panoramax Website.

### Front-end parameters

Some API responses creates links to front-end pages (for example, RSS feed). Panoramax API offer a basic default front-end (Flask templates in `/geovisio/templates` folder), but you may either want to use other Flask templates, or use a completely separated front-end (like [Panoramax Website](https://gitlab.com/panoramax/server/website)).

If you want to override default front-end, you may change:

- `API_MAIN_PAGE`: front page to use. Either a HTML template name (from `/geovisio/templates` folder), or a complete URL to a third-party web page (like `https://my-panoramax.fr/welcome`). Defaults to `main.html`.
- `API_VIEWER_PAGE` : page for the full-page web viewer. Same logic as above. Defaults to `viewer.html`.
- `API_WEBSITE_URL`: URL to the website, used to generate links to the website. If set to `same-host`, the website is assumed to be on the same host as the API (and will respect the host of the current request). If set to `false`, there is no associated website. Defaults to `same-host`.

### 🔐 Authentication & OAuth

These parameters are useful if you want to enable authentication on your Panoramax instance. A short summary of available parameters is listed below, and more details about setting up authentication is available in [External identity providers documentation](./deep_dive/external_Identity_Providers.md).

- `OAUTH_PROVIDER`: external OAuth provider used to authenticate users. If provided can be either `oidc` (for [OpenIdConnect](https://openid.net/connect/)) or `osm`.
- `OAUTH_OIDC_URL`: if `OAUTH_PROVIDER` is `oidc`, url of the realm to use (example: `http://localhost:3030/realms/geovisio` for a Keycloack deployed locally on port `3030`)
- `OAUTH_CLIENT_ID`: OAuth client id as set in the identity provider
- `OAUTH_CLIENT_SECRET`: OAuth client secret as set in the identity provider
- `API_FORCE_AUTH_ON_UPLOAD`: require a login before using the upload API (collection creation and picture upload). Values are `true` or `false` (defaults to `false`)
- `API_DEFAULT_COLLABORATIVE_METADATA_EDITING`: if `true`, the pictures's metadata will be, by default, editable by all users. Note that this parameter is persisted in the database (if it has not been set by the administrator). Instance administrator can edit it in the database. Values are `true` or `false` (defaults to `true`).
- `API_ENFORCE_TOS_ACCEPTANCE`: if `true`, the instance will not accept pictures if the user has not accepted the terms of service (default to `false`). The term of service **must** be defined prior to this by the instance administrator, using the `/api/pages/terms-of-service` routes. If set, the user will be redirected to the term of service page after logging or before uploading pictures.

### :octicons-database-16: Database

- `DB_CHECK_SCHEMA`: Tells Panoramax API to check that the database schema is up to date before starting. If `true` and the schema is not up to date, API will not start. This should be set to `false` only when you know the schema will be updated alongside API, as it might not be able to run correctly with an old database schema. You might want to set it to `false` if you want to upgrade API and the database schema at the same time, and only expose API to your users after the schema migration successfully ended. Values are `true` or `false` (defaults to `true`).
- `DB_MIN_CNX`: minimum number of connections in the connection pool. Default to 0
- `DB_MAX_CNX`: maximum number of connections in the connection pool. Default to 10.
- `DB_STATEMENT_TIMEOUT`: database statement timeout in milliseconds. Default to 5 minutes (300000 ms). Valid for **all** statement executed by API (apart from specificly long queries). Setting it to 0 will disable the timeout.

### :material-server: Infrastructure

- `INFRA_NB_PROXIES` : tell API that it runs behind some proxies, so that it can trust the `X-Forwarded-` headers for URL generation (more details in the [Flask documentation](https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/)).

## :material-sync: Live Parameters

Some parameters can also be set by the instance administrator directly in database. In the future, they will be editable through a back-office, but for the moment, they need to be updated directly in database using SQL queries.

=== ":simple-postgresql: Directly connected to the database"

    ```sql
    UPDATE configurations SET <variable> = <value>
    ```

    And you can set several values at the same time, for example

    ```sql
    UPDATE configurations SET
            default_duplicate_distance = NULL,
            default_duplicate_rotation = NULL,
            default_split_distance = 50,
            default_split_time = interval '2 minutes';
    ```

=== ":simple-docker: :gear: Docker Compose"

    You can pass SQL queries via the Docker Compose containers:
    ```bash
    docker compose exec -it db psql -U gvs -d geovisio -c "UPDATE configurations SET <variable> = <value>"
    ```

### Collaborative editing

- `collaborative_metadata`: same as `API_DEFAULT_COLLABORATIVE_METADATA_EDITING`, if `true`, the pictures's metadata will be, by default, editable by all users. Note that this parameter is persisted in the database (if it has not been set by the administrator). Values are `true` or `false`(defaults to `true`).

### Picture processing

- `default_split_distance`: Maximum distance between two pictures to be considered in the same sequence (in meters). This value can be overridden for each upload set.
- `default_split_time`: Maximum time interval between two pictures to be considered in the same sequence. This value can be overridden for each upload set.
- `default_duplicate_distance`: Maximum distance between two pictures to be considered as duplicates (in meters). This value can be overridden for each upload set.
- `default_duplicate_rotation`: Maximum angle of rotation for two too-close-pictures to be considered as duplicates (in degrees). This value can be overridden for each upload set.

Note that setting both `default_duplicate_distance` and `default_duplicate_rotation` to `null` will result on no deduplication by default, and setting `default_split_distance` and `default_split_time` to `null` will result to all pictures of an upload set to be in the same sequence by default.

## :octicons-bug-16: Debug parameters

The following parameters are useful for monitoring instance status, or enabling some debug functions.

- `API_LOG_LEVEL`: change the logging level. Can be `debug`, `info`, `warn` or `error`. Defaults to `info`.
- `DEBUG_PICTURES_SKIP_FS_CHECKS_WITH_PUBLIC_URL=true`: skip verification of picture file on filesystem if a public URL is defined to access pictures (with `API_PERMANENT_PICTURES_PUBLIC_URL` or `API_DERIVATES_PICTURES_PUBLIC_URL`).
- `API_ACCEPT_DUPLICATE`: makes the instance accept several times the same picture. Can be handy in development context.

### :simple-sentry: Sentry

The crash errors and performance metrics can be sent to a [Sentry](https://sentry.io) instance (whether it's a self-hosted Sentry or sentry.io).

- `SENTRY_DSN`: Sentry [data source name](https://docs.sentry.io/platforms/php/guides/symfony/configuration/options/#dsn)
- `SENTRY_TRACE_SAMPLE_RATE`: percentage of traces to send to Sentry (cf [doc](https://docs.sentry.io/platforms/python/guides/symfony/configuration/options/#traces-sample-rate)).
- `SENTRY_PROFIL_SAMPLE_RATE`: percentage of profile (performance reports) to send to Sentry ([more documentation](https://docs.sentry.io/platforms/python/profiling/?original_referrer=https%3A%2F%2Fwww.google.com%2F#enable-profiling)).
