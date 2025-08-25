from hat.drivers.iec61850.common import *  # NOQA

import importlib.resources
import typing

from hat import json


with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'json_schema_repo.json') as _path:
    json_schema_repo: json.SchemaRepository = json.merge_schema_repositories(
        json.json_schema_repo,
        json.decode_file(_path))
    """JSON schema repository"""


IedName: typing.TypeAlias = str


DeviceConf: typing.TypeAlias = json.Data
"""Device configuration defined by ``hat-drivers://iec61850/device.yaml``"""
