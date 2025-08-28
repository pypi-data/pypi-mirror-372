# Install Panoramax API

Panoramax API can be installed with different means, you can install it:

* :simple-python: as a Python package, manually or via PyPI
* :simple-docker: with a simple Docker
* ☁️ using a PaaS like [Scalingo](https://scalingo.com/)
* :simple-docker: :fontawesome-solid-gears: with a fully integrated [Docker compose](https://docs.docker.com/compose/)

The manual approach offers a high-level of customization whereas the docker compose/Scalingo approach are more _plug & play_.

!!! note 
	A Panoramax instance always needs an up and running database, as seen in [database setup documentation](./database_setup.md)

## :simple-python: As a Python package

Panoramax API best runs with a recent Linux server and needs at least Python **3.10**

### Install

=== ":simple-python: Via Git :simple-git:"

	You have to run following commands for installing classic dependencies:

	```bash
	# Retrieve API source code
	git clone https://gitlab.com/panoramax/server/api.git geovisio-api
	cd geovisio-api/

	# Enable Python environment
	python3 -m venv env
	source ./env/bin/activate

	# Install Python dependencies
	pip install -e .
	```

=== ":simple-pypi: Via PyPI"

	```bash
	# Enable Python environment
	python3 -m venv geovisio_env
	source ./geovisio_env/bin/activate

	# Install Python dependencies
	pip install geovisio
	```

## ☁️ Scalingo

The Panoramax API can be easily deployed on [Scalingo](https://scalingo.com/) solutions. All [necessary settings](./settings.md) should be defined as environment variables. Various fixtures were defined in Panoramax to make the process as straightforward as possible.

General documentation for deploying applications on Scalingo is [available on their website](https://doc.scalingo.com/platform/deployment/deploy-with-git).

## :simple-docker: Docker

You just need an up-to-date :simple-docker: Docker version. The image is [panoramax/api](https://hub.docker.com/r/panoramax/api) and are tagged by versions.

There are 2 particular tags:

* `latest` is the latest released version
* `develop` is the rolling release for on the edge features

Note: the repository was [geovisio/api](https://hub.docker.com/r/geovisio/api) before being moved to [panoramax/api](https://hub.docker.com/r/panoramax/api). It you still you [geovisio/api](https://hub.docker.com/r/geovisio/api), make sure to update the docker image name to get the lastest versions.

## :simple-docker: Docker Compose

You just need an up to date :simple-docker: Docker version. The Docker compose provided in this repository will install all needed components, including the database. 

Each Docker compose files in the [repository](https://gitlab.com/panoramax/server/api/-/tree/develop/docker) is a demo of a way to setup Panoramax API, but since Panoramax API is quite flexible, not all possibilities are covered.

There is:

__[docker-compose.yaml](https://gitlab.com/panoramax/server/api/-/blob/develop/docker/docker-compose-full.yml)__

:	minimal example with only Panoramax API

__[docker/docker-compose-full.yaml](https://gitlab.com/panoramax/server/api/-/blob/develop/docker/docker-compose-full.yml)__

:	offers a full fledged Panoramax instance (Website, API, database, Keycloak).
	??? note "Note: This does not include a blurring API" by default
		If a blurring API is needed, the `docker-compose-blurring.yml` file can be used alongside it with:
		```bash
		docker compose -f docker/docker-compose-full.yml -f docker/docker-compose-blurring.yml up
		```

	??? note "Note: for linux users, you also need to use the `docker-compose-full-linux.yml` file"
		Due to difference in networking between mac/windows and linux, the `docker-compose-full.yml` file is not able to use the host networking by default.
		To use host networking, you need to use the `docker-compose-full-linux.yml` file.
		```bash
		docker compose -f docker/docker-compose-full.yml -f docker/docker-compose-full-linux.yml up
		```


For more complete setup, you can check the tutorials:

* [Deployment with docker and OSM authentication](tutorials/running_docker_osm_auth.md)
* [Deployment with docker and Keycloak authentication](tutorials/running_docker_keycloak.md)

!!! warning

	The Docker compose files provided in this repository are more meant as examples, and will likely need to be updated to fit your production workflow.
	You will likely need to at least handle :lock: SSL/HTTPS and 🗄️ data backup.

	Feel free to copy the Docker compose file that better suits your needs and adapt it.
