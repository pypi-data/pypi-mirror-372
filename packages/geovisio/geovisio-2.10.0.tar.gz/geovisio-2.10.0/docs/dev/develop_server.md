# Developing on the server

You want to work on Panoramax and offer bug fixes or new features ? That's awesome ! 🤩

Here are some inputs about working with Panoramax API code.

If something seems missing or incomplete, don't hesitate to contact us by [email](mailto:panieravide@riseup.net) or using [an issue](https://gitlab.com/panoramax/server/api/-/issues). We really want Panoramax to be a collaborative project, so everyone is welcome (see our [code of conduct](https://gitlab.com/panoramax/server/api/-/blob/main/CODE_OF_CONDUCT.md)).

## Documentation

Documenting things is important ! 😎 We have three levels of documentation in the API repository:

- Code itself is documented with [Python Docstrings](https://peps.python.org/pep-0257/#what-is-a-docstring)
- HTTP API is documented using [OpenAPI 3](https://spec.openapis.org/oas/latest.html)
- Broader documentation on requirements, install, config (the one you're reading) using Markdown and [Mkdocs](https://www.mkdocs.org/)

### Code documentation

Code documentation is done using docstrings. You can check out the doc in your favorited IDE, or with Python:

```python
import geovisio
help(geovisio)
```

### API documentation

API documentation is automatically served from API itself. You can run it locally by running API:

```bash
flask run
```

Then access it through [localhost:5000/api/docs/swagger](http://localhost:5000/api/docs/swagger).

The API doc is generated from formatted code comments using [Flasgger](https://github.com/flasgger/flasgger). You're likely to find these comments in:

- `geovisio/web/docs.py`: for data structures and third-party specifications
- `geovisio/web/*.py`: for specific routes parameters

If you're changing the API, make sure to add all edited parameters and new routes in docs so users can easily understand how Panoramax works.

### General documentation (Mkdocs)

General documentation is available in the `docs` folder of the repository. You can read it online, or access it locally:

```bash
# Install dependencies
pip install -e .[docs]

# Generate swagger doc, and run mkdocs with a local server
make serve-doc
```

Make sure to keep it updated if you work on new features.

## Testing

We're trying to make Panoramax as reliable and secure as possible. To ensure this, we rely heavily on code testing.

### Unit tests (Pytest)

Unit tests ensure that small parts of code are working as expected. We use the Pytest solution to run unit tests.

You can run tests by following these steps:

- In an environment variable, or a [test.env dot file](https://flask.palletsprojects.com/en/2.2.x/cli/?highlight=dotenv#environment-variables-from-dotenv), add a `DB_URL` parameter, which follows the `DB_URL` [parameter format](../install/settings.md), so you can use a dedicated database for testing
- Run `pytest` command

Unit tests are available mainly in `/tests/` folder, some simpler tests are directly written as [doctests](https://docs.python.org/3/library/doctest.html) in their respective source files (in `/geovisio`).

If you're working on bug fixes or new features, please __make sure to add appropriate tests__ to keep Panoramax level of quality.

Note that tests can be run using Docker with following commands:

```bash
# All tests (including heavy ones)
docker-compose \
	run --rm --build \
	-e DB_URL="postgres://gvs:gvspwd@db/geovisio" \
	backend test  # Replace test by test-ci for only running lighter tests
```

Also note that Pytest tests folders are cleaned-up after execution, temporary files only exist during test running time.

### STAC API conformance

Third-party tool [STAC API Validator](https://github.com/stac-utils/stac-api-validator) is used to ensure that Panoramax API is compatible with [STAC API specifications](https://github.com/radiantearth/stac-api-spec). It is run automatically on our tests and Gitlab CI:

```bash
pytest -vv tests/fixed_data/test_api_conformance.py
```

Note: you need to install the dependencies for this:

```bash
pip install -e .[api-conformance]
```

## Code format

Before opening a pull requests, code need to be formatted with [black](https://black.readthedocs.io).

Install development dependencies:
```bash
pip install -e .[dev]
```

Format sources:
```bash
black .
```

You can also install git [pre-commit](https://pre-commit.com/) hooks to format code on commit with:

```bash
pre-commit install
```

## Translation

Translations are managed with [Flask Babel](https://python-babel.github.io/flask-babel/), which relies on a classic [Python gettext](https://docs.python.org/3/library/gettext.html) mechanism. They are stored under `geovisio/translations/` directory.

Only a few parts of the API needs internationalization, particularly:

- RSS feed of sequences (`/api/collections?format=rss`)
- HTML templates (default API pages)
- Various errors or warnings labels returned in HTTP responses

If you'd like to translate some string in Python code, you can do the following:

```python
from flask_babel import gettext as _
...
print(_("My text is %(mood)s", mood="cool"))
```

For HTML/Jinja templates, you can use this syntax (or [any of these ones](https://jinja.palletsprojects.com/en/3.1.x/templates/#i18n-in-templates)):

```html
<p>{%trans%}My text to translate{%endtrans%}</p>
```

To extract all strings into POT catalog, you can run this command:

```bash
make i18n-code2pot
```

Translation itself is managed through our [Weblate instance](https://weblate.panoramax.xyz/projects/panoramax/), you can go there and start translating or create a new language.

To compile translated PO files into MO files, you can run this command:

```bash
make i18n-po2code
```

Note that if you add support for a new language, you may enable it in `geovisio/__init__.py` in this function:

```python
def get_locale():
	return request.accept_languages.best_match(['fr', 'en'])
```

## Database

### Connection pool

When possible, prefer using a connection from the connection pool instead of creating one.

To acquire a connection to the database, use the context manager, this way the connection will be freed after use:

```python
from geovisio.utils import db

with db.conn(current_app) as conn:
    r = conn.execute("SELECT * FROM some_table", []).fetchall()
```

You can check the `geovisio.utils.db` module for more helpers.

!!! Note

    Those connections have a statement timeout (by default 5 minutes) to avoid very long queries blocking the backend. If a specific query is known to be very long, a connection without this timeout can be aquired as:

    ```python
    from geovisio.utils import db

    with db.long_queries_conn(current_app) as conn:
        ...
    ```

### Adding a new migration

To create a new migration, use [yoyo-migrations](https://ollycope.com/software/yoyo/latest/).

The `yoyo` binary should be available if the Python dependencies are installed.

The preferred way to create migration is to use raw SQL, but if needed a Python migration script can be added.

```bash
yoyo new -m "<a migration name>" --sql
```

(remove the `--sql` to generate a Python migration).

This will open an editor to a migration in `./migrations`.

Once saved, for SQL migrations, always provide another file named like the initial migration but with a `.rollback.sql` suffix, with the associated rollback actions.

Note: each migration is run inside a transaction.

#### Updating large tables

When performing a migration that update a potentially large table (like `pictures` or `pictures_sequence`, that can contains tens of millions rows), we don't want to lock the whole table for too long since it would cause downtime on the instance.

So when possible, the migration of a column should be written in batch (and as a best effort, the code should work on the updated or non updated table if possible).

The migration of pictures table can for example be written like:

```sql
-- transactional: false
-- The comment above is essential for Yoyo migration to skip creating a transaction
-- Disable triggers temporarily (for better performance)
SET session_replication_role = replica;

CREATE OR REPLACE PROCEDURE update_all_pictures_with_important_stuff() AS $$
DECLARE
	last_inserted_at TIMESTAMPTZ;
BEGIN
	SELECT min(inserted_at) - INTERVAL '1 minute' FROM pictures INTO last_inserted_at;

	WHILE last_inserted_at IS NOT NULL LOOP

		WITH 
			-- get a batch of 100 000 pictures to update
			pic_to_update AS (
				SELECT id, inserted_at from pictures where inserted_at > last_inserted_at ORDER BY inserted_at ASC LIMIT 100000
			)
			, updated_pic AS (
				UPDATE pictures 
					SET important_stuff = 'very_important' -- do real update here
					WHERE id in (SELECT id FROM pic_to_update)
			)
			SELECT MAX(inserted_at) FROM pic_to_update INTO last_inserted_at;
		
		RAISE NOTICE 'max insertion date is now %', last_inserted_at;

		-- commit transaction (as a procedure is in an implicit transaction, it will start a new transaction after this)
		COMMIT;

	END LOOP;
	RAISE NOTICE 'update finished';
END
$$ LANGUAGE plpgsql;

-- Actually run the update
CALL update_all_pictures_with_important_stuff();

-- Set back triggers and remove update procedure
SET session_replication_role = DEFAULT;
DROP PROCEDURE update_all_pictures_with_important_stuff;
```

The migrations [`pictures-exiv2`](https://gitlab.com/panoramax/server/api/-/blob/main/migrations/20231018_01_4G3YE-pictures-exiv2.sql) and [`jobs-error`](https://gitlab.com/panoramax/server/api/-/blob/main/migrations/20231110_01_3p070-jobs-error.sql) are real case examples of this.

### Updating an instance database schema

Migrations are technically handled by [yoyo-migrations](https://ollycope.com/software/yoyo/latest/).

For advanced schema handling (like listing the migrations, replaying a migration, ...) you can use all yoyo's command.

For example, you can list all the migrations:

```bash
yoyo list --database postgresql+psycopg://user:pwd@host:port/database
```

Note: the database connection string should use `postgresql+psycopg://` in order to force yoyo to use Psycopg v3.

## Keycloak

To work on authentication functionalities, you might need a locally deployed Keycloak server.

To spawn a configured Keycloak, run:

```bash
docker-compose -f docker/docker-compose-keycloak.yml up
```

And wait for Keycloak to start.

:warning: beware that the configuration is not meant to be used in production!

Then, provide the following variables to your local Panoramax API (either in a custom `.env` file or directly as environment variables, as stated in the [corresponding documentation section](../install/settings.md)).

```.env
OAUTH_PROVIDER='oidc'
FLASK_SECRET_KEY='some secret key'
OAUTH_OIDC_URL='http://localhost:3030/realms/geovisio'
OAUTH_CLIENT_ID="geovisio"
OAUTH_CLIENT_SECRET="what_a_secret"
```

## Links to the Panoramax's instance website

The usual flow is for the [website](https://gitlab.com/panoramax/server/website) to use the API, but for some flows (especially authentication flows), it can be useful to redirect to the website's page. All those links are defined in the [website.py](https://gitlab.com/panoramax/server/api/-/tree/develop/geovisio/utils/website.py) file. Those links should always be optional as the API should work event if no website is available.

There are 2 require pages:
* `/token-accepted`: Page to tell the users the token has been accepted
* `/tos-validation`: Page for the user to validate the terms of service

## Make a release

See [dedicated documentation](./releases.md).
