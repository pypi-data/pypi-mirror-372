#!/bin/bash

usage() {
    echo "./docker-entrypoint.sh <COMMAND>: "
    echo -e "\tThis script simplifies running GeoVisio backend in a certain mode"
    echo "Commands: "
    echo -e "\tapi (default): Starts web API for production on port 5000 by default"
    echo -e "\tdev-api: Starts web API for development on port 5000 by default"
    echo -e "\tpicture-worker: Starts an independant background worker to process pictures"
    echo -e "\tcleanup: Cleans database and remove Geovisio derivated files (it doesn't delete your original pictures)"
    echo -e "\tdb-upgrade: Upgrade the database schema"
    echo -e "\tdb-refresh: Refresh all materialized views in the database"
}

# default value is api
command=${1:-"api"}
shift

echo "Executing \"${command}\" command"

case $command in
"api")
    python3 -m waitress --port 5000 --threads=${NB_API_THREADS:-4} --call 'geovisio:create_app'
    ;;
"gunicorn-api")
    gunicorn --workers ${NB_API_WORKERS:-5} --threads ${NB_API_THREADS:-4} -b :5000 'geovisio:create_app()'
    ;;
"ssl-api")
    python3 -m waitress --port 5000 --threads=${NB_API_THREADS:-4} --url-scheme=https --trusted-proxy '*' --trusted-proxy-headers 'X-Forwarded-For X-Forwarded-Host X-Forwarded-Port X-Forwarded-Proto' --log-untrusted-proxy-headers --clear-untrusted-proxy-headers  --call 'geovisio:create_app'
    ;;
"picture-worker")
    python3 -m flask picture-worker
    ;;
"dev-api")
    python3 -m flask --debug run --host=0.0.0.0
    ;;
"cleanup")
    python3 -m flask cleanup
    ;;
"db-upgrade")
    python3 -m flask db upgrade
    ;;
"db-refresh")
    python3 -m flask db refresh
    ;;
*)
    usage
    ;;
esac
