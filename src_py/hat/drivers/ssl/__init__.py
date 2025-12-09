from ssl import *  # NOQA

from collections.abc import Callable
import enum
import pathlib
import ssl
import typing

try:
    from hat.drivers.ssl import _ssl

except ImportError:
    _ssl = None


OP_ALLOW_CLIENT_RENEGOTIATION = (1 << 8)


class SslProtocol(enum.Enum):
    TLS_CLIENT = ssl.PROTOCOL_TLS_CLIENT
    TLS_SERVER = ssl.PROTOCOL_TLS_SERVER


class KeyUpdateType(enum.Enum):
    UPDATE_NOT_REQUESTED = 0
    UPDATE_REQUESTED = 1


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


def key_update(ssl_object: ssl.SSLObject | ssl.SSLSocket,
               update_type: KeyUpdateType):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, (ssl.SSLObject, ssl.SSLSocket)):
        raise TypeError('invalid ssl object')

    result = _ssl.key_update(ssl_object._sslobj, update_type.value)
    if result != 1:
        raise Exception('key update error')


def renegotiate(ssl_object: ssl.SSLObject | ssl.SSLSocket):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, (ssl.SSLObject, ssl.SSLSocket)):
        raise TypeError('invalid ssl object')

    result = _ssl.renegotiate(ssl_object._sslobj)
    if result != 1:
        raise Exception('renegotiate error')


def get_peer_cert(ssl_object: ssl.SSLObject | ssl.SSLSocket
                  ) -> typing.Optional['Cert']:
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, (ssl.SSLObject, ssl.SSLSocket)):
        raise TypeError('invalid ssl object')

    handle = _ssl.get_peer_cert(ssl_object._sslobj)
    if not handle:
        return

    return Cert(handle)


def set_handshake_start_cb(ssl_object: ssl.SSLObject | ssl.SSLSocket,
                           cb: Callable[[], None]):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, (ssl.SSLObject, ssl.SSLSocket)):
        raise TypeError('invalid ssl object')

    if not callable(cb) and cb is not None:
        raise TypeError('invalid callback')

    _ssl.set_handshake_start_cb(ssl_object._sslobj, cb)


def set_handshake_done_cb(ssl_object: ssl.SSLObject | ssl.SSLSocket,
                          cb: Callable[[], None]):
    if not _ssl:
        raise Exception('not supported')

    if not isinstance(ssl_object, (ssl.SSLObject, ssl.SSLSocket)):
        raise TypeError('invalid ssl object')

    if not callable(cb) and cb is not None:
        raise TypeError('invalid callback')

    _ssl.set_handshake_done_cb(ssl_object._sslobj, cb)


def load_crl(path: pathlib.PurePath) -> 'Crl':
    if not _ssl:
        raise Exception('not supported')

    handle = _ssl.load_crl(str(path))
    return Crl(handle)


class Cert:

    def __init__(self, handle):
        self._handle = handle

    def get_pub_key(self) -> 'PubKey':
        handle = _ssl.get_cert_pub_key(self._handle)
        return PubKey(handle)

    def get_bytes(self) -> bytes:
        return _ssl.get_cert_bytes(self._handle)


class PubKey:

    def __init__(self, handle):
        self._handle = handle

    def is_rsa(self) -> bool:
        return _ssl.is_pub_key_rsa(self._handle)

    def get_size(self) -> int:
        return _ssl.get_pub_key_size(self._handle)


class Crl:

    def __init__(self, handle):
        self._handle = handle

    def __eq__(self, other):
        if not isinstance(other, Crl):
            return False

        return _ssl.crl_equal(self._handle, other._handle)

    def contains_cert(self, cert: Cert) -> bool:
        if not isinstance(cert, Cert):
            raise TypeError('invalid cert')

        return _ssl.crl_contains_cert(self._handle, cert._handle)
