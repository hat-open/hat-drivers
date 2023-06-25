from ssl import *  # NOQA

import enum
import pathlib
import ssl

try:
    from hat.drivers.ssl import _ssl

except ImportError:
    _ssl = None


class SslProtocol(enum.Enum):
    TLS_CLIENT = ssl.PROTOCOL_TLS_CLIENT
    TLS_SERVER = ssl.PROTOCOL_TLS_SERVER


class KeyUpdateType(enum.Enum):
    UPDATE_NOT_REQUESTED = 0
    UPDATE_REQUESTED = 1


def create_ssl_ctx(protocol: SslProtocol,
                   verify_cert: bool = False,
                   cert_path: pathlib.PurePath | None = None,
                   key_path: pathlib.PurePath | None = None,
                   ca_path: pathlib.PurePath | None = None,
                   password: str | None = None
                   ) -> ssl.SSLContext:
    ctx = ssl.SSLContext(protocol.value)
    ctx.check_hostname = False

    if verify_cert:
        ctx.verify_mode = ssl.VerifyMode.CERT_REQUIRED
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


def key_update(ssl_object: ssl.SSLObject,
               update_type: KeyUpdateType):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, ssl.SSLObject):
        raise TypeError('invalid ssl object')

    result = _ssl.key_update(ssl_object._sslobj, update_type.value)
    if result != 1:
        raise Exception('key update error')


def renegotiate(ssl_object: ssl.SSLObject):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, ssl.SSLObject):
        raise TypeError('invalid ssl object')

    result = _ssl.renegotiate(ssl_object._sslobj)
    if result != 1:
        raise Exception('renegotiate error')
