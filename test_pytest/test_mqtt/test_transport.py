import pytest

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.mqtt import common
from hat.drivers.mqtt import transport


packets = [
    transport.ConnectPacket(
        clean_start=True,
        keep_alive=0,
        session_expiry_interval=0,
        receive_maximum=0xffff,
        maximum_packet_size=None,
        topic_alias_maximum=0,
        request_response_information=True,
        request_problem_information=True,
        user_properties=[],
        authentication_method=None,
        authentication_data=None,
        client_identifier='',
        will=None,
        user_name=None,
        password=None),

    transport.ConnectPacket(
        clean_start=False,
        keep_alive=123,
        session_expiry_interval=321,
        receive_maximum=42,
        maximum_packet_size=24,
        topic_alias_maximum=1,
        request_response_information=False,
        request_problem_information=False,
        user_properties=[('abc', '123'), ('123', 'abc')],
        authentication_method='xyz',
        authentication_data=b'zyx',
        client_identifier='client',
        will=transport.Will(
            qos=common.QoS.AT_LEAST_ONCE,
            retain=True,
            delay_interval=0,
            message_expiry_interval=None,
            content_type=None,
            response_topic=None,
            correlation_data=None,
            user_properties=[],
            topic='a/b/c',
            payload=''),
        user_name='user',
        password=b'pass'),

    transport.ConnAckPacket(
        session_present=False,
        reason=common.Reason.SUCCESS,
        session_expiry_interval=None,
        receive_maximum=0xffff,
        maximum_qos=common.QoS.EXACLTY_ONCE,
        retain_available=True,
        maximum_packet_size=None,
        assigned_client_identifier=None,
        topic_alias_maximum=0xffff,
        reason_string=None,
        user_properties=[],
        wildcard_subscription_available=True,
        subscription_identifier_available=True,
        shared_subscription_available=True,
        server_keep_alive=None,
        response_information=None,
        server_reference=None,
        authentication_method=None,
        authentication_data=None),
]


def assert_packet_equal(packet1, packet2):
    for attr in ['user_properties', 'subscription_identifiers']:
        if hasattr(packet1, attr):
            assert list(getattr(packet1, attr)) == list(getattr(packet2, attr))

            packet1 = packet1._replace(**{attr: []})
            packet2 = packet2._replace(**{attr: []})

    if hasattr(packet1, 'will'):
        if packet1.will or packet2.will:
            assert_packet_equal(packet1.will, packet2.will)

            packet1 = packet1._replace(will=None)
            packet2 = packet2._replace(will=None)

    packet1 == packet2


@pytest.fixture
def addr():
    return tcp.Address('127.0.0.1', util.get_unused_tcp_port())


@pytest.mark.parametrize('packet', packets)
def test_encode_decode(packet):
    encoded_packet = transport.encode_packet(packet)

    packet_size = transport.get_next_packet_size(encoded_packet)
    assert packet_size == len(encoded_packet)

    decoded_packet = transport.decode_packet(encoded_packet)
    assert_packet_equal(decoded_packet, packet)


@pytest.mark.parametrize('packet', packets)
async def test_send_receive(addr, packet):
    conn_queue = aio.Queue()

    srv = await transport.listen(conn_queue.put_nowait, addr)
    conn1 = await transport.connect(addr)
    conn2 = await conn_queue.get()

    await conn1.send(packet)
    received_packet = await conn2.receive()
    assert_packet_equal(packet, received_packet)

    await conn2.send(packet)
    received_packet = await conn1.receive()
    assert_packet_equal(packet, received_packet)

    await conn1.async_close()
    await conn2.async_close()
    await srv.async_close()
