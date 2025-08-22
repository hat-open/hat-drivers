from hat.doit.common import *  # NOQA

from pathlib import Path

from hat.doit.c import get_py_ext_suffix
from hat.doit.common import PyVersion


build_dir = Path('build')
docs_dir = Path('docs')
peru_dir = Path('peru')
pytest_dir = Path('test_pytest')
schemas_asn1_dir = Path('schemas_asn1')
schemas_json_dir = Path('schemas_json')
schemas_sbs_dir = Path('schemas_sbs')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

pymodules_build_dir = build_dir / 'pymodules'

py_limited_api = next(iter(PyVersion))
py_ext_suffix = get_py_ext_suffix(py_limited_api=py_limited_api)
