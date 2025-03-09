#!/bin/sh

set -e

RUN_PATH=$(dirname "$(realpath "$0")")
PLAYGROUND_PATH=$RUN_PATH/..
. $PLAYGROUND_PATH/env.sh

schemas_dir=$ROOT_PATH/schemas_asn1
doc_path=$RUN_PATH/doc.html

exec $PYTHON - $schemas_dir $doc_path <<EOF
from pathlib import Path
import sys

from hat import asn1

schemas_dir = Path(sys.argv[1])
doc_path = Path(sys.argv[2])

repo = asn1.create_repository(schemas_dir)
doc_path.write_text(asn1.generate_html_doc(repo))
EOF
