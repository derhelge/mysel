#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER POSTGRES_DJANGO_USER WITH PASSWORD 'POSTGRES_DJANGO_PASSWORD';
	CREATE DATABASE POSTGRES_DJANGO_DB;
	GRANT ALL PRIVILEGES ON DATABASE POSTGRES_DJANGO_DB TO POSTGRES_DJANGO_USER;
	ALTER DATABASE POSTGRES_DJANGO_DB OWNER TO POSTGRES_DJANGO_USER;
	GRANT ALL ON SCHEMA public TO POSTGRES_DJANGO_USER;
	\c POSTGRES_DJANGO_DB;
	CREATE EXTENSION IF NOT EXISTS pgcrypto;
	CREATE USER POSTGRES_DOVECOT_USER WITH PASSWORD 'POSTGRES_DOVECOT_PASSWORD';
	REVOKE ALL ON ALL TABLES IN SCHEMA public FROM POSTGRES_DOVECOT_USER;
EOSQL
