import asyncio
import pytest
import socket

from hat import aio

from hat.drivers import icmp
from hat.drivers.icmp import common
from hat.drivers.icmp import encoder


def has_permission():
    try:
        s = socket.socket(family=socket.AF_INET,
                          type=socket.SOCK_DGRAM,
                          proto=socket.IPPROTO_ICMP)
        s.close()

    except PermissionError:
        return False

    return True


pytestmark = pytest.mark.skipif(not has_permission(),
                                reason="insufficient permissions")

# according to rfc5737, this ip is provided for use only in documentation
unused_local_ip = '192.0.2.0'


async def test_create_endpoint():
    endpoint = await icmp.create_endpoint()

    assert isinstance(endpoint, icmp.Endpoint)
    assert endpoint.is_open

    endpoint.close()
    await endpoint.wait_closing()
    assert endpoint.is_closing
    await endpoint.wait_closed()
    assert endpoint.is_closed


async def test_create_endpoint_fail():
    with pytest.raises(Exception):
        await icmp.create_endpoint(unused_local_ip)


async def test_ping_localhost():
    endpoint = await icmp.create_endpoint()

    await endpoint.ping('127.0.0.1')

    await endpoint.async_close()


async def test_ping_failure():
    endpoint = await icmp.create_endpoint()

    with pytest.raises(asyncio.TimeoutError):
        await aio.wait_for(endpoint.ping(unused_local_ip), timeout=0.05)

    await endpoint.async_close()


async def test_ping_closed_endoint():
    endpoint = await icmp.create_endpoint()

    endpoint.close()

    with pytest.raises(ConnectionError):
        await endpoint.ping('127.0.0.1')

    await endpoint.wait_closed()


@pytest.mark.parametrize('is_reply', [True, False])
@pytest.mark.parametrize('identifier', [0, 123])
@pytest.mark.parametrize('sequence_number', [456, 789])
@pytest.mark.parametrize('data_bytes', [b'', b'some data goes here'])
def test_encode_decode(is_reply, identifier, sequence_number, data_bytes):
    msg = common.EchoMsg(
        is_reply=is_reply,
        identifier=identifier,
        sequence_number=sequence_number,
        data=data_bytes)

    msg_encoded = encoder.encode_msg(msg)
    msg_decoded = encoder.decode_msg(msg_encoded)

    assert msg == msg_decoded


def test_decode_checksum():
    msg = common.EchoMsg(
        is_reply=False,
        identifier=1,
        sequence_number=2,
        data=b'')

    msg_encoded = encoder.encode_msg(msg)
    msg_corrupt = msg_encoded
    msg_corrupt[-1] = (msg_corrupt[-1] + 1) % 0x100

    with pytest.raises(Exception, match='invalid checksum'):
        encoder.decode_msg(msg_corrupt)


def test_decode_invalid_msg_type():
    msg = common.EchoMsg(
        is_reply=False,
        identifier=1,
        sequence_number=2,
        data=b'')

    msg_encoded = encoder.encode_msg(msg)
    msg_corrupt = msg_encoded
    msg_corrupt[0] = 123

    with pytest.raises(Exception, match='unsupported message type'):
        encoder.decode_msg(msg_corrupt)
