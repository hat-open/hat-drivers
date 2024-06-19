#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")/..
. $PLAYGROUND_PATH/env.sh

$PYTHON $PLAYGROUND_PATH/icmp/ping.py "$@"
