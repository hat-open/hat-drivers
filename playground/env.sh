PYTHON=${PYTHON:-python}
RUN_PATH=$(cd $(dirname -- "$0") && pwd)
ROOT_PATH=$RUN_PATH/..
DIST_PATH=$RUN_PATH/dist

export PYTHONPATH=$ROOT_PATH/src_py
