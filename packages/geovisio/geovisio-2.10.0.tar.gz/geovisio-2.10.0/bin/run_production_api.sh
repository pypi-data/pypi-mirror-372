#!/usr/bin/env bash

# script called by the Scalingo Procfile
# use the `USE_GUNICORN` env var to chose between gunicorn and waitress

if [ "${USE_GUNICORN}" == "1" ]; then
    DB_CHECK_SCHEMA=false gunicorn --workers "${NB_API_WORKERS:-5}" --threads "${NB_API_THREADS:-4}" -b ":$PORT" 'geovisio:create_app()'
else
    # use waitress
    DB_CHECK_SCHEMA=false python3 -m waitress --port "$PORT" --url-scheme=https --threads="${NB_API_THREADS:-4}" --trusted-proxy '*' --trusted-proxy-headers 'X-Forwarded-For X-Forwarded-Host X-Forwarded-Port X-Forwarded-Proto' --log-untrusted-proxy-headers --clear-untrusted-proxy-headers --call 'geovisio:create_app'
fi