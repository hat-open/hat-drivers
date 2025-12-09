from pathlib import Path
import asyncio
import contextlib
import logging

from hat import aio

from hat.drivers import ssl
from hat.drivers import tcp


mlog: logging.Logger = logging.getLogger(__name__)


def create_ssl_ctx(protocol: ssl.SslProtocol,
                   *,
                   verify_cert: bool = False,
                   cert_path: Path | None = None,
                   key_path: Path | None = None,
                   ca_path: Path | None = None,
                   password: str | None = None,
                   maximum_version: ssl.TLSVersion = ssl.TLSVersion.TLSv1_3
                   ) -> ssl.SSLContext:
    ctx = ssl.create_ssl_ctx(protocol=protocol,
                             check_hostname=False,
                             verify_cert=verify_cert,
                             load_default_certs=False,
                             cert_path=cert_path,
                             key_path=key_path,
                             ca_path=ca_path,
                             password=password)

    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.maximum_version = maximum_version

    ctx.set_ciphers('TLS_RSA_WITH_AES_128_GCM_SHA256:'
                    'TLS_DHE_RSA_WITH_AES_128_GCM_SHA256:'
                    'TLS_DHE_RSA_WITH_AES_256_GCM_SHA384:'
                    'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256:'
                    'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384:'
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256:'
                    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384:'
                    'TLS_AES_128_GCM_SHA256:'
                    'TLS_AES_256_GCM_SHA384:'
                    'TLS_CHACHA20_POLY1305_SHA256:'
                    'TLS_AES_128_CCM_SHA256:'
                    'TLS_AES_128_CCM_8_SHA256')

    ctx.options |= ssl.OP_ALLOW_CLIENT_RENEGOTIATION

    return ctx


async def attach_validator(conn: tcp.Connection,
                           renegotiate_delay: float | None = None,
                           crl_path: Path | None = None,
                           reload_crl_delay: float | None = None):
    validator = _Validator()
    validator._conn = conn
    validator._executor = aio.Executor()
    validator._handshake_start_event = aio.Event()
    validator._handshake_done_event = aio.Event()
    validator._renegotiate_event = aio.Event()
    validator._version = None
    validator._crl = None

    _bind_resource(conn.async_group, validator)

    try:
        validator._check_version()

        validator._check_cert()
        validator.async_group.spawn(validator._validate_loop)

        if crl_path is not None:
            validator._crl = await validator._executor.spawn(_ext_load_crl,
                                                             crl_path)
            validator._check_crl()

            if reload_crl_delay:
                validator.async_group.spawn(validator._reload_crl_loop,
                                            crl_path, reload_crl_delay)

        if renegotiate_delay:
            validator.async_group.spawn(validator._schedule_renegotiate_loop,
                                        renegotiate_delay)

        validator.async_group.spawn(validator._renegotiate_loop)

        validator.async_group.spawn(aio.call_on_cancel,
                                    ssl.set_handshake_start_cb,
                                    conn.ssl_object, None)
        ssl.set_handshake_start_cb(conn.ssl_object,
                                   validator._handshake_start_event.set)

        validator.async_group.spawn(aio.call_on_cancel,
                                    ssl.set_handshake_done_cb,
                                    conn.ssl_object, None)
        ssl.set_handshake_done_cb(conn.ssl_object,
                                  validator._handshake_done_event.set)

    except BaseException:
        await aio.uncancellable(validator.async_close())
        raise


class _Validator(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._executor.async_group

    async def _reload_crl_loop(self, path, delay):
        try:
            while True:
                await asyncio.sleep(delay)

                crl = await self._executor.spawn(_ext_load_crl, path)
                if self._crl == crl:
                    continue

                self._crl = crl
                self._renegotiate_event.set()
                self._check_crl()

        except Exception as e:
            mlog.error("reload crl loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _schedule_renegotiate_loop(self, delay):
        try:
            while True:
                self._handshake_start_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._handshake_start_event.wait(),
                                       delay)
                    continue

                self._renegotiate_event.set()

        except Exception as e:
            mlog.error("schedule renegotiate loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _renegotiate_loop(self):
        try:
            while True:
                await self._renegotiate_event.wait()
                self._renegotiate_event.clear()

                if self._conn.ssl_object.version() == 'TLSv1.3':
                    ssl.key_update(self._conn.ssl_object,
                                   ssl.KeyUpdateType.UPDATE_REQUESTED)

                else:
                    ssl.renegotiate(self._conn.ssl_object)

                await _do_handshake(self._conn)

        except Exception as e:
            mlog.error("schedule renegotiate loop error: %s", e, exc_info=e)

        finally:
            self.close()

    async def _validate_loop(self):
        try:
            while True:
                await self._handshake_done_event.wait()
                self._handshake_done_event.clear()

                self._check_version()
                self._check_cert()
                self._check_crl()

        except Exception as e:
            mlog.error("validate loop error: %s", e, exc_info=e)

        finally:
            self.close()

    def _check_version(self):
        version = self._conn.ssl_object.version()

        if self._version is not None and self._version != version:
            mlog.warning('TLS version change')

        self._version = version

    def _check_cert(self):
        cert = _get_peer_cert(self._conn)

        cert_bytes = cert.get_bytes()
        if len(cert_bytes) > 8192:
            mlog.warning('TLS certificate size exceeded')

        key = cert.get_pub_pkey()

        if key.is_rsa():
            key_size = key.get_size()

            if key_size < 2048:
                raise Exception('insufficient RSA key length')

            if key_size > 8192:
                mlog.warning('RSA key length greater than 8192')

    def _check_crl(self):
        if self._crl is None:
            return

        cert = _get_peer_cert(self._conn)

        if self._crl.contains_cert(cert):
            raise Exception('certificate in CRL')


def _bind_resource(async_group, resource):
    async_group.spawn(aio.call_on_cancel, resource.async_close)
    async_group.spawn(aio.call_on_done, resource.wait_closing(),
                      async_group.close)


async def _do_handshake(conn):
    while True:
        try:
            conn.ssl_object.do_handshake()
            break

        except ssl.SSLWantReadError:
            conn._protocol._transport._ssl_protocol._do_read()
            await asyncio.sleep(0.005)


def _ext_load_crl(path: Path) -> ssl.Crl | None:
    try:
        return ssl.load_crl(path)

    except Exception as e:
        mlog.error("error loading CRL: %s", e, exc_info=e)


def _get_peer_cert(conn):
    cert = ssl.get_peer_cert(conn.ssl_object)
    if not cert:
        raise Exception('peer cert not available')

    return cert
