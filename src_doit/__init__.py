from .pymodules import *  # NOQA

from pathlib import Path
import sys

from hat import asn1
from hat import json
from hat import sbs
from hat.doit.c import get_task_clang_format
from hat.doit.docs import (build_sphinx,
                           build_pdoc)
from hat.doit.py import (get_task_build_wheel,
                         get_task_run_pytest,
                         get_task_create_pip_requirements,
                         run_flake8,
                         get_py_versions)

from . import common
from . import pymodules


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_asn1',
           'task_sbs',
           'task_peru',
           'task_format',
           'task_pip_requirements',
           *pymodules.__all__]


build_py_dir = common.build_dir / 'py'
build_docs_dir = common.build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [
        common.build_dir,
        *common.src_py_dir.rglob('asn1_repo.json'),
        *common.src_py_dir.rglob('sbs_repo.json'),
        *(common.src_py_dir / 'hat/drivers/ssl').glob('_ssl.*'),
        *(common.src_py_dir / 'hat/drivers/serial').glob('_native_serial.*'),
        *(common.src_py_dir /
          'hat/drivers/modbus/transport').glob('_encoder.*')])]}


def task_build():
    """Build"""
    return get_task_build_wheel(
        src_dir=common.src_py_dir,
        build_dir=build_py_dir,
        py_versions=get_py_versions(common.py_limited_api),
        py_limited_api=common.py_limited_api,
        platform=common.target_platform,
        is_purelib=False,
        task_dep=['asn1',
                  'sbs',
                  'pymodules'])


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [common.src_py_dir]),
                        (run_flake8, [common.pytest_dir])]}


def task_test():
    """Test"""
    return get_task_run_pytest(task_dep=['asn1',
                                         'sbs',
                                         'pymodules'])


def task_docs():
    """Docs"""

    def build():
        build_sphinx(src_dir=common.docs_dir,
                     dst_dir=build_docs_dir,
                     project='hat-drivers')
        build_pdoc(module='hat.drivers',
                   dst_dir=build_docs_dir / 'py_api')

    return {'actions': [build],
            'task_dep': ['asn1',
                         'sbs',
                         'pymodules']}


def task_asn1():
    """Generate ASN.1 repository"""
    yield _get_subtask_asn1(
        src_paths=[common.schemas_asn1_dir / 'acse.asn'],
        dst_path=common.src_py_dir / 'hat/drivers/acse/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=[common.schemas_asn1_dir / 'copp.asn'],
        dst_path=common.src_py_dir / 'hat/drivers/copp/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=[common.schemas_asn1_dir / 'mms.asn'],
        dst_path=common.src_py_dir / 'hat/drivers/mms/asn1_repo.json')

    yield _get_subtask_asn1(
        src_paths=list((common.schemas_asn1_dir / 'snmp').rglob('*.asn')),
        dst_path=common.src_py_dir / 'hat/drivers/snmp/encoder/asn1_repo.json')


def task_sbs():
    """Generate SBS repository"""
    yield _get_subtask_sbs(
        src_paths=[common.schemas_sbs_dir / 'chatter.sbs'],
        dst_path=common.src_py_dir / 'hat/drivers/chatter/sbs_repo.json')


def task_peru():
    """Peru"""
    return {'actions': [f'{sys.executable} -m peru sync']}


def task_format():
    """Format"""
    yield from get_task_clang_format([*Path('src_c').rglob('*.c'),
                                      *Path('src_c').rglob('*.h')])


def task_pip_requirements():
    """Create pip requirements"""
    return get_task_create_pip_requirements()


def _get_subtask_asn1(src_paths, dst_path):

    def generate():
        repo = asn1.create_repository(*src_paths)
        data = asn1.repository_to_json(repo)
        json.encode_file(data, dst_path, indent=None)

    return {'name': str(dst_path),
            'actions': [generate],
            'file_dep': src_paths,
            'targets': [dst_path]}


def _get_subtask_sbs(src_paths, dst_path):

    def generate():
        repo = sbs.Repository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, dst_path, indent=None)

    return {'name': str(dst_path),
            'actions': [generate],
            'file_dep': src_paths,
            'targets': [dst_path]}
