from pprint import pprint
import asyncio
import contextlib

import cryptography.x509
import cryptography.hazmat.primitives.asymmetric.rsa

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
        print(">> cipher")
        pprint(conn.ssl_object.cipher())

        print(">> peer cert")
        pprint(conn.ssl_object.getpeercert())

        cert_bytes = conn.ssl_object.getpeercert(True)
        cert = cryptography.x509.load_der_x509_certificate(cert_bytes)
        key = cert.public_key()

        print(">> key")
        pprint(key)

        if isinstance(key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey):  # NOQA
            print(">> rsa key length")
            pprint(key.key_size)

    finally:
        await aio.uncancellable(conn.async_close())


if __name__ == '__main__':
    main()
