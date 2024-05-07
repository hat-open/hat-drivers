from .modbus import *  # NOQA
from .serial import *  # NOQA
from .ssl import *  # NOQA

from . import modbus
from . import serial
from . import ssl


__all__ = ['task_pymodules',
           *modbus.__all__,
           *serial.__all__,
           *ssl.__all__]


def task_pymodules():
    """Build pymodules"""
    return {'actions': None,
            'task_dep': ['pymodules_ssl',
                         'pymodules_serial',
                         'pymodules_modbus']}
