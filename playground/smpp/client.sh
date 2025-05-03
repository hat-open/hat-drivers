#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")/..
. $PLAYGROUND_PATH/env.sh

exec $PYTHON $PLAYGROUND_PATH/smpp/client.py "$@"
