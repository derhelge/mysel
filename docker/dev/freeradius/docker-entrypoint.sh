#!/bin/sh
set -e

PATH=/opt/sbin:/opt/bin:$PATH
export PATH

if [ "$#" -eq 0 ] || [ "${1#-}" != "$1" ]; then
    # cd /etc/raddb/certs
    # make destroycerts
    # make
    chown -R freerad:freerad /etc/raddb/certs
    cd /
    set -- freeradius "$@"
fi

exec "$@"