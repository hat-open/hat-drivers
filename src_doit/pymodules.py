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
           'task_pymodules_ssl_cleanup',
           'task_pymodules_native_serial',
           'task_pymodules_native_serial_obj',
           'task_pymodules_native_serial_dep',
           'task_pymodules_native_serial_cleanup']


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

native_serial_path = (src_py_dir / 'hat/drivers/serial/_native_serial'
                      ).with_suffix(py_ext_suffix)
native_serial_impl_path = (src_c_dir / 'hat/win32_serial.c'
                           if common.target_platform.value[0] == 'win32'
                           else src_c_dir / 'hat/posix_serial.c')
native_serial_src_paths = [*(src_c_dir / 'py/_native_serial').rglob('*.c'),
                           deps_dir / 'hat-util/src_c/hat/py_allocator.c',
                           native_serial_impl_path]
native_serial_build_dir = (pymodules_build_dir / 'native_serial' /
                           f'{common.target_platform.name.lower()}_'
                           f'{common.target_py_version.name.lower()}')
native_serial_c_flags = [*get_py_c_flags(py_limited_api=py_limited_api),
                         '-fPIC',
                         '-O2',
                         '-pthread',
                         '-D_POSIX_C_SOURCE=200809L',
                         '-DMODULE_NAME="_native_serial"',
                         f"-I{deps_dir / 'hat-util/src_c'}",
                         f"-I{src_c_dir}"]
native_serial_ld_flags = [*get_py_ld_flags(py_limited_api=py_limited_api),
                          '-pthread']
native_serial_ld_libs = [*get_py_ld_libs(py_limited_api=py_limited_api)]

native_serial_build = CBuild(src_paths=native_serial_src_paths,
                             build_dir=native_serial_build_dir,
                             c_flags=native_serial_c_flags,
                             ld_flags=native_serial_ld_flags,
                             ld_libs=native_serial_ld_libs,
                             task_dep=['pymodules_native_serial_cleanup'])


def task_pymodules():
    """Build pymodules"""
    return {'actions': None,
            'task_dep': ['pymodules_ssl',
                         'pymodules_native_serial']}


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


def task_pymodules_native_serial():
    """Build pymodules native_serial"""
    yield from native_serial_build.get_task_lib(native_serial_path)


def task_pymodules_native_serial_obj():
    """Build pymodules native_serial .o files"""
    yield from native_serial_build.get_task_objs()


def task_pymodules_native_serial_dep():
    """Build pymodules native_serial .d files"""
    yield from native_serial_build.get_task_deps()


def task_pymodules_native_serial_cleanup():
    """Cleanup pymodules native_serial"""

    def cleanup():
        for path in native_serial_path.parent.glob('_native_serial.*'):
            if path == native_serial_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}
