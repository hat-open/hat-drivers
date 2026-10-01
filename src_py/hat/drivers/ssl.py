from ssl import *  # NOQA

import enum
import pathlib
import ssl


class SslProtocol(enum.Enum):
    TLS_CLIENT = ssl.PROTOCOL_TLS_CLIENT
    TLS_SERVER = ssl.PROTOCOL_TLS_SERVER


def create_ssl_ctx(protocol: SslProtocol,
                   *,
                   check_hostname: bool = False,
                   verify_cert: bool = False,
                   load_default_certs: bool = True,
                   cert_path: pathlib.PurePath | None = None,
                   key_path: pathlib.PurePath | None = None,
                   ca_path: pathlib.PurePath | None = None,
                   password: str | None = None
                   ) -> ssl.SSLContext:
    ctx = ssl.SSLContext(protocol.value)
    ctx.check_hostname = check_hostname

    if verify_cert:
        ctx.verify_mode = ssl.VerifyMode.CERT_REQUIRED

        if load_default_certs:
            ctx.load_default_certs(ssl.Purpose.CLIENT_AUTH
                                   if protocol == SslProtocol.TLS_SERVER
                                   else ssl.Purpose.SERVER_AUTH)

        if ca_path:
            ctx.load_verify_locations(cafile=str(ca_path))

    else:
        ctx.verify_mode = ssl.VerifyMode.CERT_NONE

    if cert_path:
        ctx.load_cert_chain(certfile=str(cert_path),
                            keyfile=str(key_path) if key_path else None,
                            password=password)

    return ctx
