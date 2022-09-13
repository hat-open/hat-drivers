from hat import json
from hat.drivers.pnetgateway import common


def data_to_json(data: common.Data) -> json.Data:
    return {'key': data.key,
            'value': data.value,
            'quality': data.quality.value,
            'timestamp': data.timestamp,
            'type': data.type.value,
            'source': data.source.value}


def data_from_json(data: json.Data) -> common.Data:
    return common.Data(key=data['key'],
                       value=data['value'],
                       quality=common.Quality(data['quality']),
                       timestamp=data['timestamp'],
                       type=common.DataType(data['type']),
                       source=common.Source(data['source']))


def change_to_json(change: common.Change) -> json.Data:
    res = {'key': change.key}

    if change.value is not None:
        res['value'] = change.value

    if change.quality is not None:
        res['quality'] = change.quality.value

    if change.timestamp is not None:
        res['timestamp'] = change.timestamp

    if change.source is not None:
        res['source'] = change.source.value

    return res


def change_from_json(change: json.Data) -> common.Change:
    return common.Change(key=change['key'],
                         value=change.get('value'),
                         quality=(common.Quality(change['quality'])
                                  if 'quality' in change else None),
                         timestamp=change.get('timestamp'),
                         source=(common.Source(change['source'])
                                 if 'source' in change else None))


def command_to_json(cmd: common.Command) -> json.Data:
    return {'key': cmd.key,
            'value': cmd.value}


def command_from_json(cmd: json.Data) -> common.Command:
    return common.Command(key=cmd['key'],
                          value=cmd['value'])
