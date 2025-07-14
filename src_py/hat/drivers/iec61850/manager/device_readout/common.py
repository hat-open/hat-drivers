from hat.drivers.iec61850.manager.common import *  # NOQA

import typing

from hat import json

from hat.drivers.iec61850.manager.common import (BasicValueType,
                                                 AcsiValueType,
                                                 ArrayValueType,
                                                 StructValueType,
                                                 ValueType,
                                                 DataRef,
                                                 PersistedDatasetRef,
                                                 NonPersistedDatasetRef,
                                                 DatasetRef,
                                                 RcbRef,
                                                 CommandRef)


class RootDataRef(typing.NamedTuple):
    logical_device: str
    logical_node: str
    fc: str
    name: str


def value_type_to_json(value_type: ValueType) -> json.Data:
    if isinstance(value_type, BasicValueType):
        return value_type.name

    if isinstance(value_type, AcsiValueType):
        return value_type.name

    if isinstance(value_type, ArrayValueType):
        return {'type': 'ARRAY',
                'element_type': value_type_to_json(value_type.type),
                'length': value_type.length}

    if isinstance(value_type, StructValueType):
        return {'type': 'STRUCT',
                'elements': [{'name': i_name,
                              'type': value_type_to_json(i_type)}
                             for i_name, i_type in value_type.elements]}

    raise TypeError('unsupported value type')


def data_ref_to_json(ref: DataRef) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'fc': ref.fc,
            'names': list(ref.names)}


def dataset_ref_to_json(ref: DatasetRef) -> json.Data:
    if isinstance(ref, PersistedDatasetRef):
        return {'logical_device': ref.logical_device,
                'logical_node': ref.logical_node,
                'name': ref.name}

    if isinstance(ref, NonPersistedDatasetRef):
        return ref.name

    raise TypeError('unsupported ref type')


def rcb_ref_to_json(ref: RcbRef) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'type': ref.type.name,
            'name': ref.name}


def command_ref_to_json(ref: CommandRef) -> json.Data:
    return {'logical_device': ref.logical_device,
            'logical_node': ref.logical_node,
            'name': ref.name}
