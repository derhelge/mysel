#!/bin/bash

if [ ! -f .env.dev ]; then
  cp env.example .env.dev
  echo "Created .env.dev file from env.example template"
else
  echo ".env file already exists, skipping creation"
fi

# openLDAP
set -e
./openldap/generate_bootstrap.sh
