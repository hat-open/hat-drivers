from pathlib import Path
import subprocess
import sys

from hat import asn1
from hat import json
from hat.doit import common


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_asn1']


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')
schemas_asn1_dir = Path('schemas_asn1')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [build_dir,
                                        *src_py_dir.rglob('asn1_repo.json')])]}


def task_build():
    """Build"""

    def build():
        common.wheel_build(
            src_dir=src_py_dir,
            dst_dir=build_py_dir,
            src_paths=list(common.path_rglob(src_py_dir,
                                             blacklist={'__pycache__'})),
            name='hat-drivers',
            description='Hat communication drivers',
            url='https://github.com/hat-open/hat-drivers',
            license=common.License.APACHE2,
            packages=['hat'])

    return {'actions': [build],
            'task_dep': ['asn1']}


def task_check():
    """Check with flake8"""
    return {'actions': [(_run_flake8, [src_py_dir]),
                        (_run_flake8, [pytest_dir])]}


def task_test():
    """Test"""

    def run(args):
        subprocess.run([sys.executable, '-m', 'pytest',
                        '-s', '-p', 'no:cacheprovider',
                        *(args or [])],
                       cwd=str(pytest_dir),
                       check=True)

    return {'actions': [run],
            'pos_arg': 'args',
            'task_dep': ['asn1']}


def task_docs():
    """Docs"""

    def build():
        common.sphinx_build(common.SphinxOutputType.HTML, docs_dir,
                            build_docs_dir)
        subprocess.run([sys.executable, '-m', 'pdoc',
                        '--html', '--skip-errors', '-f',
                        '-o', str(build_docs_dir / 'py_api'),
                        'hat.drivers'],
                       stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL,
                       check=True)

    return {'actions': [build],
            'task_dep': ['asn1']}


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


def _run_flake8(path):
    subprocess.run([sys.executable, '-m', 'flake8', str(path)],
                   check=True)


def _get_subtask_asn1(src_paths, dst_path):

    def generate():
        repo = asn1.Repository(*src_paths)
        data = repo.to_json()
        json.encode_file(data, dst_path, indent=None)

    return {'name': str(dst_path),
            'actions': [generate],
            'file_dep': src_paths,
            'targets': [dst_path]}
