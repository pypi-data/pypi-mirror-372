# Pictures processing

Panoramax API has 2 modes to process pictures.

The pictures processing can either be done directly by the API (as background threads), or delegated to independent picture processing workers.

Using the API to process pictures is easier to deploy, but using independent picture processing workers can be handy to distribute the load on different servers, especially since picture processing can be quite resource consuming for a limited time.

The 2 modes are not exclusives, you can process pictures from the API and also have independent picture processing workers.

Each worker will only process pictures one by one, but several workers can be run in the same time.

## API

The parameter `PICTURE_PROCESS_THREADS_LIMIT` can be used to limit the number of background threads used to process the pictures. If set to `0`, no background thread will be run, so no pictures will be processed unless a separate picture processing worker is run.

## Separate picture processing workers

Separate picture processing workers can be run with the flask endpoint `picture-worker`:

Note: the picture workers use the same environment variables as the API.

=== ":simple-python: Python package"

    When run directly with flask it is done like:

    ```bash
    flask picture-worker
    ```

=== ":simple-docker: Docker"

    There is a separate docker entrypoint that can be used when using docker:

    ```bash
    docker run \
        -e DB_URL=<database connection string>  -e <other variables> \
        --name geovisio-worker \
        panoramax/api:develop \
        picture-worker
    ```

=== ":simple-docker:  :gear: Docker Compose"

    A docker compose example can be viewed as the service `background-worker` of the [docker compose full file](https://gitlab.com/panoramax/server/api/-/blob/main/docker/docker-compose-full.yml).

    In the docker compose example, `5` workers will be run (defined as a [replica](https://docs.docker.com/compose/compose-file/deploy/#replicas))

    To change this number, you can do:

    ```bash
    docker compose up background-worker -d --scale background-worker=<VALUE>
    ```
