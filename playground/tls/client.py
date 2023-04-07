from pprint import pprint
import asyncio
import contextlib

import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.hazmat.primitives.serialization
import cryptography.x509

from hat import aio

from hat.drivers import ssl
from hat.drivers import tcp


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    addr = tcp.Address('127.0.0.1', 1234)
    ctx = ssl.create_ssl_ctx(ssl.SslProtocol.TLS_CLIENT)
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    conn = await tcp.connect(addr, ssl=ctx)

    print(">> cert store stats")
    pprint(ctx.cert_store_stats())

    try:
        while True:
            print(">> version")
            pprint(conn.ssl_object.version())

            print(">> cipher")
            pprint(conn.ssl_object.cipher())

            print(">> peer cert")
            pprint(conn.ssl_object.getpeercert())

            cert_bytes = conn.ssl_object.getpeercert(True)
            cert = cryptography.x509.load_der_x509_certificate(cert_bytes)
            key = cert.public_key()

            print(">> key")
            key_pem = key.public_bytes(
                encoding=cryptography.hazmat.primitives.serialization.Encoding.PEM,  # NOQA
                format=cryptography.hazmat.primitives.serialization.PublicFormat.SubjectPublicKeyInfo)  # NOQA
            pprint(key_pem)

            if isinstance(key, cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey):  # NOQA
                print(">> rsa key length")
                pprint(key.key_size)

            await asyncio.sleep(5)

            if conn.ssl_object.version() == 'TLSv1.3':
                ssl.key_update(conn.ssl_object,
                               ssl.KeyUpdateType.UPDATE_REQUESTED)
            else:
                ssl.renegotiate(conn.ssl_object)

            conn.ssl_object.do_handshake()

            conn.write(b'123')

    finally:
        await aio.uncancellable(conn.async_close())


if __name__ == '__main__':
    main()
