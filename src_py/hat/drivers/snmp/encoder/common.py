from hat.drivers.snmp.common import *  # NOQA

import importlib.resources

from hat import asn1
from hat import json


with importlib.resources.open_text(__package__, 'asn1_repo.json') as _f:
    encoder = asn1.ber.BerEncoder(
        asn1.repository_from_json(
            json.decode_stream(_f)))
