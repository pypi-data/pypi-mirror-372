# API documentation

Welcome to Panoramax __API__ documentation ! It will help you through all phases of setup, run and develop on Panoramax API and backend.

!!! note

	If at some point you're lost or need help, you can contact us through [issues](https://gitlab.com/panoramax/server/api/-/issues), by [email](mailto:panoramax@panoramax.fr) or on [Matrix channels](https://matrix.to/#/#panoramax-space:matrix.org).

## Architecture overview

Panoramax API is the backend powering a Panoramax instance.

<div class="grid cards" markdown>

- :simple-flask:{ .lg .middle } **API**

    ---

    A [Python](https://www.python.org/) API the [Flask framework](https://flask.palletsprojects.com/).

- :simple-postgresql:{ .lg .middle } **Database**

    ---

    A [PostgreSQL](https://www.postgresql.org/) database with the [PostGIS](https://postgis.net/) extension.

- :simple-python:{ .lg .middle } **Pictures Workers**

    ---

    For better handling of uploaded pictures, several [Picture Workers](./install/deep_dive/pictures_processing.md) can be run alongside the API, they will regularly poll the database to check for pictures to process.


- 🗄️ **Flexible storage**

    ---

    Flexible storage for uploaded pictures, on files or object storage.


- 🔐 **OAuth**

    ---

    Optional external OAuth2 provider to handle authentication

- 🙈 **External blurring API**

    ---

    Optional external [blurring API](./install/deep_dive/blur_api.md)

</div>

??? example "Architecture diagram"

    ![Architecture overview](./images/geovisio-architecture-simple.png)


## How to host

Panoramax API setup is quite flexible, deep dive in the documentation to see how to host you own Panoramax instance.

[:octicons-arrow-right-24: How to install](./install/install.md)

## Using the API

Panoramax offers a REST API to access collections (sequences), items (pictures) and their metadata.

[:octicons-arrow-right-24: How to use the API](./api/api.md)
