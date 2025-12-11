from pathlib import Path
import argparse
import asyncio
import contextlib
import logging.config

from hat import aio

from hat.drivers import iec62351
from hat.drivers import ssl
from hat.drivers import tcp


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=1234)
    parser.add_argument('--strict-mode', action='store_true')
    parser.add_argument('--cert', type=Path, default=None)
    parser.add_argument('--key', type=Path, default=None)
    parser.add_argument('--ca', type=Path, default=None)
    parser.add_argument('--password', default=None)
    parser.add_argument('--maximum-version', default='TLSv1_3')
    parser.add_argument('--renegotiate-delay', type=float, default=None)
    parser.add_argument('--crl', type=Path, default=None)
    parser.add_argument('--reload-crl-delay', type=float, default=None)
    parser.add_argument('--handshake-timeout', type=float, default=5)
    parser.add_argument('--log-level', default='DEBUG')
    parser.add_argument('action', choices=['client', 'server'])
    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'console_formater': {
                'format': '[%(asctime)s %(levelname)s %(name)s] %(message)s'}},
        'handlers': {
            'console_handler': {
                'class': 'logging.StreamHandler',
                'formatter': 'console_formater',
                'level': args.log_level}},
        'root': {
            'level': args.log_level,
            'handlers': ['console_handler']},
        'disable_existing_loggers': False})

    addr = tcp.Address(args.host, args.port)
    maximum_version = ssl.TLSVersion[args.maximum_version]

    if args.action == 'client':
        protocol = ssl.SslProtocol.TLS_CLIENT
        main_cb = client_main

    elif args.action == 'server':
        protocol = ssl.SslProtocol.TLS_SERVER
        main_cb = server_main

    else:
        raise ValueError('unsupported action')

    ctx = iec62351.Context(protocol=protocol,
                           strict_mode=args.strict_mode,
                           cert_path=args.cert,
                           key_path=args.key,
                           ca_path=args.ca,
                           password=args.password,
                           maximum_version=maximum_version,
                           renegotiate_delay=args.renegotiate_delay,
                           crl_path=args.crl,
                           reload_crl_delay=args.reload_crl_delay,
                           handshake_timeout=args.handshake_timeout)

    aio.init_asyncio()

    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(main_cb(addr=addr,
                                ctx=ctx))


async def server_main(addr, ctx):
    async def on_connection(conn):
        await ctx.register(conn)

    srv = await tcp.listen(connection_cb=on_connection,
                           addr=addr,
                           ssl=ctx.ssl_ctx,
                           bind_connections=True)

    try:
        await srv.wait_closing()

    finally:
        await aio.uncancellable(srv.async_close())


async def client_main(addr, ctx):
    conn = await tcp.connect(addr=addr,
                             ssl=ctx.ssl_ctx)

    try:
        await ctx.register(conn)

        await conn.wait_closing()

    finally:
        await aio.uncancellable(conn.async_close())


if __name__ == '__main__':
    main()
