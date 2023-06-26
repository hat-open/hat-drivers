"""Connection oriented presentation protocol"""

import asyncio
import importlib.resources
import logging
import typing

from hat import aio
from hat import asn1

from hat.drivers import cosp
from hat.drivers import tcp


mlog = logging.getLogger(__name__)

with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'asn1_repo.json') as _path:
    _encoder = asn1.Encoder(asn1.Encoding.BER,
                            asn1.Repository.from_json(_path))


class ConnectionInfo(typing.NamedTuple):
    local_addr: tcp.Address
    local_tsel: int | None
    local_ssel: int | None
    local_psel: int | None
    remote_addr: tcp.Address
    remote_tsel: int | None
    remote_ssel: int | None
    remote_psel: int | None


IdentifiedEntity: typing.TypeAlias = tuple[asn1.ObjectIdentifier, asn1.Entity]
"""Identified entity"""

ValidateCb: typing.TypeAlias = aio.AsyncCallable[['SyntaxNames',
                                                  IdentifiedEntity],
                                                 IdentifiedEntity | None]
"""Validate callback"""

ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""


class SyntaxNames:
    """Syntax name registry

    Args:
        syntax_names: list of ASN.1 ObjectIdentifiers representing syntax names

    """

    def __init__(self, syntax_names: list[asn1.ObjectIdentifier]):
        self._syntax_id_names = {(i * 2 + 1): name
                                 for i, name in enumerate(syntax_names)}
        self._syntax_name_ids = {v: k
                                 for k, v in self._syntax_id_names.items()}

    def get_name(self, syntax_id: int) -> asn1.ObjectIdentifier:
        """Get syntax name associated with id"""
        return self._syntax_id_names[syntax_id]

    def get_id(self, syntax_name: asn1.ObjectIdentifier) -> int:
        """Get syntax id associated with name"""
        return self._syntax_name_ids[syntax_name]


async def connect(addr: tcp.Address,
                  syntax_names: SyntaxNames,
                  user_data: IdentifiedEntity | None = None,
                  *,
                  local_psel: int | None = None,
                  remote_psel: int | None = None,
                  copp_receive_queue_size: int = 1024,
                  copp_send_queue_size: int = 1024,
                  **kwargs
                  ) -> 'Connection':
    """Connect to COPP server

    Additional arguments are passed directly to `hat.drivers.cosp.connect`.

    """
    cp_ppdu = _cp_ppdu(syntax_names, local_psel, remote_psel, user_data)
    cp_ppdu_data = _encode('CP-type', cp_ppdu)
    conn = await cosp.connect(addr, cp_ppdu_data, **kwargs)

    try:
        cpa_ppdu = _decode('CPA-PPDU', conn.conn_res_user_data)
        _validate_connect_response(cp_ppdu, cpa_ppdu)

        calling_psel, called_psel = _get_psels(cp_ppdu)
        return Connection(conn, syntax_names, cp_ppdu, cpa_ppdu,
                          calling_psel, called_psel,
                          copp_receive_queue_size, copp_send_queue_size)

    except Exception:
        await aio.uncancellable(_close_cosp(conn, _arp_ppdu()))
        raise


async def listen(validate_cb: ValidateCb,
                 connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 *,
                 bind_connections: bool = False,
                 copp_receive_queue_size: int = 1024,
                 copp_send_queue_size: int = 1024,
                 **kwargs
                 ) -> 'Server':
    """Create COPP listening server

    Additional arguments are passed directly to `hat.drivers.cosp.listen`.

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
    server._receive_queue_size = copp_receive_queue_size
    server._send_queue_size = copp_send_queue_size

    server._srv = await cosp.listen(server._on_validate,
                                    server._on_connection,
                                    addr,
                                    bind_connections=False,
                                    **kwargs)

    return server


class Server(aio.Resource):
    """COPP listening server

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

    async def _on_validate(self, user_data):
        cp_ppdu = _decode('CP-type', user_data)
        cp_params = cp_ppdu['normal-mode-parameters']
        called_psel_data = cp_params.get('called-presentation-selector')
        called_psel = (int.from_bytes(called_psel_data, 'big')
                       if called_psel_data else None)
        cp_pdv_list = cp_params['user-data'][1][0]
        syntax_names = _sytax_names_from_cp_ppdu(cp_ppdu)
        cp_user_data = (
            syntax_names.get_name(
                cp_pdv_list['presentation-context-identifier']),
            cp_pdv_list['presentation-data-values'][1])

        cpa_user_data = await aio.call(self._validate_cb, syntax_names,
                                       cp_user_data)

        cpa_ppdu = _cpa_ppdu(syntax_names, called_psel, cpa_user_data)
        cpa_ppdu_data = _encode('CPA-PPDU', cpa_ppdu)
        return cpa_ppdu_data

    async def _on_connection(self, cosp_conn):
        try:
            try:
                cp_ppdu = _decode('CP-type', cosp_conn.conn_req_user_data)
                cpa_ppdu = _decode('CPA-PPDU', cosp_conn.conn_res_user_data)

                syntax_names = _sytax_names_from_cp_ppdu(cp_ppdu)
                calling_psel, called_psel = _get_psels(cp_ppdu)

                conn = Connection(cosp_conn, syntax_names, cp_ppdu, cpa_ppdu,
                                  calling_psel, called_psel,
                                  self._receive_queue_size,
                                  self._send_queue_size)

            except Exception:
                await aio.uncancellable(_close_cosp(cosp_conn, _arp_ppdu()))
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
    """COPP connection

    For creating new connection see `connect` or `listen`.

    """

    def __init__(self,
                 conn: cosp.Connection,
                 syntax_names: SyntaxNames,
                 cp_ppdu: asn1.Value,
                 cpa_ppdu: asn1.Value,
                 local_psel: int | None,
                 remote_psel: int | None,
                 receive_queue_size: int,
                 send_queue_size: int):
        cp_user_data = cp_ppdu['normal-mode-parameters']['user-data']
        cpa_user_data = cpa_ppdu['normal-mode-parameters']['user-data']

        conn_req_user_data = (
            syntax_names.get_name(
                cp_user_data[1][0]['presentation-context-identifier']),
            cp_user_data[1][0]['presentation-data-values'][1])
        conn_res_user_data = (
            syntax_names.get_name(
                cpa_user_data[1][0]['presentation-context-identifier']),
            cpa_user_data[1][0]['presentation-data-values'][1])

        self._conn = conn
        self._syntax_names = syntax_names
        self._conn_req_user_data = conn_req_user_data
        self._conn_res_user_data = conn_res_user_data
        self._loop = asyncio.get_running_loop()
        self._info = ConnectionInfo(local_psel=local_psel,
                                    remote_psel=remote_psel,
                                    **conn.info._asdict())
        self._close_ppdu = _arp_ppdu()
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
    def syntax_names(self) -> SyntaxNames:
        """Syntax names"""
        return self._syntax_names

    @property
    def conn_req_user_data(self) -> IdentifiedEntity:
        """Connect request's user data"""
        return self._conn_req_user_data

    @property
    def conn_res_user_data(self) -> IdentifiedEntity:
        """Connect response's user data"""
        return self._conn_res_user_data

    def close(self, user_data: IdentifiedEntity | None = None):
        """Close connection"""
        self._close(_aru_ppdu(self._syntax_names, user_data))

    async def async_close(self, user_data: IdentifiedEntity | None = None):
        """Async close"""
        self.close(user_data)
        await self.wait_closed()

    async def receive(self) -> IdentifiedEntity:
        """Receive data"""
        try:
            return await self._receive_queue.get()

        except aio.QueueClosedError:
            raise ConnectionError()

    async def send(self, data: IdentifiedEntity):
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
        await _close_cosp(self._conn, self._close_ppdu)

    def _close(self, ppdu):
        if not self.is_open:
            return

        self._close_ppdu = ppdu
        self._async_group.close()

    async def _receive_loop(self):
        try:
            while True:
                cosp_data = await self._conn.receive()

                user_data = _decode('User-data', cosp_data)
                pdv_list = user_data[1][0]
                syntax_name = self._syntax_names.get_name(
                    pdv_list['presentation-context-identifier'])
                data = pdv_list['presentation-data-values'][1]

                await self._receive_queue.put((syntax_name, data))

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self._close(_arp_ppdu())
            self._receive_queue.close()

    async def _send_loop(self):
        future = None
        try:
            while True:
                data, future = await self._send_queue.get()

                if data is None:
                    await self._conn.drain()

                else:
                    ppdu_data = _encode('User-data',
                                        _user_data(self._syntax_names, data))
                    await self._conn.send(ppdu_data)

                if future and not future.done():
                    future.set_result(None)

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("send loop error: %s", e, exc_info=e)

        finally:
            self._close(_arp_ppdu())
            self._send_queue.close()

            while True:
                if future and not future.done():
                    future.set_result(None)
                if self._send_queue.empty():
                    break
                _, future = self._send_queue.get_nowait()


async def _close_cosp(cosp_conn, ppdu):
    try:
        data = _encode('Abort-type', ppdu)

    except Exception as e:
        mlog.error("error encoding abort ppdu: %s", e, exc_info=e)
        data = None

    finally:
        await cosp_conn.async_close(data)


def _get_psels(cp_ppdu):
    cp_params = cp_ppdu['normal-mode-parameters']
    calling_psel_data = cp_params.get('calling-presentation-selector')
    calling_psel = (int.from_bytes(calling_psel_data, 'big')
                    if calling_psel_data else None)
    called_psel_data = cp_params.get('called-presentation-selector')
    called_psel = (int.from_bytes(called_psel_data, 'big')
                   if called_psel_data else None)
    return calling_psel, called_psel


def _validate_connect_response(cp_ppdu, cpa_ppdu):
    cp_params = cp_ppdu['normal-mode-parameters']
    cpa_params = cpa_ppdu['normal-mode-parameters']
    called_psel_data = cp_params.get('called-presentation-selector')
    responding_psel_data = cpa_params.get('responding-presentation-selector')

    if called_psel_data and responding_psel_data:
        called_psel = int.from_bytes(called_psel_data, 'big')
        responding_psel = int.from_bytes(responding_psel_data, 'big')

        if called_psel != responding_psel:
            raise Exception('presentation selectors not matching')

    result_list = cpa_params['presentation-context-definition-result-list']
    if any(i['result'] != 0 for i in result_list):
        raise Exception('presentation context not accepted')


def _cp_ppdu(syntax_names, calling_psel, called_psel, user_data):
    cp_params = {
        'presentation-context-definition-list': [
            {'presentation-context-identifier': i,
             'abstract-syntax-name': name,
             'transfer-syntax-name-list': [_encoder.syntax_name]}
            for i, name in syntax_names._syntax_id_names.items()]}

    if calling_psel is not None:
        cp_params['calling-presentation-selector'] = \
            calling_psel.to_bytes(4, 'big')

    if called_psel is not None:
        cp_params['called-presentation-selector'] = \
            called_psel.to_bytes(4, 'big')

    if user_data:
        cp_params['user-data'] = _user_data(syntax_names, user_data)

    return {
        'mode-selector': {
            'mode-value': 1},
        'normal-mode-parameters': cp_params}


def _cpa_ppdu(syntax_names, responding_psel, user_data):
    cpa_params = {
        'presentation-context-definition-result-list': [
            {'result': 0,
             'transfer-syntax-name': _encoder.syntax_name}
            for _ in syntax_names._syntax_id_names.keys()]}

    if responding_psel is not None:
        cpa_params['responding-presentation-selector'] = \
            responding_psel.to_bytes(4, 'big')

    if user_data:
        cpa_params['user-data'] = _user_data(syntax_names, user_data)

    return {
        'mode-selector': {
            'mode-value': 1},
        'normal-mode-parameters': cpa_params}


def _aru_ppdu(syntax_names, user_data):
    aru_params = {}

    if user_data:
        aru_params['user-data'] = _user_data(syntax_names, user_data)

    return 'aru-ppdu', ('normal-mode-parameters', aru_params)


def _arp_ppdu():
    return 'arp-ppdu', {}


def _user_data(syntax_names, user_data):
    return 'fully-encoded-data', [{
        'presentation-context-identifier': syntax_names.get_id(user_data[0]),
        'presentation-data-values': (
            'single-ASN1-type', user_data[1])}]


def _sytax_names_from_cp_ppdu(cp_ppdu):
    cp_params = cp_ppdu['normal-mode-parameters']
    syntax_names = SyntaxNames([])
    syntax_names._syntax_id_names = {
        i['presentation-context-identifier']: i['abstract-syntax-name']
        for i in cp_params['presentation-context-definition-list']}
    syntax_names._syntax_name_ids = {
        v: k for k, v in syntax_names._syntax_id_names.items()}
    return syntax_names


def _encode(name, value):
    return _encoder.encode('ISO8823-PRESENTATION', name, value)


def _decode(name, data):
    res, _ = _encoder.decode('ISO8823-PRESENTATION', name, memoryview(data))
    return res
