from hat.doit.c import (get_py_c_flags,
                        get_py_ld_flags,
                        get_py_ld_libs,
                        CBuild)

from .. import common


__all__ = ['task_pymodules_modbus',
           'task_pymodules_modbus_obj',
           'task_pymodules_modbus_dep',
           'task_pymodules_modbus_cleanup']


modbus_path = (common.src_py_dir / 'hat/drivers/modbus/transport/_encoder'
               ).with_suffix(common.py_ext_suffix)
modbus_src_paths = [common.src_c_dir / 'py/modbus/_encoder.c']
modbus_build_dir = (common.pymodules_build_dir / 'modbus' /
                    f'{common.target_platform.name.lower()}')
modbus_c_flags = [*get_py_c_flags(py_limited_api=common.py_limited_api),
                  '-fPIC',
                  '-O2']
modbus_ld_flags = [*get_py_ld_flags(py_limited_api=common.py_limited_api)]
modbus_ld_libs = [*get_py_ld_libs(py_limited_api=common.py_limited_api)]

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
