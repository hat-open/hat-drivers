import collections
import logging

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


def create_logger(logger: logging.Logger,
                  meta_type: str,
                  info: udp.EndpointInfo
                  ) -> logging.LoggerAdapter:
    extra = {'meta': {'type': meta_type,
                      'name': info.name,
                      'local_addr': {'host': info.local_addr.host,
                                     'port': info.local_addr.port}}}

    if info.remote_addr is not None:
        extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                        'port': info.remote_addr.port}

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 meta_type: str,
                 info: udp.EndpointInfo):
        extra = {'meta': {'type': meta_type,
                          'communication': True,
                          'name': info.name,
                          'local_addr': {'host': info.local_addr.host,
                                         'port': info.local_addr.port}}}

        if info.remote_addr is not None:
            extra['meta']['remote_addr'] = {'host': info.remote_addr.host,
                                            'port': info.remote_addr.port}

        self._log = logging.LoggerAdapter(logger, extra)

    def log(self,
            action: common.CommLogAction,
            msg: encoder.Msg | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if msg is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_msg(msg),
                            stacklevel=2)


def _format_msg(msg):
    if isinstance(msg, encoder.v1.Msg):
        return _format_v1_msg(msg)

    if isinstance(msg, encoder.v2c.Msg):
        return _format_v2c_msg(msg)

    if isinstance(msg, encoder.v3.Msg):
        return _format_v3_msg(msg)

    raise TypeError('unsupported message type')


def _format_v1_msg(msg):
    segments = collections.deque()

    segments.append(msg.type.name)
    segments.append(f"community={msg.community}")

    if isinstance(msg.pdu, encoder.v1.BasicPdu):
        segments.append(f"req_id={msg.pdu.request_id}")

        if msg.pdu.error.type != common.ErrorType.NO_ERROR:
            segments.append(f"error={_format_error(msg.pdu.error)}")

    elif isinstance(msg.pdu, encoder.v1.TrapPdu):
        segments.append(f"enterprise={_format_oid(msg.pdu.enterprise)}")
        segments.append(f"addr={_format_address(msg.pdu.addr)}")
        segments.append(f"cause={_format_cause(msg.pdu.cause)}")
        segments.append(f"timestamp={msg.pdu.timestamp}")

    else:
        raise TypeError('unsupported pdu type')

    data = collections.deque()
    for i in msg.pdu.data:
        data.append(_format_data(i))

    segments.append(f"data={_format_segments(data)}")

    return _format_segments(segments)


def _format_v2c_msg(msg):
    segments = collections.deque()

    segments.append(msg.type.name)
    segments.append(f"community={msg.community}")

    if isinstance(msg.pdu, encoder.v2c.BasicPdu):
        segments.append(f"req_id={msg.pdu.request_id}")

        if msg.pdu.error.type != common.ErrorType.NO_ERROR:
            segments.append(f"error={_format_error(msg.pdu.error)}")

    elif isinstance(msg.pdu, encoder.v2c.BulkPdu):
        segments.append(f"req_id={msg.pdu.request_id}")
        segments.append(f"non_repeaters={msg.pdu.non_repeaters}")
        segments.append(f"max_repetitions={msg.pdu.max_repetitions}")

    else:
        raise TypeError('unsupported pdu type')

    data = collections.deque()
    for i in msg.pdu.data:
        data.append(_format_data(i))

    segments.append(f"data={_format_segments(data)}")

    return _format_segments(segments)


def _format_v3_msg(msg):
    segments = collections.deque()

    segments.append(msg.type.name)
    segments.append(f"id={msg.id}")

    if msg.reportable:
        segments.append('reportable')

    if msg.auth:
        segments.append('auth')

    if msg.priv:
        segments.append('priv')

    segments.append(
        f"engine={_format_authorative_engine(msg.authorative_engine)}")
    segments.append(f"user={msg.user}")
    segments.append(f"context={_format_context(msg.context)}")

    if isinstance(msg.pdu, encoder.v3.BasicPdu):
        segments.append(f"req_id={msg.pdu.request_id}")

        if msg.pdu.error.type != common.ErrorType.NO_ERROR:
            segments.append(f"error={_format_error(msg.pdu.error)}")

    elif isinstance(msg.pdu, encoder.v3.BulkPdu):
        segments.append(f"req_id={msg.pdu.request_id}")
        segments.append(f"non_repeaters={msg.pdu.non_repeaters}")
        segments.append(f"max_repetitions={msg.pdu.max_repetitions}")

    else:
        raise TypeError('unsupported pdu type')

    data = collections.deque()
    for i in msg.pdu.data:
        data.append(_format_data(i))

    segments.append(f"data={_format_segments(data)}")


def _format_error(error):
    segments = collections.deque()
    segments.append(error.type.name)
    segments.append(f"index={error.index}")

    return _format_segments(segments)


def _format_cause(cause):
    segments = collections.deque()
    segments.append(cause.type.name)
    segments.append(f"value={cause.value}")

    return _format_segments(segments)


def _format_data(data):
    segments = collections.deque()
    segments.append(f"name={_format_oid(data.name)}")

    if isinstance(data, (common.IntegerData,
                         common.UnsignedData,
                         common.CounterData,
                         common.BigCounterData,
                         common.TimeTicksData)):
        segments.append(f"value={data.value}")

    elif isinstance(data, (common.StringData,
                           common.ArbitraryData)):
        segments.append(f"value=({data.value.hex(' ')})")

    elif isinstance(data, common.ObjectIdData):
        segments.append(f"value={_format_oid(data.value)}")

    elif isinstance(data, common.IpAddressData):
        segments.append(f"value={_format_address(data.value)}")

    else:
        name = type(data).__name__[:-4]
        segments.append(name)

    return _format_segments(segments)


def _format_oid(oid):
    return '.'.join(str(i) for i in oid)


def _format_address(addr):
    return '.'.join(str(i) for i in addr)


def _format_authorative_engine(engine):
    segments = collections.deque()
    segments.append(f"id=({engine.id.hex(' ')})")
    segments.append(f"boots={engine.boots}")
    segments.append(f"time={engine.time}")

    return _format_segments(segments)


def _format_context(context):
    segments = collections.deque()
    segments.append(f"engine_id=({context.engine_id.hex(' ')})")
    segments.append(f"name={context.name}")

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
