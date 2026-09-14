import collections
import logging

from hat.drivers import net
from hat.drivers import serial

from hat.drivers.modbus.transport import common


def create_logger(logger: logging.Logger,
                  info: net.ConnectionInfo | serial.EndpointInfo
                  ) -> logging.LoggerAdapter:
    if isinstance(info, net.TcpConnectionInfo):
        extra = {'meta': {'type': 'ModbusTcpConnection',
                          **net.connection_info_to_json(info)}}

    elif isinstance(info, serial.EndpointInfo):
        extra = {'meta': {'type': 'ModbusSerialConnection',
                          **serial.endpoint_info_to_json(info)}}

    else:
        raise TypeError('invalid info type')

    return logging.LoggerAdapter(logger, extra)


class CommunicationLogger:

    def __init__(self,
                 logger: logging.Logger,
                 info: net.ConnectionInfo | serial.EndpointInfo):
        self._log = create_logger(logger=logger,
                                  info=info)
        self._log.extra['meta']['communication'] = True

    def log(self,
            action: common.CommLogAction,
            adu: common.Adu | None = None):
        if not self._log.isEnabledFor(logging.DEBUG):
            return

        if adu is None:
            self._log.debug(action.value, stacklevel=2)

        else:
            self._log.debug('%s %s', action.value, _format_adu(adu),
                            stacklevel=2)


def _format_adu(adu):
    segments = collections.deque()
    segments.append(type(adu.pdu).__name__)

    if isinstance(adu, common.TcpAdu):
        segments.append(f"transaction={adu.transaction_id}")
        segments.append(f"device={adu.device_id}")

    elif isinstance(adu, common.RtuAdu):
        segments.append(f"device={adu.device_id}")

    elif isinstance(adu, common.AsciiAdu):
        segments.append(f"device={adu.device_id}")

    else:
        raise TypeError('unsupported adu type')

    if isinstance(adu.pdu, common.ErrorRes):
        segments.append(f"fc={adu.pdu.fc.name}")
        segments.append(f"error={adu.pdu.error.name}")

    elif isinstance(adu.pdu, common.ReadCoilsReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.ReadCoilsRes):
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.ReadDiscreteInputsReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.ReadDiscreteInputsRes):
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.ReadHoldingRegistersReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.ReadHoldingRegistersRes):
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.ReadInputRegistersReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.ReadInputRegistersRes):
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.WriteSingleCoilReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"value={adu.pdu.value}")

    elif isinstance(adu.pdu, common.WriteSingleCoilRes):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"value={adu.pdu.value}")

    elif isinstance(adu.pdu, common.WriteSingleRegisterReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"value={adu.pdu.value}")

    elif isinstance(adu.pdu, common.WriteSingleRegisterRes):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"value={adu.pdu.value}")

    elif isinstance(adu.pdu, common.WriteMultipleCoilsReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.WriteMultipleCoilsRes):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.WriteMultipleRegistersReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"values={adu.pdu.values}")

    elif isinstance(adu.pdu, common.WriteMultipleRegistersRes):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"quantity={adu.pdu.quantity}")

    elif isinstance(adu.pdu, common.MaskWriteRegisterReq):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"and={adu.pdu.and_mask}")
        segments.append(f"or={adu.pdu.or_mask}")

    elif isinstance(adu.pdu, common.MaskWriteRegisterRes):
        segments.append(f"addr={adu.pdu.address}")
        segments.append(f"and={adu.pdu.and_mask}")
        segments.append(f"or={adu.pdu.or_mask}")

    elif isinstance(adu.pdu, common.ReadFifoQueueReq):
        segments.append(f"addr={adu.pdu.address}")

    elif isinstance(adu.pdu, common.ReadFifoQueueRes):
        segments.append(f"values={adu.pdu.values}")

    else:
        raise TypeError('unsupported pdu type')

    return _format_segments(segments)


def _format_segments(segments):
    if len(segments) == 1:
        return segments[0]

    return f"({' '.join(segments)})"
