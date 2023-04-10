from .pymodules import *  # NOQA

from pathlib import Path
import sys

from hat import asn1
from hat import json
from hat.doit import common
from hat.doit.c import get_task_clang_format
from hat.doit.docs import (build_sphinx,
                           build_pdoc)
from hat.doit.py import (build_wheel,
                         run_pytest,
                         run_flake8,
                         get_py_versions)

from . import pymodules


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_asn1',
           'task_peru',
           'task_format',
           *pymodules.__all__]


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')
schemas_asn1_dir = Path('schemas_asn1')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [
            build_dir,
            *src_py_dir.rglob('asn1_repo.json'),
            *(src_py_dir / 'hat/drivers/ssl').glob('_ssl.*'),
            *(src_py_dir / 'hat/drivers/serial').glob('_native_serial.*')])]}


def task_build():
    """Build"""

    def build():
        build_wheel(
            src_dir=src_py_dir,
            dst_dir=build_py_dir,
            name='hat-drivers',
            description='Hat communication drivers',
            url='https://github.com/hat-open/hat-drivers',
            license=common.License.APACHE2,
            py_versions=get_py_versions(pymodules.py_limited_api),
            py_limited_api=pymodules.py_limited_api,
            platform=common.target_platform,
            has_ext_modules=True)

    return {'actions': [build],
            'task_dep': ['asn1',
                         'pymodules']}


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir])]}


def task_test():
    """Test"""
    return {'actions': [lambda args: run_pytest(pytest_dir, *(args or []))],
            'pos_arg': 'args',
            'task_dep': ['asn1',
                         'pymodules']}


def task_docs():
    """Docs"""

    def build():
        build_sphinx(src_dir=docs_dir,
                     dst_dir=build_docs_dir,
                     project='hat-drivers')
        build_pdoc(module='hat.drivers',
                   dst_dir=build_docs_dir / 'py_api')

    return {'actions': [build],
            'task_dep': ['asn1',
                         'pymodules']}


def task_asn1():
    """Generate ASN.1 repository"""
    yield _get_subtask_asn1(
        src_paths=[schemas_asn1_dir / 'acse.asn'],
        dst_path=src_py_dir / 'hat/drivers/acse/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=[schemas_asn1_dir / 'copp.asn'],
        dst_path=src_py_dir / 'hat/drivers/copp/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=[schemas_asn1_dir / 'mms.asn'],
        dst_path=src_py_dir / 'hat/drivers/mms/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=list((schemas_asn1_dir / 'snmp').rglob('*.asn')),
        dst_path=src_py_dir / 'hat/drivers/snmp/encoder/asn1_repo.json')


def task_peru():
    """Peru"""
    return {'actions': [f'{sys.executable} -m peru sync']}


def task_format():
    """Format"""
    yield from get_task_clang_format([*Path('src_c').rglob('*.c'),
                                      *Path('src_c').rglob('*.h')])


def _get_subtask_asn1(src_paths, dst_path):

    def generate():
        repo = asn1.Repository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, dst_path, indent=None)

    return {'name': str(dst_path),
            'actions': [generate],
            'file_dep': src_paths,
            'targets': [dst_path]}
