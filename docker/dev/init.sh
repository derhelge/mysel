#!/bin/bash

source .env.dev

# Array of files to exclude/include
files=(
  "keycloak/import/realm-export.json"
  "mailserver/dovecot-sql.conf.ext" 
  "mailserver/dovecot-ldap.conf.ext"
)
# Define replacements as associative arrays with target files
declare -A replacements=(
  ["keycloak/import/realm-export.json"]="DJANGO_OIDC_SECRET LDAP_ADMIN_PASSWORD ROUNDCUBEMAIL_OIDC_SECRET"
  ["mailserver/dovecot-sql.conf.ext"]="POSTGRES_DJANGO_DB POSTGRES_DOVECOT_USER POSTGRES_DOVECOT_PASSWORD"
  ["mailserver/dovecot-ldap.conf.ext"]="LDAP_ADMIN_PASSWORD"
)

# Check if --reverse flag is provided
if [ "$1" == "--reverse" ]; then
  echo "Reverting files to original state..."
  for file in "${files[@]}"; do
    git checkout -- "$file"
    git update-index --no-assume-unchanged "$file"
    echo "Reverted: $file"
  done
else
  if [ ! -f .env.dev ]; then
    cp env.example .env.dev
    echo "Created .env.dev file from env.example template"
  else
    echo ".env file already exists, skipping creation"
  fi
  
  echo "Excluding files from git repo..."
  for file in "${files[@]}"; do
    git update-index --assume-unchanged "$file"
    echo "Excluded: $file" 
  done
  
  echo "Replacing passwords and secrets in various files..."
  
  # Process each file and its replacements
  for file in "${!replacements[@]}"; do
  for var in ${replacements[$file]}; do
      sed -i "s/$var/${!var}/g" "$file"
  done
  done
  
  # openLDAP
  set -e
  ./openldap/generate_bootstrap.sh
fi