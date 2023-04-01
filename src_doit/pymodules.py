from pathlib import Path

from hat.doit import common
from hat.doit.c import (get_py_ext_suffix,
                        get_py_c_flags,
                        get_py_ld_flags,
                        get_py_ld_libs,
                        CBuild)


__all__ = ['task_pymodules',
           'task_pymodules_ssl',
           'task_pymodules_ssl_obj',
           'task_pymodules_ssl_dep',
           'task_pymodules_ssl_cleanup']


py_limited_api = next(iter(common.PyVersion))
py_ext_suffix = get_py_ext_suffix(py_limited_api=py_limited_api)

build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

pymodules_build_dir = build_dir / 'pymodules'

ssl_path = (src_py_dir / 'hat/drivers/ssl/_ssl').with_suffix(py_ext_suffix)
ssl_src_paths = [*(src_c_dir / 'py/_ssl').rglob('*.c')]
ssl_build_dir = (pymodules_build_dir / 'ssl' /
                 f'{common.target_platform.name.lower()}_'
                 f'{common.target_py_version.name.lower()}')
ssl_c_flags = [*get_py_c_flags(py_limited_api=py_limited_api),
               '-fPIC',
               '-O2']
ssl_ld_flags = [*get_py_ld_flags(py_limited_api=py_limited_api)]
ssl_ld_libs = [*get_py_ld_libs(py_limited_api=py_limited_api),
               '-lssl']

ssl_build = CBuild(src_paths=ssl_src_paths,
                   build_dir=ssl_build_dir,
                   c_flags=ssl_c_flags,
                   ld_flags=ssl_ld_flags,
                   ld_libs=ssl_ld_libs,
                   task_dep=['pymodules_ssl_cleanup'])


def task_pymodules():
    """Build pymodules"""
    return {'actions': None,
            'task_dep': ['pymodules_ssl']}


def task_pymodules_ssl():
    """Build pymodules ssl"""
    yield from ssl_build.get_task_lib(ssl_path)


def task_pymodules_ssl_obj():
    """Build pymodules ssl .o files"""
    yield from ssl_build.get_task_objs()


def task_pymodules_ssl_dep():
    """Build pymodules ssl .d files"""
    yield from ssl_build.get_task_deps()


def task_pymodules_ssl_cleanup():
    """Cleanup pymodules ssl"""

    def cleanup():
        for path in ssl_path.parent.glob('_ssl.*'):
            if path == ssl_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}
