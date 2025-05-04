#!/bin/bash
set -e

# Ersetze Platzhalter in SQL Config
envsubst < /etc/dovecot/dovecot-sql.conf.ext.template > /etc/dovecot/dovecot-sql.conf.ext

# Ersetze Platzhalter in LDAP Config
envsubst < /etc/dovecot/dovecot-ldap.conf.ext.template > /etc/dovecot/dovecot-ldap.conf.ext

# Setze korrekte Berechtigungen
chmod 640 /etc/dovecot/dovecot-sql.conf.ext
chmod 640 /etc/dovecot/dovecot-ldap.conf.ext

# Führe original docker-entrypoint aus (falls vorhanden)
exec "$@"
