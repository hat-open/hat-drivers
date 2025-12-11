#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
PLAYGROUND_PATH=$RUN_PATH/..
. $PLAYGROUND_PATH/env.sh

CERTS_PATH=$RUN_PATH/certs

export PYTHONASYNCIODEBUG=1

exec python $RUN_PATH/main.py \
    --cert $CERTS_PATH/server.cert \
    --key $CERTS_PATH/server.key \
    --ca $CERTS_PATH/ca.cert \
    "$@" \
    server
