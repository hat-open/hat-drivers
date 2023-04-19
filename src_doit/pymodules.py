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
           'task_pymodules_serial',
           'task_pymodules_serial_obj',
           'task_pymodules_serial_dep',
           'task_pymodules_serial_cleanup',
           'task_pymodules_modbus',
           'task_pymodules_modbus_obj',
           'task_pymodules_modbus_dep',
           'task_pymodules_modbus_cleanup']


py_limited_api = next(iter(common.PyVersion))
py_ext_suffix = get_py_ext_suffix(py_limited_api=py_limited_api)

build_dir = Path('build')
peru_dir = Path('peru')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

pymodules_build_dir = build_dir / 'pymodules'

is_target_posix = common.target_platform.value[0] in ('linux', 'darwin')
is_target_linux = common.target_platform.value[0] == 'linux'
is_target_win32 = common.target_platform.value[0] == 'win32'


ssl_path = (src_py_dir / 'hat/drivers/ssl/_ssl').with_suffix(py_ext_suffix)
ssl_src_paths = [src_c_dir / 'py/ssl/_ssl.c']
ssl_build_dir = (pymodules_build_dir / 'ssl' /
                 f'{common.target_platform.name.lower()}')
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


serial_path = (src_py_dir /
               'hat/drivers/serial/_native_serial').with_suffix(py_ext_suffix)
serial_posix_src_paths = [src_c_dir / 'hat/serial_posix.c']
serial_win32_src_paths = [src_c_dir / 'hat/serial_win32.c']
serial_src_paths = [src_c_dir / 'py/serial/_native_serial.c',
                    peru_dir / 'hat-util/src_c/hat/py_allocator.c',
                    peru_dir / 'hat-util/src_c/hat/ring.c',
                    src_c_dir / 'hat/serial.c',
                    *(serial_posix_src_paths if is_target_posix else []),
                    *(serial_win32_src_paths if is_target_win32 else [])]
serial_build_dir = (pymodules_build_dir / 'serial' /
                    f'{common.target_platform.name.lower()}')
serial_posix_c_flags = ['-pthread',
                        '-D_POSIX_C_SOURCE=200809L']
serial_linux_c_flags = ['-D_DEFAULT_SOURCE']
serial_win32_c_flags = []
serial_c_flags = [*get_py_c_flags(py_limited_api=py_limited_api),
                  '-fPIC',
                  '-O2',
                  '-std=c11',
                  f"-I{peru_dir / 'hat-util/src_c'}",
                  f"-I{src_c_dir}",
                  *(serial_posix_c_flags if is_target_posix else []),
                  *(serial_linux_c_flags if is_target_linux else []),
                  *(serial_win32_c_flags if is_target_win32 else [])]
serial_posix_ld_flags = ['-pthread']
serial_win32_ld_flags = []
serial_ld_flags = [*get_py_ld_flags(py_limited_api=py_limited_api),
                   *(serial_posix_ld_flags if is_target_posix else []),
                   *(serial_win32_ld_flags if is_target_win32 else [])]
serial_ld_libs = [*get_py_ld_libs(py_limited_api=py_limited_api)]

serial_build = CBuild(src_paths=serial_src_paths,
                      build_dir=serial_build_dir,
                      c_flags=serial_c_flags,
                      ld_flags=serial_ld_flags,
                      ld_libs=serial_ld_libs,
                      task_dep=['pymodules_serial_cleanup',
                                'peru'])


modbus_path = (src_py_dir / 'hat/drivers/modbus/transport/_encoder'
               ).with_suffix(py_ext_suffix)
modbus_src_paths = [src_c_dir / 'py/modbus/_encoder.c']
modbus_build_dir = (pymodules_build_dir / 'modbus' /
                    f'{common.target_platform.name.lower()}')
modbus_c_flags = [*get_py_c_flags(py_limited_api=py_limited_api),
                  '-fPIC',
                  '-O2']
modbus_ld_flags = [*get_py_ld_flags(py_limited_api=py_limited_api)]
modbus_ld_libs = [*get_py_ld_libs(py_limited_api=py_limited_api)]

modbus_build = CBuild(src_paths=modbus_src_paths,
                      build_dir=modbus_build_dir,
                      c_flags=modbus_c_flags,
                      ld_flags=modbus_ld_flags,
                      ld_libs=modbus_ld_libs,
                      task_dep=['pymodules_modbus_cleanup'])


def task_pymodules():
    """Build pymodules"""
    return {'actions': None,
            'task_dep': ['pymodules_ssl',
                         'pymodules_serial',
                         'pymodules_modbus']}


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


def task_pymodules_serial():
    """Build pymodules serial"""
    yield from serial_build.get_task_lib(serial_path)


def task_pymodules_serial_obj():
    """Build pymodules serial .o files"""
    yield from serial_build.get_task_objs()


def task_pymodules_serial_dep():
    """Build pymodules serial .d files"""
    yield from serial_build.get_task_deps()


def task_pymodules_serial_cleanup():
    """Cleanup pymodules serial"""

    def cleanup():
        for path in serial_path.parent.glob('_native_serial.*'):
            if path == serial_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}


def task_pymodules_modbus():
    """Build pymodules modbus"""
    yield from modbus_build.get_task_lib(modbus_path)


def task_pymodules_modbus_obj():
    """Build pymodules modbus .o files"""
    yield from modbus_build.get_task_objs()


def task_pymodules_modbus_dep():
    """Build pymodules modbus .d files"""
    yield from modbus_build.get_task_deps()


def task_pymodules_modbus_cleanup():
    """Cleanup pymodules modbus"""

    def cleanup():
        for path in modbus_path.parent.glob('_encoder.*'):
            if path == modbus_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}
