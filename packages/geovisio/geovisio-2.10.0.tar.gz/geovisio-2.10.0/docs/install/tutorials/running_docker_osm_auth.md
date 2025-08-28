# A complete Panoramax deployment with :simple-openstreetmap: OpenStreetMap authentication

Here is a simple example on how to host a Panoramax instance based on a simple docker compose, and using OSM OAuth2 so the users only need an OSM account to be able to upload pictures.

!!! Tip

    For a production grade deployment, you might need to adapt some things:

    - Tune PostgreSQL configuration to suit your needs, and at the very least backup it 💾.
    - Think about the storage of the pictures, see what disks you'll need, you'll likely need a lot of storage. And as the very least backup them 💾.
    - Maybe split the services between several hosts (pictures workers separate from HTTP API).
    - Add cache in Nginx to speed up some responses.
    - ...

!!! Info

    Some documentation on how to fine tune Panoramax API is available [here](https://gitlab.com/panoramax/server/api/-/blob/develop/docs/install/settings.md).

As a requirement for this example, you'll need a Linux server (this should also work with other OS, but not tested here), with [docker](https://www.docker.com/) and [docker compose](https://docs.docker.com/compose/) installed.

!!! Note
    If you have the legacy `docker-compose` installed, you might need to replace the `docker compose` commands with `docker-compose`. Also note that, depending on you docker installation, you might need `sudo` rights to run docker commands.

Having nice `https` urls is mandatory to use the OAuth2 on OpenStreetMap, you'll also need a domain. You'll need a reverse proxy to handle tls, cf the [Domain section](#domain-configuration).

## Creating our :simple-openstreetmap: OSM OAuth2 client

First, we'll configure our OSM OAuth2 client.

You can follow [the documentation](https://wiki.openstreetmap.org/wiki/OAuth) for this, here is a simple walkthrough.

Go to "My settings" > "OAuth 2 applications"

And register a new client, giving it a nice name, a redirect uri with `https://{your_domain}/api/auth/redirect` (like `https://your.panoramax.org/api/auth/redirect`) and the permission "Read user preferences".
![OSM OAuth2 client configration](osm_oauth_client.png).

Make sure to save the client ID/secret given when registering the client, you'll need both of them in the configuration of the next section.

## Running :simple-docker: :gear: docker compose

This tutorial uses the files in [docker/full-osm-auth/docker-compose.yml](https://gitlab.com/panoramax/server/api/-/blob/develop/docker/full-osm-auth/docker-compose.yml), if it's not already done, you need to clone the git repository and go in the directory.

```bash
git clone https://gitlab.com/panoramax/server/api.git geovisio-api
cd geovisio-api/docker/full-osm-auth/
```

### Configuration

Some key variables can be changed by providing a `.env` file or environment variables to docker compose. Feel free to also adapt the docker-compose.yml file if more changes are needed.

The easiest way is to copy the `env.example` file:

```bash
cp env.example .env
```

And change all the required configuration in the file.

At least you'll need to fill:

- `FLASK_SESSION_COOKIE_DOMAIN`: The domain name you plan to expose the service on (the same you used in the redirect of the OAuth2 client).
- `OAUTH_CLIENT_ID` and `OAUTH_CLIENT_SECRET`: The OSM OAuth2 client ID and secret.
- `FLASK_SECRET_KEY`: A secret key to sign the cookies.
- `PG_PASSWORD`: The password for the main PostgreSQL database account.

Following the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY), you can generate the secret key with:

```bash
python -c 'import secrets; print(secrets.token_hex())'
```

### Build your own blur and detect API (optional)

The blurring is handled as a separate service, by [SgBlur](https://gitlab.com/panoramax/server/sgblur). This API is called by the background workers and needs GPU to be efficient.
    
The OpenStreetMap French chapter offers a [public endpoint](https://blur.panoramax.openstreetmap.fr) so it's for the moment not mandatory to host your own.

However, if you plan to have a big workload or if you want to have your own blurring API and you have at least one Nvidia GPU (We only support Nvidia CUDA right now), you can add the blurring services by [adding](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/) the docker compose file `../docker-compose-blurring.yml`. To do so, add `-f docker-compose.yml -f ../docker-compose-blurring.yml` to each docker compose command below, like:

```bash
docker compose --project-name geovisio-osm -f docker-compose.yml -f ../docker-compose-blurring.yml up -d
```

### Running the :simple-docker: :gear: docker compose

We'll run the docker compose in detached mode, giving it a nice name (it will use our `.env` by default).

```bash
docker compose --project-name geovisio-osm up -d
```

You can check the services state with the command:

```bash
docker compose -p geovisio-osm ps
```

And the logs with

```bash
docker compose -p geovisio-osm logs -f
```

You can check that the API is working by querying on the host:

```bash
curl --fail http://localhost:8080/api
```

!!! Note
    Everything will not be working using http://localhost:8080, as we set some configuration telling the API it will be served on a custom domain.

## :material-dns: Domain configuration

You need to set up your domain and must use https as it is mandatory for OAuth2. There are many ways to do this, maybe the easiest way for this is to use a reverse proxy, and let it handle TLS for you.

You can use [nginx](https://www.nginx.com/) + [letsencrypt](https://letsencrypt.org/fr/) (maybe using [certbot](https://certbot.eff.org/)), [caddy](https://caddyserver.com) or anything you want.

### :simple-caddy: Caddy

Here is a simple Caddy configuration for this:

```caddy
my.domain.org {
    reverse_proxy :8080
}
```

## 🔄 Updating the instance

If at one point you want to update your API version (and you should, we try to add nice functionalities often!), you can run:

```bash
docker compose -p geovisio-osm up --pull=always -d
```

## Accessing the database

If you want to query directly the database, you can do:

```bash
docker compose -p geovisio-osm exec -it db psql postgres://gvs:{your_password}@db/geovisio
```

## Using Panoramax

After all this, you should be able to go to your custom domain 🌐, log in using your osm account 🔎, upload some pictures 📸 and enjoy Panoramax 🎉

If everything does not work as intended, feel free to open an [issue on the gitlab repository](https://gitlab.com/panoramax/server/api/-/issues), contact us in the [Matrix room](https://matrix.to/#/#panoramax-general:matrix.org) or on [community.openstreetmap.org, with the panoramax tag](https://community.openstreetmap.org/tag/panoramax).
