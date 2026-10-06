from hat.drivers.common import *  # NOQA

import typing


UInt3: typing.TypeAlias = int
"""In range [0, 0x07]"""

UInt4: typing.TypeAlias = int
"""In range [0, 0x0f]"""

UInt7: typing.TypeAlias = int
"""In range [0, 0x7f]"""

UInt8: typing.TypeAlias = int
"""In range [0, 0xff]"""

UInt16: typing.TypeAlias = int
"""In range [0, 0xffff]"""

UInt24: typing.TypeAlias = int
"""In range [0, 0xffffff]"""
