# :simple-postgresql:{ .lg .middle } Database setup

Panoramax API relies on a [PostgreSQL](https://www.postgresql.org/) 12+ database with [PostGIS](https://postgis.net/) 3.4+ extension to run.

!!! note
    The recommended PostgreSQL version is 15+, since this way, granular permissions can be granted to the user.

You can use your own existing PostgreSQL server, a cloud-managed PostgreSQL database, or have PostgreSQL running in our Docker files. If you want to install your own PostgreSQL server, refer to these software documentation to know more about their install.

!!! important
    For production-grade deployment, be sure that your database is backuped, it would be a shame to loose all your data :boom:!

Once your PostgreSQL server is ready and running, we recommend you to do the following:

- Add a system/OS user named `geovisio`, for example under Linux:

```bash
$ sudo useradd geovisio
```

- Create a PostgreSQL role `geovisio` with this command:

```bash
$ sudo su - postgres -c "psql -c \"CREATE ROLE geovisio LOGIN PASSWORD 'mypassword'\""
```

- Create a new database (with **UTF-8 encoding**) using this command:

```bash
$ sudo su - postgres -c "psql -c \"CREATE DATABASE geovisio ENCODING 'UTF-8' TEMPLATE template0 OWNER geovisio\""
```

- Enable PostGIS extension in your database:

```bash
$ sudo su - postgres -c "psql -d geovisio -c \"CREATE EXTENSION postgis\""
```

- Make sure your database is running at UTC timezone:

```bash
$ sudo su - postgres -c "psql -d geovisio -c \"ALTER DATABASE geovisio SET TIMEZONE TO 'UTC'\""
```

- If postgres 15+ is used, grant [`session_replication_role`](https://www.postgresql.org/docs/current/runtime-config-client.html), so that sql migrations can be non blocking.

```bash
$ sudo su - postgres -c "psql -d geovisio -c \"GRANT SET ON PARAMETER session_replication_role TO geovisio\""
```

else, the user must have superuser privilege (but it's way better to only grant `session_replication_role`):

```bash
$ sudo su - postgres -c "psql -d geovisio -c \"ALTER USER geovisio WITH SUPERUSER\""
```

## Troubleshooting

Got some issues on this part ? Here are a few hints that may help.

- PostgreSQL server is not listening ?
  - Check the [postgresql.conf](https://www.postgresql.org/docs/current/config-setting.html#CONFIG-SETTING-CONFIGURATION-FILE) file and verify that `listen_adresses` is set to `*`
- PostgreSQL says `Peer authentication failed` ?
  - Check your [pg_hba.conf](https://www.postgresql.org/docs/current/auth-pg-hba-conf.html) file and verify that a rule exist to allow your `geovisio` user or any other OS user to login into your database
  - This is particularly useful if you're running only Panoramax API in Docker, with a PostgreSQL database server on your host, where database IP address might look like `172.17.0.*`. You may have to add an entry like this to allow login:

```
host	geovisio	geovisio	172.17.0.0/24	trust
```
