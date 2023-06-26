import collections
import datetime
import math

import pytest

from hat import aio
from hat import util

from hat.drivers import mms
from hat.drivers import tcp


@pytest.fixture
async def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


async def test_listen(addr):

    def on_connection(conn):
        raise NotImplementedError()

    server = await mms.listen(on_connection, addr)

    assert server.is_open
    assert len(server.addresses) == 1

    await server.async_close()


@pytest.mark.parametrize("conn_count", [1, 2, 10])
async def test_connect(addr, conn_count):
    server_conn_queue = aio.Queue()
    server = await mms.listen(server_conn_queue.put_nowait, addr)

    conns = collections.deque()

    for _ in range(conn_count):
        client_conn = await mms.connect(addr)
        server_conn = await server_conn_queue.get()

        conns.append((client_conn, server_conn))

    while conns:
        client_conn, server_conn = conns.popleft()

        assert client_conn.is_open
        assert server_conn.is_open

        await client_conn.async_close()
        await server_conn.wait_closed()

    await server.async_close()


@pytest.mark.parametrize("req, res", [
    (mms.StatusRequest(),
     mms.StatusResponse(logical=1, physical=1)),
    (mms.GetNameListRequest(object_class=mms.ObjectClass.NAMED_VARIABLE,
                            object_scope=mms.VmdSpecificObjectScope(),
                            continue_after='123'),
     mms.GetNameListResponse(identifiers=['a', 'b', 'c'],
                             more_follows=False)),
    (mms.GetNameListRequest(object_class=mms.ObjectClass.NAMED_VARIABLE,
                            object_scope=mms.AaSpecificObjectScope(),
                            continue_after='123'),
     mms.GetNameListResponse(identifiers=['a', 'b', 'c'],
                             more_follows=False)),
    (mms.GetNameListRequest(
        object_class=mms.ObjectClass.NAMED_VARIABLE,
        object_scope=mms.DomainSpecificObjectScope(identifier='1234'),
        continue_after='123'),
     mms.GetNameListResponse(identifiers=['a', 'b', 'c'],
                             more_follows=False)),
    (mms.IdentifyRequest(),
     mms.IdentifyResponse(vendor='a', model='b', revision='c', syntaxes=None)),
    (mms.IdentifyRequest(),
     mms.IdentifyResponse(vendor='a', model='b', revision='c',
                          syntaxes=[(2, 1, 3), (1, 2, 5)])),
    (mms.GetVariableAccessAttributesRequest(value='x'),
     mms.GetVariableAccessAttributesResponse(
         mms_deletable=True, type_description=mms.BooleanTypeDescription())),
    (mms.GetNamedVariableListAttributesRequest(
        value=mms.VmdSpecificObjectName(identifier='x')),
     mms.GetNamedVariableListAttributesResponse(
        mms_deletable=True,
        specification=[
            mms.NameVariableSpecification(
                name=mms.DomainSpecificObjectName(domain_id='abc',
                                                  item_id='xyuz'))])),
    (mms.GetVariableAccessAttributesRequest(
        value=mms.VmdSpecificObjectName(identifier='x')),
     mms.GetVariableAccessAttributesResponse(
        mms_deletable=True, type_description=mms.BooleanTypeDescription())),
    (mms.ReadRequest(value=mms.VmdSpecificObjectName(identifier='x')),
     mms.ReadResponse(results=[mms.BooleanData(value=True)])),
    (mms.ReadRequest(value=mms.VmdSpecificObjectName(identifier='x')),
     mms.ReadResponse(results=[mms.DataAccessError.INVALID_ADDRESS])),
    (mms.WriteRequest(specification=mms.VmdSpecificObjectName(identifier='x'),
                      data=[mms.BooleanData(value=True)]),
     mms.WriteResponse(results=[mms.DataAccessError.INVALID_ADDRESS])),
    (mms.WriteRequest(
        specification=[
            mms.NameVariableSpecification(
                name=mms.DomainSpecificObjectName(domain_id='dev',
                                                  item_id='abc'))],
        data=[mms.BooleanData(value=True)]),
     mms.WriteResponse(results=[None])),
    (mms.DefineNamedVariableListRequest(
        name=mms.VmdSpecificObjectName(identifier='x'),
        specification=[
            mms.NameVariableSpecification(
                name=mms.VmdSpecificObjectName(identifier='b'))]),
     mms.DefineNamedVariableListResponse()),
    (mms.DeleteNamedVariableListRequest(
        names=[mms.VmdSpecificObjectName(identifier='x')]),
     mms.DeleteNamedVariableListResponse(matched=0, deleted=0)),
    (mms.DeleteNamedVariableListRequest(
        names=[mms.VmdSpecificObjectName(identifier='x')]),
     mms.ErrorResponse(error_class=mms.ErrorClass.RESOURCE, value=0))
])
async def test_request_response(addr, req, res):

    def on_request(conn, request):
        assert req == request
        return res

    server_conn_queue = aio.Queue()
    server = await mms.listen(server_conn_queue.put_nowait, addr,
                              request_cb=on_request)
    client_conn = await mms.connect(addr, request_cb=on_request)
    server_conn = await server_conn_queue.get()
    await server.async_close()

    assert client_conn.is_open
    assert server_conn.is_open

    result = await client_conn.send_confirmed(req)
    assert result == res

    result = await server_conn.send_confirmed(req)
    assert result == res

    await server_conn.async_close()
    await client_conn.async_close()


@pytest.mark.parametrize("msg", [
    mms.UnsolicitedStatusUnconfirmed(logical=1, physical=1),
    mms.EventNotificationUnconfirmed(
        enrollment=mms.VmdSpecificObjectName(identifier='x'),
        condition=mms.AaSpecificObjectName(identifier='y'),
        severity=0,
        time=None),
    mms.EventNotificationUnconfirmed(
        enrollment=mms.DomainSpecificObjectName(domain_id='x',
                                                item_id='y'),
        condition=mms.VmdSpecificObjectName(identifier='y'),
        severity=0,
        time=b'2020-7-2T12:00:00.000Z'),
    mms.InformationReportUnconfirmed(
        specification=mms.VmdSpecificObjectName(identifier='x'),
        data=[]),
    mms.InformationReportUnconfirmed(
        specification=[
            mms.AddressVariableSpecification(address=10),
            mms.InvalidatedVariableSpecification(),
            mms.NameVariableSpecification(
                mms.VmdSpecificObjectName(identifier='x')),
            mms.ScatteredAccessDescriptionVariableSpecification(
                specifications=[mms.InvalidatedVariableSpecification()]),
            mms.VariableDescriptionVariableSpecification(
                address=10, type_specification=mms.BooleanTypeDescription()),
            mms.VariableDescriptionVariableSpecification(
                address=10,
                type_specification=mms.VmdSpecificObjectName('x'))],
        data=[mms.ArrayData(elements=[mms.BooleanData(value=True),
                                      mms.BooleanData(value=False),
                                      mms.BooleanData(value=True)])])
])
async def test_unconfirmed(addr, msg):

    server_conn_queue = aio.Queue()
    server_unconfirmed_queue = aio.Queue()
    server = await mms.listen(
        server_conn_queue.put_nowait, addr,
        unconfirmed_cb=lambda _, msg: server_unconfirmed_queue.put_nowait(msg))

    client_unconfirmed_queue = aio.Queue()
    client_conn = await mms.connect(
        addr,
        unconfirmed_cb=lambda _, msg: client_unconfirmed_queue.put_nowait(msg))
    server_conn = await server_conn_queue.get()
    await server.async_close()

    await client_conn.send_unconfirmed(msg)
    result = await server_unconfirmed_queue.get()
    assert result == msg

    await server_conn.send_unconfirmed(msg)
    result = await client_unconfirmed_queue.get()
    assert result == msg

    await server_conn.async_close()
    await client_conn.async_close()


@pytest.mark.parametrize("type_description", [
    mms.ArrayTypeDescription(number_of_elements=10,
                             element_type=mms.VmdSpecificObjectName('x')),
    mms.BcdTypeDescription(xyz=1213),
    mms.BinaryTimeTypeDescription(xyz=True),
    mms.BitStringTypeDescription(xyz=1213),
    mms.BooleanTypeDescription(),
    mms.FloatingPointTypeDescription(format_width=12, exponent_width=10),
    mms.GeneralizedTimeTypeDescription(),
    mms.IntegerTypeDescription(xyz=345),
    mms.MmsStringTypeDescription(xyz=123),
    mms.ObjIdTypeDescription(),
    mms.OctetStringTypeDescription(xyz=1231),
    mms.StructureTypeDescription(components=[
        ('1', mms.ObjIdTypeDescription()),
        (None, mms.BooleanTypeDescription()),
        (None, mms.VmdSpecificObjectName('x'))]),
    mms.UnsignedTypeDescription(xyz=21412),
    mms.UtcTimeTypeDescription(),
    mms.VisibleStringTypeDescription(xyz=5542),
])
async def test_type_description_serialization(addr, type_description):
    req = mms.GetVariableAccessAttributesRequest(value='x')
    res = mms.GetVariableAccessAttributesResponse(
        mms_deletable=True, type_description=type_description)

    async def on_request(conn, request):
        assert request == req
        return res

    server_conn_queue = aio.Queue()
    server = await mms.listen(server_conn_queue.put_nowait, addr,
                              request_cb=on_request)
    client_conn = await mms.connect(addr)
    server_conn = await server_conn_queue.get()
    await server.async_close()

    result = await client_conn.send_confirmed(req)
    assert result == res

    await server_conn.async_close()
    await client_conn.async_close()


@pytest.mark.parametrize("data", [
    mms.BcdData(10),
    mms.ArrayData([mms.BcdData(11), mms.BcdData(12)]),
    mms.BinaryTimeData(datetime.datetime.utcnow().replace(
        microsecond=0,
        tzinfo=datetime.timezone.utc)),
    mms.BitStringData([True, False, True]),
    mms.BooleanData(True),
    mms.BooleanArrayData([True, False]),
    mms.FloatingPointData(1.25),
    mms.GeneralizedTimeData('19851106210627.3'),
    mms.IntegerData(100),
    mms.MmsStringData('abcxyz'),
    mms.ObjIdData((0, 1, 1, 4, 1203)),
    mms.OctetStringData(b'34104332'),
    mms.StructureData([mms.MmsStringData('xyz'),
                       mms.IntegerData(321412)]),
    mms.UnsignedData(123),
    mms.UtcTimeData(value=datetime.datetime.now(datetime.timezone.utc),
                    leap_second=False,
                    clock_failure=False,
                    not_synchronized=False,
                    accuracy=None),
    mms.VisibleStringData('123')
])
async def test_data_serialization(addr, data):
    req = mms.ReadRequest(mms.AaSpecificObjectName('x'))
    res = mms.ReadResponse([data])

    async def on_request(conn, request):
        assert request == req
        return res

    server_conn_queue = aio.Queue()
    server = await mms.listen(server_conn_queue.put_nowait, addr,
                              request_cb=on_request)
    client_conn = await mms.connect(addr)
    server_conn = await server_conn_queue.get()
    await server.async_close()

    result = await client_conn.send_confirmed(req)
    result = result.results[0]

    if isinstance(data, mms.FloatingPointData):
        assert isinstance(result, mms.FloatingPointData)
        assert math.isclose(data.value, result.value)

    else:
        assert data == result

    await server_conn.async_close()
    await client_conn.async_close()
