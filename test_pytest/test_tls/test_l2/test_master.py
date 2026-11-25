import asyncio
import enum
import sys

import pytest

from hat import aio
from hat import util

from hat.drivers import net
from hat.drivers import serial
from hat.drivers.tls import l1
from hat.drivers.tls.l2 import common
from hat.drivers.tls.l2 import encoder
from hat.drivers.tls.l2 import master


CommType = enum.Enum('CommType', ['TCP', 'UNIX', 'SERIAL'])


if sys.platform == 'win32':
    comm_types = [CommType.TCP]
else:
    comm_types = [CommType.TCP,
                  CommType.UNIX,
                  CommType.SERIAL]


@pytest.fixture
def tcp_addr():
    return net.TcpAddress('127.0.0.1', util.get_unused_tcp_port())


@pytest.fixture
def unix_addr(tmp_path):
    return tmp_path / 'sock'


@pytest.fixture
async def patch_serial_read_timeout(monkeypatch):
    monkeypatch.setattr(serial.py_serial, 'read_timeout', 0.01)


class _MockSlave(aio.Resource):

    def __init__(self, link: l1.Link):
        self._link = link
        self._receive_queue = aio.Queue()
        self.async_group.spawn(self._receive_loop)

    @property
    def async_group(self) -> aio.Group:
        return self._link.async_group

    @property
    def info(self) -> l1.LinkInfo:
        return self._link.info

    async def send(self, frame):
        await self.send_raw(encoder.encode_frame(frame))

    async def send_raw(self, data):
        await self._link.write(data)
        await self._link.drain()

    async def receive(self):
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _receive_loop(self):
        data = b''

        try:
            while True:
                size = encoder.get_next_frame_size(data)

                if len(data) < size:
                    data += bytes(await self._link.read(size - len(data)))
                    continue

                frame_data, data = data[:size], data[size:]
                frame = encoder.decode_frame(frame_data)
                self._receive_queue.put_nowait(frame)

        except ConnectionError:
            pass

        finally:
            self.close()
            self._receive_queue.close()


@pytest.fixture
async def create_master_slave_links(tcp_addr, unix_addr, nullmodem,
                                    patch_serial_read_timeout):
    links = []
    endpoints = []

    async def create_master_slave_links(comm_type):
        slave_queue = aio.Queue()
        master_queue = aio.Queue()

        if comm_type in (CommType.TCP, CommType.UNIX):
            addr = tcp_addr if comm_type == CommType.TCP else unix_addr
            slave_endpoint = await l1.create_net_server_endpoint(
                link_cb=slave_queue.put_nowait,
                addr=addr)
            endpoints.append(slave_endpoint)
            master_endpoint = await l1.create_net_client_endpoint(
                link_cb=master_queue.put_nowait,
                addr=addr,
                reconnect_delay=0.01)
            endpoints.append(master_endpoint)

        elif comm_type == CommType.SERIAL:
            slave_endpoint = await l1.create_serial_endpoint(
                link_cb=slave_queue.put_nowait,
                port=str(nullmodem[0]),
                reconnect_delay=0.01)
            endpoints.append(slave_endpoint)
            master_endpoint = await l1.create_serial_endpoint(
                link_cb=master_queue.put_nowait,
                port=str(nullmodem[1]),
                reconnect_delay=0.01)
            endpoints.append(master_endpoint)

        else:
            raise ValueError()

        slave_link = await slave_queue.get()
        links.append(slave_link)
        master_link = await master_queue.get()
        links.append(master_link)

        return master_link, slave_link

    yield create_master_slave_links

    for link in links:
        await link.async_close()
    for endpoint in endpoints:
        await endpoint.async_close()


async def connect(link, slave_link, addr, send_retry_count=3,
                  poll_data_delay=None, poll_test_delay=None):
    master_link = master.MasterLink(link=link)
    master_conn_fut = master_link.async_group.spawn(
        master_link.open_connection,
        addr=addr,
        send_retry_count=send_retry_count,
        poll_data_delay=poll_data_delay,
        poll_test_delay=poll_test_delay)

    slave = _MockSlave(slave_link)

    await slave.receive()

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_STATUS,
        address=addr,
        data=b''))

    await slave.receive()

    await slave.send(common.ShortFrame())

    master_conn = await master_conn_fut

    return master_conn, slave


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('reset_unit', [True, False])
async def test_connect(create_master_slave_links, comm_type, reset_unit):
    addr = 1
    connect_delay = 0.01

    link, slave_link = await create_master_slave_links(comm_type)
    master_link = master.MasterLink(link=link)
    master_conn_fut = master_link.async_group.spawn(
        master_link.open_connection, addr=addr, reset_unit=reset_unit,
        connect_delay=connect_delay)

    slave = _MockSlave(slave_link)

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.REQ_STATUS

    # timeout, starting over
    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.REQ_STATUS

    # ignored, starting over
    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.REJECT,
        address=addr,
        data=b''))

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.REQ_STATUS

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_STATUS,
        address=addr,
        data=b''))

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == (common.ReqFunction.RESET_UNIT if reset_unit
                            else common.ReqFunction.RESET_COMMUNICATION)

    # ignored, starting over
    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.REJECT,
        address=addr,
        data=b''))

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.REQ_STATUS

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_STATUS,
        address=addr,
        data=b''))

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == (common.ReqFunction.RESET_UNIT if reset_unit
                            else common.ReqFunction.RESET_COMMUNICATION)

    await slave.send(common.ShortFrame())

    master_conn = await master_conn_fut
    assert master_conn.is_open
    assert master_conn.info.addr == addr

    await master_conn.async_close()
    assert master_link.is_open


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('reset_unit', [True, False])
async def test_connect_reset_ack(create_master_slave_links, comm_type,
                                 reset_unit):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_link = master.MasterLink(link=link)
    master_conn_fut = master_link.async_group.spawn(
        master_link.open_connection, addr=addr, reset_unit=reset_unit)

    slave = _MockSlave(slave_link)

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == common.ReqFunction.REQ_STATUS

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_STATUS,
        address=addr,
        data=b''))

    req = await slave.receive()
    assert isinstance(req, common.ReqFrame)
    assert req.function == (common.ReqFunction.RESET_UNIT if reset_unit
                            else common.ReqFunction.RESET_COMMUNICATION)

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RESET_ACK,
        address=addr,
        data=b''))

    master_conn = await master_conn_fut
    assert master_conn.is_open
    assert master_conn.info.addr == addr

    await master_conn.async_close()
    assert master_link.is_open


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('address', [common.broadcast_address, 12345])
async def test_connect_unsupported_address(create_master_slave_links,
                                           comm_type, address):
    link, slave_link = await create_master_slave_links(comm_type)
    master_link = master.MasterLink(link=link)
    with pytest.raises(Exception):
        await master_link.open_connection(addr=address)


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('exceeded', [True, False])
@pytest.mark.parametrize('send_retry_count', [1, 5])
async def test_send_retry_count(create_master_slave_links, comm_type,
                                exceeded, send_retry_count):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       send_retry_count=send_retry_count)

    send_group = link.async_group.create_subgroup(
        log_exceptions=False)
    send_future = send_group.spawn(master_conn.send, b'hello')
    received_first = await slave.receive()
    assert received_first.data == b'hello'

    for i in range(send_retry_count):
        received_retry = await slave.receive()
        assert received_retry == received_first

    assert not send_future.done()

    if exceeded:
        # no response after send_retry_count exceeded
        with pytest.raises(Exception):
            await send_future
        await master_conn.wait_closed()

    else:
        await slave.send(common.ShortFrame())
        await send_future
        assert master_conn.is_open


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('req_function', [common.ReqFunction.SEND_DATA,
                                          common.ReqFunction.SEND_TEST])
async def test_send(create_master_slave_links, comm_type, req_function):
    addr = 1
    is_test = req_function == common.ReqFunction.SEND_TEST

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr)

    send_group = link.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(master_conn.send, b'data', with_ack=True,
                                   test=is_test)
    received = await slave.receive()
    assert received.data == b'data'
    assert received.function == req_function

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_ACK,
        address=addr,
        data=b''))

    await send_future

    send_future = send_group.spawn(master_conn.send, b'data', with_ack=False,
                                   test=is_test)
    received = await slave.receive()
    assert received.data == b'data'

    if req_function == common.ReqFunction.SEND_TEST:
        assert received.function == common.ReqFunction.SEND_TEST

        await slave.send(common.ResFrame(
            access_demand=False,
            data_flow_control=False,
            function=common.ResFunction.RES_ACK,
            address=addr,
            data=b''))

    else:
        assert received.function == common.ReqFunction.SEND_DATA_NO_RES

    await send_future


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('with_ack, req_function', [
    (True, common.ReqFunction.SEND_DATA),
    (False, common.ReqFunction.SEND_DATA_NO_RES)])
async def test_send_data_with_ack(create_master_slave_links, comm_type,
                                  with_ack, req_function):
    send_retry_count = 3

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr=1,
                                       send_retry_count=send_retry_count)

    send_group = link.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(
        master_conn.send, b'data', with_ack=with_ack)
    req_first = await slave.receive()
    assert req_first.data == b'data'
    assert req_first.function == req_function

    if with_ack:
        for i in range(send_retry_count):
            req_retry = await slave.receive()
            assert req_retry == req_first

        assert not send_future.done()
        with pytest.raises(Exception):
            await send_future
        await master_conn.wait_closed()

    else:
        await send_future
        assert master_conn.is_open


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('with_ack', [True, False])
async def test_send_test(create_master_slave_links, comm_type, with_ack):
    send_retry_count = 3

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr=1,
                                       send_retry_count=send_retry_count)

    send_group = link.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(
        master_conn.send, b'hello', with_ack=with_ack, test=True)
    req_first = await slave.receive()
    assert req_first.data == b'hello'
    assert req_first.function == common.ReqFunction.SEND_TEST

    for i in range(send_retry_count):
        req_retry = await slave.receive()
        assert req_retry == req_first

    assert not send_future.done()
    with pytest.raises(Exception):
        await send_future
    await master_conn.wait_closed()


@pytest.mark.parametrize('comm_type', comm_types)
@pytest.mark.parametrize('is_test', [True, False])
@pytest.mark.parametrize('res_function', [common.ResFunction.RESET_ACK,
                                          common.ResFunction.REJECT,
                                          # common.ResFunction.RES_ACK,
                                          common.ResFunction.RES_REJECT,
                                          common.ResFunction.RES_STATUS])
async def test_send_unexpected_response(create_master_slave_links, comm_type,
                                        is_test, res_function):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr)

    send_group = master_conn.async_group.create_subgroup(
        log_exceptions=False)
    send_future = send_group.spawn(master_conn.send, b'data',
                                   with_ack=True, test=is_test)
    received = await slave.receive()
    assert received.data == b'data'

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=res_function,
        address=addr,
        data=b''))

    with pytest.raises(Exception):
        await send_future


@pytest.mark.parametrize('comm_type', comm_types)
async def test_poll_data_loop(create_master_slave_links, comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_data_delay=0.01)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))
    received = await master_conn.receive()
    assert received == (b'data', False)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_ACK,
        address=addr,
        data=b''))

    with pytest.raises(Exception):
        await asyncio.wait_for(master_conn.receive(), 1)


@pytest.mark.parametrize('comm_type', comm_types)
async def test_poll_test_loop(create_master_slave_links, comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_test_delay=0.01)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_TEST
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_TEST,
        address=addr,
        data=b'data'))
    received = await master_conn.receive()
    assert received == (b'data', True)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_TEST
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_ACK,
        address=addr,
        data=b''))

    with pytest.raises(Exception):
        await asyncio.wait_for(master_conn.receive(), 1)


@pytest.mark.parametrize('comm_type', comm_types)
async def test_frame_count_bit(create_master_slave_links, comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_data_delay=0.01)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''
    assert req.frame_count_valid

    frame_count_bit = req.frame_count_bit

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))
    received = await master_conn.receive()
    assert received == (b'data', False)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''
    assert req.frame_count_valid
    assert req.frame_count_bit != frame_count_bit

    frame_count_bit = req.frame_count_bit

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))
    received = await master_conn.receive()
    assert received == (b'data', False)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''
    assert req.frame_count_valid
    assert req.frame_count_bit != frame_count_bit

    frame_count_bit = req.frame_count_bit

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))
    received = await master_conn.receive()
    assert received == (b'data', False)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''
    assert req.frame_count_valid
    assert req.frame_count_bit != frame_count_bit


@pytest.mark.parametrize('comm_type', comm_types)
async def test_access_demand(create_master_slave_links, comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_data_delay=100)

    req = await slave.receive()
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=True,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))

    received = await master_conn.receive()
    assert received == (b'data', False)

    req = await asyncio.wait_for(slave.receive(), 0.1)
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b''))

    with pytest.raises(Exception):
        await asyncio.wait_for(slave.receive(), 0.1)


@pytest.mark.parametrize('comm_type', comm_types)
async def test_data_flow_control_poll_data(create_master_slave_links,
                                           comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_data_delay=0.01)

    req = await asyncio.wait_for(slave.receive(), 0.1)
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=True,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))

    send_group = link.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(master_conn.send, b'master data')

    req = await asyncio.wait_for(slave.receive(), 0.1)
    assert req.function == common.ReqFunction.REQ_DATA_1_OR_2
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_DATA,
        address=addr,
        data=b'data'))

    while True:
        req = await asyncio.wait_for(slave.receive(), 0.1)
        if req.function == common.ReqFunction.SEND_DATA:
            break

    assert req.data == b'master data'

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_ACK,
        address=addr,
        data=b''))

    await send_future


@pytest.mark.parametrize('comm_type', comm_types)
async def test_data_flow_control_poll_test(create_master_slave_links,
                                           comm_type):
    addr = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       poll_test_delay=0.01)

    req = await asyncio.wait_for(slave.receive(), 0.1)
    assert req.function == common.ReqFunction.REQ_TEST
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=True,
        function=common.ResFunction.RES_TEST,
        address=addr,
        data=b'data'))

    send_group = link.async_group.create_subgroup(log_exceptions=False)
    send_future = send_group.spawn(master_conn.send, b'master data')

    req = await asyncio.wait_for(slave.receive(), 0.1)
    assert req.function == common.ReqFunction.REQ_TEST
    assert req.data == b''

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_TEST,
        address=addr,
        data=b'data'))

    while True:
        req = await asyncio.wait_for(slave.receive(), 0.1)
        if req.function == common.ReqFunction.SEND_DATA:
            break

    assert req.data == b'master data'

    await slave.send(common.ResFrame(
        access_demand=False,
        data_flow_control=False,
        function=common.ResFunction.RES_ACK,
        address=addr,
        data=b'data'))

    await send_future


@pytest.mark.parametrize('comm_type', comm_types)
async def test_slave_close(create_master_slave_links, comm_type):
    addr = 1
    send_retry_count = 1

    link, slave_link = await create_master_slave_links(comm_type)
    master_conn, slave = await connect(link, slave_link, addr,
                                       send_retry_count=send_retry_count)

    assert master_conn.is_open
    await slave.async_close()

    if comm_type in (CommType.TCP, CommType.UNIX):
        await asyncio.wait_for(master_conn.wait_closed(), 1)
        await asyncio.wait_for(link.wait_closed(), 1)

    else:
        with pytest.raises(Exception):
            await asyncio.wait_for(master_conn.send(b'hi'), 1)
        await asyncio.wait_for(master_conn.wait_closed(), 1)
        assert link.is_open

    with pytest.raises(Exception):
        await master_conn.send(b'hi')
    with pytest.raises(Exception):
        await master_conn.receive()
