"""Association Controll Service Element"""

import asyncio
import importlib.resources
import logging
import typing

from hat import aio
from hat import asn1

from hat.drivers import copp
from hat.drivers import tcp


mlog = logging.getLogger(__name__)

# (joint-iso-itu-t, association-control, abstract-syntax, apdus, version1)
_acse_syntax_name = (2, 2, 1, 0, 1)

with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'asn1_repo.json') as _path:
    _encoder = asn1.Encoder(asn1.Encoding.BER,
                            asn1.Repository.from_json(_path))


class ConnectionInfo(typing.NamedTuple):
    local_addr: tcp.Address
    local_tsel: int | None
    local_ssel: int | None
    local_psel: int | None
    local_ap_title: asn1.ObjectIdentifier | None
    local_ae_qualifier: int | None
    remote_addr: tcp.Address
    remote_tsel: int | None
    remote_ssel: int | None
    remote_psel: int | None
    remote_ap_title: asn1.ObjectIdentifier | None
    remote_ae_qualifier: int | None


ValidateCb: typing.TypeAlias = aio.AsyncCallable[[copp.SyntaxNames,
                                                  copp.IdentifiedEntity],
                                                 copp.IdentifiedEntity | None]
"""Validate callback"""

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


async def connect(addr: tcp.Address,
                  syntax_name_list: list[asn1.ObjectIdentifier],
                  app_context_name: asn1.ObjectIdentifier,
                  user_data: copp.IdentifiedEntity | None = None,
                  *,
                  local_ap_title: asn1.ObjectIdentifier | None = None,
                  remote_ap_title: asn1.ObjectIdentifier | None = None,
                  local_ae_qualifier: int | None = None,
                  remote_ae_qualifier: int | None = None,
                  acse_receive_queue_size: int = 1024,
                  acse_send_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Connect to ACSE server

    Additional arguments are passed directly to `hat.drivers.copp.connect`
    (`syntax_names` is set by this coroutine).

    """
    syntax_names = copp.SyntaxNames([_acse_syntax_name, *syntax_name_list])
    aarq_apdu = _aarq_apdu(syntax_names, app_context_name,
                           local_ap_title, remote_ap_title,
                           local_ae_qualifier, remote_ae_qualifier,
                           user_data)
    copp_user_data = _acse_syntax_name, _encode(aarq_apdu)
    conn = await copp.connect(addr, syntax_names, copp_user_data, **kwargs)

    try:
        aare_apdu_syntax_name, aare_apdu_entity = conn.conn_res_user_data
        if aare_apdu_syntax_name != _acse_syntax_name:
            raise Exception("invalid syntax name")

        aare_apdu = _decode(aare_apdu_entity)
        if aare_apdu[0] != 'aare' or aare_apdu[1]['result'] != 0:
            raise Exception("invalid apdu")

        calling_ap_title, called_ap_title = _get_ap_titles(aarq_apdu)
        calling_ae_qualifier, called_ae_qualifier = _get_ae_qualifiers(
            aarq_apdu)
        return Connection(conn, aarq_apdu, aare_apdu,
                          calling_ap_title, called_ap_title,
                          calling_ae_qualifier, called_ae_qualifier,
                          acse_receive_queue_size, acse_send_queue_size)

    except Exception:
        await aio.uncancellable(_close_copp(conn, _abrt_apdu(1)))
        raise


async def listen(validate_cb: ValidateCb,
                 connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 *,
                 bind_connections: bool = False,
                 acse_receive_queue_size: int = 1024,
                 acse_send_queue_size: int = 1024,
                 **kwargs
                 ) -> 'Server':
    """Create ACSE listening server

    Additional arguments are passed directly to `hat.drivers.copp.listen`.

    Args:
        validate_cb: callback function or coroutine called on new
            incomming connection request prior to creating connection object
        connection_cb: new connection callback
        addr: local listening address

    """
    server = Server()
    server._validate_cb = validate_cb
    server._connection_cb = connection_cb
    server._bind_connections = bind_connections
    server._receive_queue_size = acse_receive_queue_size
    server._send_queue_size = acse_send_queue_size

    server._srv = await copp.listen(server._on_validate,
                                    server._on_connection,
                                    addr,
                                    bind_connections=False,
                                    **kwargs)

    return server


class Server(aio.Resource):
    """ACSE listening server

    For creating new server see `listen`.

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._srv.async_group

    @property
    def addresses(self) -> list[tcp.Address]:
        """Listening addresses"""
        return self._srv.addresses

    async def _on_validate(self, syntax_names, user_data):
        aarq_apdu_syntax_name, aarq_apdu_entity = user_data
        if aarq_apdu_syntax_name != _acse_syntax_name:
            raise Exception('invalid acse syntax name')

        aarq_apdu = _decode(aarq_apdu_entity)
        if aarq_apdu[0] != 'aarq':
            raise Exception('not aarq message')

        aarq_external = aarq_apdu[1]['user-information'][0]
        if aarq_external.direct_ref is not None:
            if aarq_external.direct_ref != _encoder.syntax_name:
                raise Exception('invalid encoder identifier')

        _, called_ap_title = _get_ap_titles(aarq_apdu)
        _, called_ae_qualifier = _get_ae_qualifiers(aarq_apdu)
        _, called_ap_invocation_identifier = \
            _get_ap_invocation_identifiers(aarq_apdu)
        _, called_ae_invocation_identifier = \
            _get_ae_invocation_identifiers(aarq_apdu)

        aarq_user_data = (syntax_names.get_name(aarq_external.indirect_ref),
                          aarq_external.data)

        user_validate_result = await aio.call(self._validate_cb, syntax_names,
                                              aarq_user_data)

        aare_apdu = _aare_apdu(syntax_names,
                               user_validate_result,
                               called_ap_title, called_ae_qualifier,
                               called_ap_invocation_identifier,
                               called_ae_invocation_identifier)
        return _acse_syntax_name, _encode(aare_apdu)

    async def _on_connection(self, copp_conn):
        try:
            try:
                aarq_apdu = _decode(copp_conn.conn_req_user_data[1])
                aare_apdu = _decode(copp_conn.conn_res_user_data[1])

                calling_ap_title, called_ap_title = _get_ap_titles(aarq_apdu)
                calling_ae_qualifier, called_ae_qualifier = _get_ae_qualifiers(
                    aarq_apdu)

                conn = Connection(copp_conn, aarq_apdu, aare_apdu,
                                  calling_ap_title, called_ap_title,
                                  calling_ae_qualifier, called_ae_qualifier,
                                  self._receive_queue_size,
                                  self._send_queue_size)

            except Exception:
                await aio.uncancellable(_close_copp(copp_conn, _abrt_apdu(1)))
                raise

            try:
                await aio.call(self._connection_cb, conn)

            except BaseException:
                await aio.uncancellable(conn.async_close())
                raise

        except Exception as e:
            mlog.error("error creating new incomming connection: %s", e,
                       exc_info=e)
            return

        if not self._bind_connections:
            return

        try:
            await conn.wait_closed()

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise


class Connection(aio.Resource):
    """ACSE connection

    For creating new connection see `connect` or `listen`.

    """

    def __init__(self,
                 conn: copp.Connection,
                 aarq_apdu: asn1.Value,
                 aare_apdu: asn1.Value,
                 local_ap_title: asn1.ObjectIdentifier | None,
                 remote_ap_title: asn1.ObjectIdentifier | None,
                 local_ae_qualifier: int | None,
                 remote_ae_qualifier: int | None,
                 receive_queue_size: int,
                 send_queue_size: int):
        aarq_external = aarq_apdu[1]['user-information'][0]
        aare_external = aare_apdu[1]['user-information'][0]

        conn_req_user_data = (
            conn.syntax_names.get_name(aarq_external.indirect_ref),
            aarq_external.data)
        conn_res_user_data = (
            conn.syntax_names.get_name(aare_external.indirect_ref),
            aare_external.data)

        self._conn = conn
        self._conn_req_user_data = conn_req_user_data
        self._conn_res_user_data = conn_res_user_data
        self._loop = asyncio.get_running_loop()
        self._info = ConnectionInfo(local_ap_title=local_ap_title,
                                    local_ae_qualifier=local_ae_qualifier,
                                    remote_ap_title=remote_ap_title,
                                    remote_ae_qualifier=remote_ae_qualifier,
                                    **conn.info._asdict())
        self._close_apdu = _abrt_apdu(0)
        self._receive_queue = aio.Queue(receive_queue_size)
        self._send_queue = aio.Queue(send_queue_size)
        self._async_group = aio.Group()

        self.async_group.spawn(aio.call_on_cancel, self._on_close)
        self.async_group.spawn(self._receive_loop)
        self.async_group.spawn(self._send_loop)
        self.async_group.spawn(aio.call_on_done, conn.wait_closing(),
                               self.close)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> ConnectionInfo:
        """Connection info"""
        return self._info

    @property
    def conn_req_user_data(self) -> copp.IdentifiedEntity:
        """Connect request's user data"""
        return self._conn_req_user_data

    @property
    def conn_res_user_data(self) -> copp.IdentifiedEntity:
        """Connect response's user data"""
        return self._conn_res_user_data

    async def receive(self) -> copp.IdentifiedEntity:
        """Receive data"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self, data: copp.IdentifiedEntity):
        """Send data"""
        try:
            await self._send_queue.put((data, None))

        except aio.QueueClosedError:
            raise ConnectionError()

    async def drain(self):
        """Drain output buffer"""
        try:
            future = self._loop.create_future()
            await self._send_queue.put((None, future))
            await future

        except aio.QueueClosedError:
            raise ConnectionError()

    async def _on_close(self):
        await _close_copp(self._conn, self._close_apdu)

    def _close(self, apdu):
        if not self.is_open:
            return

        self._close_apdu = apdu
        self._async_group.close()

    async def _receive_loop(self):
        try:
            while True:
                syntax_name, entity = await self._conn.receive()

                if syntax_name == _acse_syntax_name:
                    if entity[0] == 'abrt':
                        close_apdu = None

                    elif entity[0] == 'rlrq':
                        close_apdu = _rlre_apdu()

                    else:
                        close_apdu = _abrt_apdu(1)

                    self._close(close_apdu)
                    break

                await self._receive_queue.put((syntax_name, entity))

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self._close(_abrt_apdu(1))
            self._receive_queue.close()

    async def _send_loop(self):
        future = None
        try:
            while True:
                data, future = await self._send_queue.get()

                if data is None:
                    await self._conn.drain()

                else:
                    await self._conn.send(data)

                if future and not future.done():
                    future.set_result(None)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self._close(_abrt_apdu(1))
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_result(None)
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()


async def _close_copp(copp_conn, apdu):
    data = (_acse_syntax_name, _encode(apdu)) if apdu else None
    await copp_conn.async_close(data)


def _get_ap_titles(aarq_apdu):
    calling = None
    if 'calling-AP-title' in aarq_apdu[1]:
        if aarq_apdu[1]['calling-AP-title'][0] == 'ap-title-form2':
            calling = aarq_apdu[1]['calling-AP-title'][1]

    called = None
    if 'called-AP-title' in aarq_apdu[1]:
        if aarq_apdu[1]['called-AP-title'][0] == 'ap-title-form2':
            called = aarq_apdu[1]['called-AP-title'][1]

    return calling, called


def _get_ae_qualifiers(aarq_apdu):
    calling = None
    if 'calling-AE-qualifier' in aarq_apdu[1]:
        if aarq_apdu[1]['calling-AE-qualifier'][0] == 'ap-qualifier-form2':
            calling = aarq_apdu[1]['calling-AE-qualifier'][1]

    called = None
    if 'called-AE-qualifier' in aarq_apdu[1]:
        if aarq_apdu[1]['called-AE-qualifier'][0] == 'ap-qualifier-form2':
            called = aarq_apdu[1]['called-AE-qualifier'][1]

    return calling, called


def _get_ap_invocation_identifiers(aarq_apdu):
    calling = aarq_apdu[1].get('calling-AP-invocation-identifier')
    called = aarq_apdu[1].get('called-AP-invocation-identifier')
    return calling, called


def _get_ae_invocation_identifiers(aarq_apdu):
    calling = aarq_apdu[1].get('calling-AE-invocation-identifier')
    called = aarq_apdu[1].get('called-AE-invocation-identifier')
    return calling, called


def _aarq_apdu(syntax_names, app_context_name,
               calling_ap_title, called_ap_title,
               calling_ae_qualifier, called_ae_qualifier,
               user_data):
    aarq_apdu = 'aarq', {'application-context-name': app_context_name}

    if calling_ap_title is not None:
        aarq_apdu[1]['calling-AP-title'] = 'ap-title-form2', calling_ap_title

    if called_ap_title is not None:
        aarq_apdu[1]['called-AP-title'] = 'ap-title-form2', called_ap_title

    if calling_ae_qualifier is not None:
        aarq_apdu[1]['calling-AE-qualifier'] = ('ae-qualifier-form2',
                                                calling_ae_qualifier)

    if called_ae_qualifier is not None:
        aarq_apdu[1]['called-AE-qualifier'] = ('ae-qualifier-form2',
                                               called_ae_qualifier)

    if user_data:
        aarq_apdu[1]['user-information'] = [
            asn1.External(direct_ref=_encoder.syntax_name,
                          indirect_ref=syntax_names.get_id(user_data[0]),
                          data=user_data[1])]

    return aarq_apdu


def _aare_apdu(syntax_names, user_data,
               responding_ap_title, responding_ae_qualifier,
               responding_ap_invocation_identifier,
               responding_ae_invocation_identifier):
    aare_apdu = 'aare', {
        'application-context-name': user_data[0],
        'result': 0,
        'result-source-diagnostic': ('acse-service-user', 0),
        'user-information': [
            asn1.External(direct_ref=_encoder.syntax_name,
                          indirect_ref=syntax_names.get_id(user_data[0]),
                          data=user_data[1])]}

    if responding_ap_title is not None:
        aare_apdu[1]['responding-AP-title'] = ('ap-title-form2',
                                               responding_ap_title)

    if responding_ae_qualifier is not None:
        aare_apdu[1]['responding-AE-qualifier'] = ('ae-qualifier-form2',
                                                   responding_ae_qualifier)

    if responding_ap_invocation_identifier is not None:
        aare_apdu[1]['responding-AP-invocation-identifier'] = \
            responding_ap_invocation_identifier

    if responding_ae_invocation_identifier is not None:
        aare_apdu[1]['responding-AE-invocation-identifier'] = \
            responding_ae_invocation_identifier

    return aare_apdu


def _abrt_apdu(source):
    return 'abrt', {'abort-source': source}


def _rlre_apdu():
    return 'rlre', {}


def _encode(value):
    return _encoder.encode_value('ACSE-1', 'ACSE-apdu', value)


def _decode(entity):
    return _encoder.decode_value('ACSE-1', 'ACSE-apdu', entity)
