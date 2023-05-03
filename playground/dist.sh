#!/bin/sh

set -e

. $(dirname -- "$0")/env.sh

TARGET_PLATFORMS="linux_gnu_x86_64
                  linux_gnu_aarch64
                  windows_amd64"

cd $ROOT_PATH
rm -rf $DIST_PATH
mkdir -p $DIST_PATH

for TARGET_PLATFORM in $TARGET_PLATFORMS; do
    export TARGET_PLATFORM
    $PYTHON -m doit clean_all
    $PYTHON -m doit
    cp $ROOT_PATH/build/py/dist/*.whl $DIST_PATH
done

IMAGES="linux/amd64/build-hat-drivers:alpine3.17-cpy3.11
        linux/arm/v7/build-hat-drivers:debian11-cpy3.10"

for IMAGE in $IMAGES; do
    $PYTHON -m doit clean_all
    PLATFORM=$(dirname $IMAGE)
    IMAGE_ID=$(podman images -q $IMAGE)
    podman build --platform $PLATFORM \
                 -f $RUN_PATH/dockerfiles/$IMAGE \
                 -t $IMAGE \
                 .
    if [ -n "$IMAGE_ID" -a "$IMAGE_ID" != "$(podman images -q $IMAGE)" ]; then
        podman rmi $IMAGE_ID
    fi
    podman run --rm \
               --platform $PLATFORM \
               -v $DIST_PATH:/hat/dist \
               -v ~/.cache/pip:/root/.cache/pip \
               -i $IMAGE /bin/sh - << EOF
set -e
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.pip.dev.txt
doit clean_all
doit
cp build/py/dist/*.whl dist
EOF
done

$PYTHON -m doit clean_all
