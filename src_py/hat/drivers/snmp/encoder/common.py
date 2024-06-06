from hat.drivers.snmp.common import *  # NOQA

import importlib.resources

from hat import asn1


with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'asn1_repo.json') as _path:
    encoder = asn1.Encoder(asn1.Encoding.BER,
                           asn1.Repository.from_json(_path))
