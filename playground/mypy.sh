#!/bin/sh

set -e

PLAYGROUND_PATH=$(dirname "$(realpath "$0")")
. $PLAYGROUND_PATH/env.sh

export MYPYPATH=$PYTHONPATH

exec $PYTHON -m mypy "$@"
