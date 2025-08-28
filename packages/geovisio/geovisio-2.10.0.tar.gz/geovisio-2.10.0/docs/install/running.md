# Running Panoramax API

Panoramax is mainly an API and some [pictures background workers](./deep_dive/pictures_processing.md). The pictures workers are technically optional, if they are not spawned the pictures will be processed by the API, but if they are not run, pictures process cannot be retried, are lost on restart...

!!! info "Information"

	Apart in development, you should run both API and picture workers.

!!! warning "Important"

	All Panoramax commands will require some configuration. Be sure to check [the documentation](../install/settings.md) before running the commands.

## Start API

This command starts the HTTP API to serve pictures & sequences to users.

=== ":simple-python: Python package"

    For production context, you want a more robust WSGI server than the Flask's embedded one. Flask team recommend several servers, [check the documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/) to understand the different tradeoff.

    === "🍽️ Waitress"

        You can use [Waitress](https://docs.pylonsproject.org/projects/waitress/en/stable/).

        ```bash
        pip install waitress
        python3 -m waitress --port 5000 --url-scheme=https --call 'geovisio:create_app'
        ```

        You can pass more parameters to `waitress`, like `--threads` to define the number of worker threads run, check the documentation for fine tuning if needed.

    === "🦄 Gunicorn"

        You can use [Gunicorn](https://gunicorn.org/).

        ```bash
        pip install gunicorn
        gunicorn -b :5000 'geovisio:create_app()'
        ```

        You can pass more parameters to `gunicorn`, like `--workers` to define the number of processes and `--threads` to define the number of threads by process, check the documentation for fine tuning if needed.

=== ":simple-docker: Docker"

	```bash
	docker run \
		-e DB_URL=<database connection string> \
		-p 5000:5000 \
		--name geovisio \
		-v <path where to persist pictures>:/data/geovisio \
		panoramax/api:develop \
		api
	```

=== ":simple-docker: :lock: Docker + SSL"

	```bash
	docker run \
		-e DB_URL=<database connection string> \
		-p 5000:5000 \
		--name geovisio \
		-v <path where to persist pictures>:/data/geovisio \
		panoramax/api:develop \
		ssl-api
	```

=== ":simple-docker: :gear: Docker Compose"

	Docker compose is handy to run several services at once, you can spawn the API and the pictures workers with:

	<div class="annotate" markdown>

	```
	docker compose -f <you_compose_file> up --detach (1)
	```

	</div>

	1. This will run all the services in detached mode


=== ":magic_wand: Development API"

	With this you can have hot reload for better development experience.

	```bash
	flask --debug run
	```

	Note that you can also run with another `env` file if you test over many setups:

	```bash
	FLASK_SKIP_DOTENV=1 flask --env-file myconf.env run
	```

	In that case, your `env` file may contain the `FLASK_APP=geovisio` variable to properly start.

## Background worker

This command starts the 1 picture worker, used to process uploaded pictures in the background.

Several workers can run in parallel, you just adjust the number of times you spawn them to the number of CPUs you want to use.

=== ":simple-python: Python package"

	```bash
	flask picture-worker
	```

	Spawning more workers requires running this command several times.

=== ":simple-docker: Docker"

	```bash
	docker run \
		-e DB_URL=<database connection string> \
		-p 5000:5000 \
		--name geovisio-worker \
		-v <path where to persist pictures>:/data/geovisio \
		panoramax/api:develop \
		picture-worker
	```

	!!! note
		This docker container should have access to the same file system used by the API. So you'll likely want to share the volumes between the API containers and the pictures background worker containers

=== ":simple-docker: :gear: Docker Compose"

	As seen below, you can spawn the API and the pictures workers with one command.

	Docker compose also have a way to scale the number of containers of one service.

	```
	docker compose -F <you_compose_file> up background-worker -d --scale background-worker=<VALUE>
	```
