#!/bin/bash
set -e

# create a custom schema for keycloak

psql -v ON_ERROR_STOP=1  --dbname $POSTGRES_DB <<-EOSQL
    CREATE USER keycloak_user WITH PASSWORD 'keycloak_password';
    CREATE SCHEMA IF NOT EXISTS keycloak AUTHORIZATION keycloak_user;
EOSQL

