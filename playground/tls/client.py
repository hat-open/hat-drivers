from pprint import pprint
import asyncio
import contextlib

from hat import aio

from hat.drivers import tcp


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    addr = tcp.Address('127.0.0.1', 1234)
    ctx = tcp.create_ssl_ctx(tcp.SslProtocol.TLS_CLIENT)
    conn = await tcp.connect(addr, ssl=ctx)

    print(">> cert store stats")
    pprint(ctx.cert_store_stats())

    try:
        while True:
            print(">> cipher")
            pprint(conn.ssl_object.cipher())

            print(">> peer cert")
            pprint(conn.ssl_object.getpeercert())

            print(">> alpn protocol")
            pprint(conn.ssl_object.selected_alpn_protocol())

            print(">> shared ciphers")
            pprint(conn.ssl_object.shared_ciphers())

            await asyncio.sleep(5)

            conn.ssl_object.do_handshake()

    finally:
        await aio.uncancellable(conn.async_close())


if __name__ == '__main__':
    main()
