#!/bin/sh

cd $(dirname -- "$0")

mkdir -p ./data

exec chromium --remote-debugging-port=22222 \
              --user-data-dir=data \
              --headless \
              --disable-gpu \
              "$@"
