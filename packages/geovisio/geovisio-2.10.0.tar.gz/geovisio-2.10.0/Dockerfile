FROM python:3.11-slim

# Stable metadata
LABEL org.opencontainers.image.title="GeoVisio API"
LABEL org.opencontainers.image.description="Panoramax is a digital resource for sharing and using field photos. GeoVisio API is the backend part of the ecosystem."
LABEL org.opencontainers.image.authors="Adrien PAVIE <panieravide@riseup.net>"
LABEL org.opencontainers.image.source="https://gitlab.com/panoramax/server/api.git"
LABEL org.opencontainers.image.documentation="https://docs.panoramax.fr/api/"
LABEL org.opencontainers.image.vendor="Panoramax"
LABEL org.opencontainers.image.licenses="MIT"
LABEL org.opencontainers.image.url="https://panoramax.fr/"

# Install system dependencies
# and create a `geovisio` user, to run the app as non root user
RUN apt update \
    && apt install -y git gettext make \
    && pip install waitress gunicorn Babel \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/geovisio /data/geovisio \
    && groupadd --gid 1000 geovisio \
    && useradd --uid 1000 --gid 1000 -m geovisio \
    && chown -R geovisio:geovisio /opt/geovisio /data/geovisio

WORKDIR /opt/geovisio
USER geovisio

# Install Python dependencies
COPY ./README.md ./LICENSE ./pyproject.toml ./
COPY ./geovisio/__init__.py ./geovisio/
RUN pip install -e . --user

# Add source files
COPY ./images ./images/
COPY ./docker/docker-entrypoint.sh ./
COPY ./geovisio ./geovisio
COPY ./migrations ./migrations
COPY ./Makefile ./

# Generate i18n compiled files
USER root
RUN make i18n-po2code
USER geovisio

# Retrieve build metadata
ARG GIT_DESCRIBE
LABEL org.opencontainers.image.revision=$GIT_DESCRIBE

# Environment variables
ENV FLASK_APP=geovisio
ENV FS_URL="/data/geovisio"
ENV API_GIT_VERSION=$GIT_DESCRIBE

# Expose service
EXPOSE 5000
ENTRYPOINT ["./docker-entrypoint.sh"]
