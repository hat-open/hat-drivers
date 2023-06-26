from hat.drivers.modbus.common import *  # NOQA

import abc
import enum
import typing

from hat.drivers.modbus.common import Error


Request = type('Request', (abc.ABC, ), {})
Response = type('Response', (abc.ABC, ), {})


def request(cls):
    Request.register(cls)
    return cls


def response(cls):
    Response.register(cls)
    return cls


class Direction(enum.Enum):
    REQUEST = 0
    RESPONSE = 1


class FunctionCode(enum.Enum):
    READ_COILS = 1
    READ_DISCRETE_INPUTS = 2
    READ_HOLDING_REGISTERS = 3
    READ_INPUT_REGISTERS = 4
    WRITE_SINGLE_COIL = 5
    WRITE_SINGLE_REGISTER = 6
    WRITE_MULTIPLE_COILS = 15
    WRITE_MULTIPLE_REGISTER = 16
    MASK_WRITE_REGISTER = 22
    READ_FIFO_QUEUE = 24


@response
class ErrorRes(typing.NamedTuple):
    fc: FunctionCode
    error: Error


@request
class ReadCoilsReq(typing.NamedTuple):
    address: int
    quantity: int | None


@response
class ReadCoilsRes(typing.NamedTuple):
    values: list[int]


@request
class ReadDiscreteInputsReq(typing.NamedTuple):
    address: int
    quantity: int | None


@response
class ReadDiscreteInputsRes(typing.NamedTuple):
    values: list[int]


@request
class ReadHoldingRegistersReq(typing.NamedTuple):
    address: int
    quantity: int | None


@response
class ReadHoldingRegistersRes(typing.NamedTuple):
    values: list[int]


@request
class ReadInputRegistersReq(typing.NamedTuple):
    address: int
    quantity: int | None


@response
class ReadInputRegistersRes(typing.NamedTuple):
    values: list[int]


@request
class WriteSingleCoilReq(typing.NamedTuple):
    address: int
    value: int


@response
class WriteSingleCoilRes(typing.NamedTuple):
    address: int
    value: int


@request
class WriteSingleRegisterReq(typing.NamedTuple):
    address: int
    value: int


@response
class WriteSingleRegisterRes(typing.NamedTuple):
    address: int
    value: int


@request
class WriteMultipleCoilsReq(typing.NamedTuple):
    address: int
    values: list[int]


@response
class WriteMultipleCoilsRes(typing.NamedTuple):
    address: int
    quantity: int


@request
class WriteMultipleRegistersReq(typing.NamedTuple):
    address: int
    values: list[int]


@response
class WriteMultipleRegistersRes(typing.NamedTuple):
    address: int
    quantity: int


@request
class MaskWriteRegisterReq(typing.NamedTuple):
    address: int
    and_mask: int
    or_mask: int


@response
class MaskWriteRegisterRes(typing.NamedTuple):
    address: int
    and_mask: int
    or_mask: int


@request
class ReadFifoQueueReq(typing.NamedTuple):
    address: int


@response
class ReadFifoQueueRes(typing.NamedTuple):
    values: list[int]


Pdu: typing.TypeAlias = Request | Response


class TcpAdu(typing.NamedTuple):
    transaction_id: int
    device_id: int
    pdu: Pdu


class RtuAdu(typing.NamedTuple):
    device_id: int
    pdu: Pdu


class AsciiAdu(typing.NamedTuple):
    device_id: int
    pdu: Pdu


Adu: typing.TypeAlias = TcpAdu | RtuAdu | AsciiAdu


def get_pdu_function_code(pdu: Pdu) -> FunctionCode:
    if isinstance(pdu, ErrorRes):
        return pdu.fc

    if isinstance(pdu, (ReadCoilsReq,
                        ReadCoilsRes)):
        return FunctionCode.READ_COILS

    if isinstance(pdu, (ReadDiscreteInputsReq,
                        ReadDiscreteInputsRes)):
        return FunctionCode.READ_DISCRETE_INPUTS

    if isinstance(pdu, (ReadHoldingRegistersReq,
                        ReadHoldingRegistersRes)):
        return FunctionCode.READ_HOLDING_REGISTERS

    if isinstance(pdu, (ReadInputRegistersReq,
                        ReadInputRegistersRes)):
        return FunctionCode.READ_INPUT_REGISTERS

    if isinstance(pdu, (WriteSingleCoilReq,
                        WriteSingleCoilRes)):
        return FunctionCode.WRITE_SINGLE_COIL

    if isinstance(pdu, (WriteSingleRegisterReq,
                        WriteSingleRegisterRes)):
        return FunctionCode.WRITE_SINGLE_REGISTER

    if isinstance(pdu, (WriteMultipleCoilsReq,
                        WriteMultipleCoilsRes)):
        return FunctionCode.WRITE_MULTIPLE_COILS

    if isinstance(pdu, (WriteMultipleRegistersReq,
                        WriteMultipleRegistersRes)):
        return FunctionCode.WRITE_MULTIPLE_REGISTER

    if isinstance(pdu, (MaskWriteRegisterReq,
                        MaskWriteRegisterRes)):
        return FunctionCode.MASK_WRITE_REGISTER

    if isinstance(pdu, (ReadFifoQueueReq,
                        ReadFifoQueueRes)):
        return FunctionCode.READ_FIFO_QUEUE

    raise ValueError('unsupported pdu')
