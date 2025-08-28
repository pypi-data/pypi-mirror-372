# Define allowed or excluded areas

For various reasons, you may want to define where people are allowed to upload pictures. Reasons can be:

- :lock: To ensure no picture is uploaded outside your region
- :eyes: To enforce requests for privacy, hiding private property or private ways
- :material-database: To avoid having too much pictures to store

Panoramax API offers an _excluded areas_ mechanism, where you can set quite easily where people should not send pictures. To configure this, make sure to have first a valid [GeoJSON file](https://geojson.org/) with either all your excluded areas, or all your allowed ones.

## Getting a GeoJSON file

If you don't know what GeoJSON file is, you may want to download or create one that suits your needs.

=== ":globe_with_meridians: For a country"

	Many providers offer ready-to-download GeoJSON files for countries. You can go to [world-geojson](https://github.com/georgique/world-geojson/tree/develop/countries) and download the file for your country.

=== ":material-scissors-cutting: For a specific county/city"

	Websites like [OSM Boundaries](https://osm-boundaries.com/) offer a simple interface to choose a combination or administrative boundaries that you can download as GeoJSON.

=== ":material-pencil: Any custom area"

	Tools like [GeoJSON.io](https://geojson.io/) allows you to draw easily shapes and download them as GeoJSON file.

## Sending your file to the API

Once your GeoJSON file is ready, you can send it to the API using your admin account. First, if you don't have it yet, you need your user token. An instance administrator can get the JWT token of the default instance's account with the flask command `default-account-tokens get`, see the [administrating section](../cli.md#jwt-token-for-the-instance-administrator) for more details.

Then, you can upload your GeoJSON file using a program like _curl_:

=== ":no_entry_sign: GeoJSON of excluded areas"

	```bash
	curl -X PUT "https://my-panoramax.fr/api/configuration/excluded_areas" \
		-H "Authorization: Bearer YOUR_TOKEN_HERE" \
		-H "Content-Type: application/geo+json" \
		--data-binary "@/path/to/your/excluded_areas.geojson"
	```

=== ":white_check_mark: GeoJSON of allowed areas"

	```bash
	curl -X PUT "https://my-panoramax.fr/api/configuration/excluded_areas?invert=true" \
		-H "Authorization: Bearer YOUR_TOKEN_HERE" \
		-H "Content-Type: application/geo+json" \
		--data-binary "@/path/to/your/allowed_areas.geojson"
	```

!!! Note

	The _PUT_ method replaces all excluded areas at once, for a finer, progressive approach, see the section below.

## Fine-managing of excluded areas

Beyond the all-at-once approach, you can also set excluded areas one by one, or add them progressively as you have requests. For example, you can add a publicly shown excluded area like:

```bash
curl -X POST "https://my-panoramax.fr/api/configuration/excluded_areas" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/geo+json" \
     --data '{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-0.1, -0.1],[-0.1, 0.1],[0.1, 0.1],[0.1, -0.1],[-0.1, -0.1]]]},"properties":{"label":"Null Island", "is_public": "true"}}'
```

Changing the `is_public` property to `false` makes the excluded area taken in account by API, but not shown on coverage map offered by API. This is handy for handling privacy requests.

## Checking your excluded areas

After uploading your file, you may want to check if generated areas are matching your expectations. You can get them using this command:

```bash
curl -X GET "https://my-panoramax.fr/api/configuration/excluded_areas?all=true" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -o "all_areas.geojson"
```

And to see what the publicly visible coverage map looks like, you can run:

```bash
curl -X GET "https://my-panoramax.fr/api/configuration/excluded_areas" \
     -o "public_coverage.geojson"
```

## And for more...

Note that API also offer other routes to manage excluded areas, including:

- General excluded areas (apply to all users)
	- `GET /api/configuration/excluded_areas`: list excluded areas
	- `POST /api/configuration/excluded_areas`: add a new general excluded area
	- `PUT /api/configuration/excluded_areas`: replace the whole set of general excluded areas with given ones
	- `DELETE /api/configuration/excluded_areas/{areaId}`: delete an existing excluded area
- Single-user excluded area (apply to user's upload only)
	- `GET /api/users/me/excluded_areas`: list excluded areas for current user
	- `POST /api/users/me/excluded_areas`: add a new excluded area for a specific user
	- `DELETE /api/users/me/excluded_areas/{areaId}`: delete a single excluded area for current user
