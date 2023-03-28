#!/bin/sh

RUN_PATH=$(dirname -- "$0")

export PYTHONPATH="$RUN_PATH/../../src_py"

exec python "$RUN_PATH/client.py" "$@"
