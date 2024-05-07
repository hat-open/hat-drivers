from hat.doit.c import (get_py_c_flags,
                        get_py_ld_flags,
                        get_py_ld_libs,
                        CBuild)

from .. import common


__all__ = ['task_pymodules_serial',
           'task_pymodules_serial_obj',
           'task_pymodules_serial_dep',
           'task_pymodules_serial_cleanup']


is_target_posix = common.target_platform.value[0] in ('linux', 'darwin')
is_target_linux = common.target_platform.value[0] == 'linux'
is_target_win32 = common.target_platform.value[0] == 'win32'


serial_path = (common.src_py_dir / 'hat/drivers/serial/_native_serial'
               ).with_suffix(common.py_ext_suffix)
serial_posix_src_paths = [common.src_c_dir / 'hat/serial_posix.c']
serial_win32_src_paths = [common.src_c_dir / 'hat/serial_win32.c']
serial_src_paths = [common.src_c_dir / 'py/serial/_native_serial.c',
                    common.peru_dir / 'hat-util/src_c/hat/py_allocator.c',
                    common.peru_dir / 'hat-util/src_c/hat/ring.c',
                    common.src_c_dir / 'hat/serial.c',
                    *(serial_posix_src_paths if is_target_posix else []),
                    *(serial_win32_src_paths if is_target_win32 else [])]
serial_build_dir = (common.pymodules_build_dir / 'serial' /
                    f'{common.target_platform.name.lower()}')
serial_posix_c_flags = ['-pthread',
                        '-D_POSIX_C_SOURCE=200809L']
serial_linux_c_flags = ['-D_DEFAULT_SOURCE']
serial_win32_c_flags = []
serial_c_flags = [*get_py_c_flags(py_limited_api=common.py_limited_api),
                  '-fPIC',
                  '-O2',
                  '-std=c11',
                  f"-I{common.peru_dir / 'hat-util/src_c'}",
                  f"-I{common.src_c_dir}",
                  *(serial_posix_c_flags if is_target_posix else []),
                  *(serial_linux_c_flags if is_target_linux else []),
                  *(serial_win32_c_flags if is_target_win32 else [])]
serial_posix_ld_flags = ['-pthread']
serial_win32_ld_flags = []
serial_ld_flags = [*get_py_ld_flags(py_limited_api=common.py_limited_api),
                   *(serial_posix_ld_flags if is_target_posix else []),
                   *(serial_win32_ld_flags if is_target_win32 else [])]
serial_ld_libs = [*get_py_ld_libs(py_limited_api=common.py_limited_api)]

serial_build = CBuild(src_paths=serial_src_paths,
                      build_dir=serial_build_dir,
                      c_flags=serial_c_flags,
                      ld_flags=serial_ld_flags,
                      ld_libs=serial_ld_libs,
                      task_dep=['pymodules_serial_cleanup',
                                'peru'])


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
