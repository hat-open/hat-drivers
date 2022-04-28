from hat import aio

from hat.drivers import udp
from hat.drivers.snmp import common
from hat.drivers.snmp import encoder


def main():
    aio.init_asyncio()
    aio.run_asyncio(async_main())


async def async_main():

    data = common.Data(type=common.DataType.EMPTY,
                       name=(1, 3, 6, 1, 2, 1, 2, 1, 0),
                       value=None)
    pdu = encoder.v1.BasicPdu(
        request_id=123,
        error=common.Error(type=common.ErrorType.NO_ERROR,
                           index=0),
        data=[data])
    msg = encoder.v1.Msg(type=encoder.v1.MsgType.GET_REQUEST,
                         community="xyz",
                         pdu=pdu)

    endpoint = await udp.create(local_addr=None,
                                remote_addr=('127.0.0.1', 161))

    req_msg_bytes = encoder.encode(msg)

    endpoint.send(req_msg_bytes)

    msg_bytes, addr = await endpoint.receive()

    msg = encoder.decode(msg_bytes)

    print('>>', msg)

    await endpoint.async_close()


if __name__ == '__main__':
    main()
