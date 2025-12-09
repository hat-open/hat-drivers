from pathlib import Path
from pprint import pprint
import asyncio
import contextlib
import subprocess
import tempfile

from hat import aio

from hat.drivers import ssl
from hat.drivers import tcp


def main():
    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main())


async def async_main():
    addr = tcp.Address('127.0.0.1', 1234)
    ctx = create_ctx()
    srv = await tcp.listen(on_connection, addr,
                           ssl=ctx,
                           bind_connections=True)

    try:
        await srv.wait_closing()

    finally:
        await aio.uncancellable(srv.async_close())


def create_ctx():
    with tempfile.TemporaryDirectory() as dir_path:
        cert_path = Path(dir_path) / 'pem'
        subprocess.run(['openssl', 'req', '-batch', '-x509', '-noenc',
                        '-newkey', 'rsa:2048',
                        '-days', '1',
                        '-keyout', str(cert_path),
                        '-out', str(cert_path)],
                       stderr=subprocess.DEVNULL,
                       check=True)
        ctx = ssl.create_ssl_ctx(ssl.SslProtocol.TLS_SERVER,
                                 cert_path=cert_path)
        ctx.options |= ssl.OP_ALLOW_CLIENT_RENEGOTIATION

        return ctx


async def on_connection(conn):
    print(">> cipher")
    pprint(conn.ssl_object.cipher())

    print(">> peer cert")
    pprint(conn.ssl_object.getpeercert())

    print(">> alpn protocol")
    pprint(conn.ssl_object.selected_alpn_protocol())

    print(">> shared ciphers")
    pprint(conn.ssl_object.shared_ciphers())

    await conn.wait_closing()


if __name__ == '__main__':
    main()
