# Available commands

Various operations can be run on Panoramax API using its _command line tool_: migrate or clean-up database, authentication token handling, sequence management...

## Database migration

As Panoramax is actively developed, when updating from a previous version, some database migration could be necessary. If so, when starting Panoramax, an error message will show up and warn about necessary migration. The following command has to be ran:

=== ":simple-python: Python package"

	```bash
	flask db upgrade
	```

=== ":simple-docker: Docker"

	```bash
	docker run --rm panoramax/api db-upgrade
	```

=== ":simple-docker: :gear: Docker Compose"

	✨ Database migrations should be handled automatically in the different docker compose by the `migrations` service

### Rollback

There might be no reason to do so, but if necessary, a migration rollback can also be done:

=== ":simple-python: Python package"

	```bash
	flask db rollback
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask db rollback'
	```

=== ":simple-docker: :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash migrations -c 'python3 -m flask db rollback' 
	```

!!! note

	A full database rollback (ie. removing all structures and data created by Panoramax API) can also be done by adding `--all` to the `rollback` command.


## Force pictures heading in sequence

Since version 1.4.0, you can import pictures without heading metadata. By default, heading is computed based on sequence movement path (looking in front), but you can edit manually after import using this command:

=== ":simple-python: Python package"

	```bash
	flask set-sequences-heading \
	--value <DEGREES_ROTATION_FROM_FORWARD> \
	--overwrite \
	<SEQUENCE_ID_1> <SEQUENCE_ID_2> ...
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask set-sequences-heading --value <DEGREES_ROTATION_FROM_FORWARD> --overwrite <SEQUENCE_ID_1> <SEQUENCE_ID_2> ...'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask set-sequences-heading --value <DEGREES_ROTATION_FROM_FORWARD> --overwrite <SEQUENCE_ID_1> <SEQUENCE_ID_2> ...'
	```


## Cached data

Some data is cached (using materialized views) in database for a better performance.

If you use [background workers](./deep_dive/pictures_processing.md) (and you **should** on a production-grade instance), they will do this regularly (based on the `PICTURE_PROCESS_REFRESH_CRON` parameter). Else you have to run from time to time the `flask db refresh` command to keep these views up-to-date. This can be run regularly using [cron](https://en.wikipedia.org/wiki/Cron) for example.

## Clean-up

Eventually, if you want to clear database and delete derivate versions of pictures files (it **doesn't** delete original pictures), you can use the `cleanup` command:

=== ":simple-python: Python package"

	```bash
	flask cleanup
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask cleanup'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask cleanup'
	```

You can cleanup only certain sequences:

=== ":simple-python: Python package"

	```bash
	flask cleanup <SEQUENCE_ID_1> <SEQUENCE_ID_2> ...
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask cleanup <SEQUENCE_ID_1> <SEQUENCE_ID_2> ...'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask cleanup <SEQUENCE_ID_1> <SEQUENCE_ID_2> ...'
	```

You can also run some partial cleaning with the same cleanup command and one of the following options:

=== ":simple-python: Python package"

	<div class="annotate" markdown>

	```
	flask cleanup --database (1) --cache (2) --permanent-pictures (3)
	```

	</div>

	1. Removes entries from database
	2. Removes picture derivates (tiles, SD and thumbnail)
	3. Removes permanent (original) pictures

	
=== ":simple-docker: Docker"

	<div class="annotate" markdown>

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask cleanup --database (1) --cache (2) --permanent-pictures (3)'
	```

	</div>

	1. Removes entries from database
	2. Removes picture derivates (tiles, SD and thumbnail)
	3. Removes permanent (original) pictures

=== ":simple-docker:  :gear: Docker Compose"

	<div class="annotate" markdown>

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask cleanup --database (1) --cache (2) --permanent-pictures (3)'
	```

	</div>

	1. Removes entries from database
	2. Removes picture derivates (tiles, SD and thumbnail)
	3. Removes permanent (original) pictures

## Sequences reorder

You can sort all sequences by pictures capture time with the following command:

=== ":simple-python: Python package"

	```bash
	flask sequences reorder
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask sequences reorder'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask sequences reorder'
	```


If you want to reorder some specific sequences, you need their ID (the UUID):

=== ":simple-python: Python package"

	```bash
	flask sequences reorder <SEQUENCE_ID_1> <SEQUENCE_ID_2>
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask sequences reorder <SEQUENCE_ID_1> <SEQUENCE_ID_2>'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask sequences reorder <SEQUENCE_ID_1> <SEQUENCE_ID_2>'
	```

## JWT token for the instance administrator

An instance administrator can get the :simple-jsonwebtokens: JWT token of the default instance's account with the flask command `default-account-tokens get`.

=== ":simple-python: Python package"

	```bash
    flask default-account-tokens get
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask default-account-tokens get'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask default-account-tokens get'
	```

This token can then be used to authenticate api calls as bearer token. This is especially useful when running an instance without an OAuth provider.

:octicons-arrow-right-24: Check the [API authentication section](../api/api.md#authentication) to know more what you can do with this token.

!!! warning
    The instance need to be configured with a valid `FLASK_SECRET_KEY` for this to work (cf [instance configuration](../install/settings.md#flask-parameters)). __Be sure not to share this token!__

## Users management

The accounts can be managed by the `user` cli subcommand.

The user can be identified by its name or its ID.

The different flags can be combined (you can create an account with a role, for example).

### Create a user

You can create a user with the following command:

!!! Warning

    For this command, a name must be provided, not the ID.

=== ":simple-python: Python package"

	```bash
	flask user <ACCOUNT_NAME> --create
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask user <ACCOUNT_NAME> --create'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask user <ACCOUNT_NAME> --create'
	```

### Set the role of an account

You can set the role of an account with the following command:

=== ":simple-python: Python package"

	```bash
	flask user <ACCOUNT_ID_OR_NAME> --set-role <ROLE>
	```
	
=== ":simple-docker: Docker"

	```bash
	docker run --rm --entrypoint bash panoramax/api -c 'python3 -m flask user <ACCOUNT_ID_OR_NAME> --set-role <ROLE>'
	```

=== ":simple-docker:  :gear: Docker Compose"

	```bash
	docker compose run --rm --entrypoint bash api -c 'python3 -m flask user <ACCOUNT_ID_OR_NAME> --set-role <ROLE>'
	```

The role can be either `admin` or `user`.
