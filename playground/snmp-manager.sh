#!/bin/sh

set -e

. $(dirname -- "$0")/env.sh

$PYTHON -m hat.drivers.snmp.manager "$@"
