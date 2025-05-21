from hat.drivers.iec61850.common import *  # NOQA

import typing

from hat import json


IedName: typing.TypeAlias = str


DeviceConf: typing.TypeAlias = json.Data
"""Device configuration defined by ``hat-drivers://iec61850/device.yaml``"""
