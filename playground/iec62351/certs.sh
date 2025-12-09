#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
PLAYGROUND_PATH=$RUN_PATH/..
. $PLAYGROUND_PATH/env.sh

CERTS_PATH=$RUN_PATH/certs

rm -rf $CERTS_PATH
mkdir -p $CERTS_PATH

duration=3650
key_type=rsa:2048

openssl req -batch -x509 -noenc \
        -newkey $key_type \
        -days $duration \
        -keyout $CERTS_PATH/ca.key \
        -out $CERTS_PATH/ca.cert

openssl req -batch -x509 -noenc \
        -newkey $key_type \
        -days $duration \
        -CA $CERTS_PATH/ca.cert \
        -CAkey $CERTS_PATH/ca.key \
        -keyout $CERTS_PATH/server.key \
        -out $CERTS_PATH/server.cert

openssl req -batch -x509 -noenc \
        -newkey $key_type \
        -days $duration \
        -CA $CERTS_PATH/ca.cert \
        -CAkey $CERTS_PATH/ca.key \
        -keyout $CERTS_PATH/client.key \
        -out $CERTS_PATH/client.cert


