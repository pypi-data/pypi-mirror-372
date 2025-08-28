# A complete Panoramax deployment with :simple-keycloak: Keycloak authentication


Here is a simple example on how to host a Panoramax instance based on a simple docker compose, and using a custom [keycloak](https://www.keycloak.org/) as OAuth2 Identity Provider.

!!! Tip
    For a production grade deployment, you might need to adapt some things:

    - Tune PostgreSQL configuration to suit your needs, and at the very least backup it 💾.
    - Think about the storage of the pictures, see what disks you'll need, you'll likely need a lot of storage. And as the very least backup them 💾.
    - Maybe split the services between several hosts (pictures workers separate from HTTP API).
    - Add cache in Nginx to speed up some responses.
    - maybe secure a bit more the keycloak, follow [the production documentation](https://www.keycloak.org/server/configuration-production), at least secure more the admin console (cf [the documentation](https://www.keycloak.org/server/reverseproxy))
    - ...

!!! Info
    Some documentation on how to fine tune Panoramax API is available [here](https://gitlab.com/panoramax/server/api/-/blob/develop/docs/install/settings.md).

As a requirement for this example, you'll need a Linux server (this should also work with other OS, but not tested here), with [docker](https://www.docker.com/) and [docker compose](https://docs.docker.com/compose/) installed.

!!! Note 
    If you have the legacy `docker-compose` installed, you might need to replace the `docker compose` commands with `docker-compose`. Also note that, depending on you docker installation, you might need `sudo` rights to run docker commands.

Having nice `https` urls is mandatory, especially for running Keycloak so you'll also need a domain. You'll need a reverse proxy to handle tls, cf the [Domain section](#domain-configuration).

## Running :simple-docker: :gear: docker compose

This tutorial uses the files in [docker/full-keycloak-auth/docker-compose.yml](https://gitlab.com/panoramax/server/api/-/blob/develop/docker/full-keycloak-auth/docker-compose.yml), if it's not already done, you need to clone the git repository and go in the directory.

```bash
git clone https://gitlab.com/panoramax/server/api.git geovisio-api
cd geovisio-api/docker/full-keycloak-auth/
```

### Configuration

Some key variables can be changed by providing a `.env` file or environment variables to docker compose. Feel free to also adapt the docker-compose.yml file if more changes are needed.

The easiest way is to copy the `env.example` file:

```bash
cp env.example .env
```

And change all the required configuration in the file.

At least you'll need to fill:

- `DOMAIN`: The domain used. This needs to be only the domain (like `panoramax.my_domain.org`).
- `OAUTH_CLIENT_SECRET`: The secret key for the oauth client
- `FLASK_SECRET_KEY`: A secret key to sign the cookies
- `KEYCLOAK_ADMIN_PASSWORD`: The admin password to access the admin console (by default at `https://your_domain/oauth`)
- `PG_PASSWORD`: The password for main PostgreSQL database account

Following the [Flask documentation](https://flask.palletsprojects.com/en/3.0.x/config/#SECRET_KEY), you can generate the secret key with:

```bash
python -c 'import secrets; print(secrets.token_hex())'
```

You can use the same method to generate `OAUTH_CLIENT_SECRET`.

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
docker compose --project-name geovisio-auth up -d
```

You can check the services state with the command:

```bash
docker compose -p geovisio-auth ps
```

And the logs with

```bash
docker compose -p geovisio-auth logs -f
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

??? Note
    The API need the [X-Forwarded-*](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Forwarded-For) headers to be set in order to build correct internal links.
    
    You can check that the proxy is setting all the necessary headers by querying the API with:

    ```bash
    curl <your_domain>/api/debug_headers
    ```

    And checking the API logs to see all headers set. The response `test_url` should be the correct URL of the API.

## 🔄 Updating the instance

If at one point you want to update your API version (and you should, we try to add nice functionalities often!), you can run:

```bash
docker compose -p geovisio-auth up --pull=always -d
```

## Accessing the database

If you want to query directly the database, you can do:

```bash
docker compose -p geovisio-auth exec -it db psql postgres://gvs:{your_password}@db/geovisio
```

## :simple-keycloak: Administration of keycloak

You can log in keycloak admin console using the `KEYCLOAK_ADMIN_PASSWORD` credentials on https://your_domain/oauth/.

You can then edit the `geovisio` realm, edit/remove some users 👥, ...

!!! Tip
    On a production grade instance, you'll likely don't want to expose this admin console on the internet, and you can follow the [reverse proxy documentation](https://www.keycloak.org/server/reverseproxy) to hide it.

### 👑 Realm

A default keycloak realm named `geovisio` is defined in the `keycloak-realm.json` file. It only define:

Some basic configuration:

* `User-managed access`: ui to manage the user configuration
* `User registration`: users can freely create accounts
* `Forgot password`: link for users that have forgotten their password
* `Remember me`: cookie to remember the user
* `Edit username`: users can edit their usernames

And a `geovisio` [OpenID Connect](https://fr.wikipedia.org/wiki/OpenID_Connect) client with the `Direct Access Flow` and `Standard Flow` Oauth2 flows.

Feel free to adjust all you need on this realm. You can refer to the [keycloak realm documentation](https://www.keycloak.org/docs/latest/server_admin/#configuring-realms).

### ✨Themes

You can load themes on keycloak for better login/registering experience. You can see what is done for the [IGN instance](https://gitlab.com/panoramax/server/infra/keycloak-buildpack/-/tree/master/themes?ref_type=heads).

The themes will need to be mounted as volumes in the keycloak container and the path defined by `KEYCLOAK_TEMPLATES_DIR`.

## Using Panoramax API

After all this, you should be able to go to your custom domain 🌐, create an account 👤, upload some pictures 📸 and enjoy Panoramax 🎉

If everything does not work as intended, feel free to open an [issue on the gitlab repository](https://gitlab.com/panoramax/server/api/-/issues), contact us in the [Matrix room](https://matrix.to/#/#panoramax-general:matrix.org) or on [community.openstreetmap.org, with the panoramax tag](https://community.openstreetmap.org/tag/panoramax).
