"""Manufacturing Message Specification"""

import asyncio
import importlib.resources
import itertools
import logging
import typing

from hat import aio
from hat import asn1

from hat.drivers import acse
from hat.drivers import tcp
from hat.drivers.mms import common
from hat.drivers.mms import encoder


mlog = logging.getLogger(__name__)

_parameter_cbb = [False] * 11  # 18
_parameter_cbb[0] = True  # str1
_parameter_cbb[1] = True  # str2
_parameter_cbb[2] = True  # vnam
_parameter_cbb[3] = True  # valt
_parameter_cbb[4] = True  # vadr
_parameter_cbb[6] = True  # tpy
_parameter_cbb[7] = True  # vlis

_service_support = [False] * 85  # 93
_service_support[0] = True  # status
_service_support[1] = True  # getNameList
_service_support[2] = True  # identify
_service_support[4] = True  # read
_service_support[5] = True  # write
_service_support[6] = True  # getVariableAccessAttributes
_service_support[11] = True  # defineNamedVariableList
_service_support[12] = True  # getNamedVariableListAttributes
_service_support[13] = True  # deleteNamedVariableList
_service_support[79] = True  # informationReport

# not supported - compatibility flags
_service_support[18] = True  # output
_service_support[83] = True  # conclude

# (iso, standard, iso9506, part, mms-abstract-syntax-version1)
_mms_syntax_name = (1, 0, 9506, 2, 1)

# (iso, standard, iso9506, part, mms-annex-version1)
_mms_app_context_name = (1, 0, 9506, 2, 3)

with importlib.resources.as_file(importlib.resources.files(__package__) /
                                 'asn1_repo.json') as _path:
    _encoder = asn1.Encoder(asn1.Encoding.BER,
                            asn1.Repository.from_json(_path))


ConnectionCb: typing.TypeAlias = aio.AsyncCallable[['Connection'], None]
"""Connection callback"""

RequestCb: typing.TypeAlias = aio.AsyncCallable[['Connection', common.Request],
                                                common.Response | common.Error]
"""Request callback"""

UnconfirmedCb: typing.TypeAlias = aio.AsyncCallable[['Connection',
                                                     common.Unconfirmed],
                                                    None]
"""Unconfirmed callback"""


async def connect(addr: tcp.Address,
                  local_detail_calling: int | None = None,
                  request_cb: RequestCb | None = None,
                  unconfirmed_cb: UnconfirmedCb | None = None,
                  **kwargs
                  ) -> 'Connection':
    """Connect to MMS server

    Additional arguments are passed directly to `hat.drivers.acse.connect`
    (`syntax_name_list`, `app_context_name` and `user_data` are set by
    this coroutine).

    """
    initiate_req = 'initiate-RequestPDU', {
        'proposedMaxServOutstandingCalling': 5,
        'proposedMaxServOutstandingCalled': 5,
        'initRequestDetail': {
            'proposedVersionNumber': 1,
            'proposedParameterCBB': _parameter_cbb,
            'servicesSupportedCalling': _service_support}}

    if local_detail_calling is not None:
        initiate_req[1]['localDetailCalling'] = local_detail_calling

    req_user_data = _encode(initiate_req)
    conn = await acse.connect(addr=addr,
                              syntax_name_list=[_mms_syntax_name],
                              app_context_name=_mms_app_context_name,
                              user_data=(_mms_syntax_name, req_user_data),
                              **kwargs)

    try:
        res_syntax_name, res_user_data = conn.conn_res_user_data
        if res_syntax_name != _mms_syntax_name:
            raise Exception("invalid syntax name")

        initiate_res = _decode(res_user_data)
        if initiate_res[0] != 'initiate-ResponsePDU':
            raise Exception("invalid initiate response")

        return Connection(conn=conn,
                          request_cb=request_cb,
                          unconfirmed_cb=unconfirmed_cb)

    except Exception:
        await aio.uncancellable(conn.async_close())
        raise


async def listen(connection_cb: ConnectionCb,
                 addr: tcp.Address = tcp.Address('0.0.0.0', 102),
                 request_cb: RequestCb | None = None,
                 unconfirmed_cb: UnconfirmedCb | None = None,
                 *,
                 bind_connections: bool = False,
                 **kwargs
                 ) -> 'Server':
    """Create MMS listening server

    Additional arguments are passed directly to `hat.drivers.acse.listen`.

    Args:
        connection_cb: new connection callback
        request_cb: received request callback
        addr: local listening address

    """
    server = Server()
    server._connection_cb = connection_cb
    server._request_cb = request_cb
    server._unconfirmed_cb = unconfirmed_cb
    server._bind_connections = bind_connections

    server._srv = await acse.listen(validate_cb=server._on_validate,
                                    connection_cb=server._on_connection,
                                    addr=addr,
                                    bind_connections=False,
                                    **kwargs)

    return server


class Server(aio.Resource):
    """MMS listening server

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
        syntax_name, req_user_data = user_data
        if syntax_name != _mms_syntax_name:
            raise Exception('invalid mms syntax name')

        initiate_req = _decode(req_user_data)
        if initiate_req[0] != 'initiate-RequestPDU':
            raise Exception('invalid initiate request')

        initiate_res = 'initiate-ResponsePDU', {
            'negotiatedMaxServOutstandingCalling': 5,
            'negotiatedMaxServOutstandingCalled': 5,
            'negotiatedDataStructureNestingLevel': 4,  # TODO compatibility
            'initResponseDetail': {
                'negotiatedVersionNumber': 1,
                'negotiatedParameterCBB': _parameter_cbb,
                'servicesSupportedCalled': _service_support}}
        if 'localDetailCalling' in initiate_req[1]:
            initiate_res[1]['localDetailCalled'] = \
                initiate_req[1]['localDetailCalling']

        res_user_data = _encode(initiate_res)
        return _mms_syntax_name, res_user_data

    async def _on_connection(self, acse_conn):
        try:
            try:
                conn = Connection(conn=acse_conn,
                                  request_cb=self._request_cb,
                                  unconfirmed_cb=self._unconfirmed_cb)

            except Exception:
                await aio.uncancellable(acse_conn.async_close())
                raise

            try:
                await aio.call(self._connection_cb, conn)

            except BaseException:
                await aio.uncancellable(conn.async_close())
                raise

        except Exception as e:
            mlog.error("error creating new incomming connection: %s",
                       e, exc_info=e)
            return

        if not self._bind_connections:
            return

        try:
            await conn.wait_closed()

        except BaseException:
            await aio.uncancellable(conn.async_close())
            raise


class Connection(aio.Resource):
    """MMS connection

    For creating new connection see `connect` or `listen`.

    """

    def __init__(self,
                 conn: acse.Connection,
                 request_cb: RequestCb,
                 unconfirmed_cb: UnconfirmedCb):
        self._conn = conn
        self._request_cb = request_cb
        self._unconfirmed_cb = unconfirmed_cb
        self._loop = asyncio.get_running_loop()
        self._next_invoke_ids = itertools.count(0)
        self._response_futures = {}
        self._close_pdu = 'conclude-RequestPDU', None
        self._async_group = aio.Group()

        self.async_group.spawn(aio.call_on_cancel, self._on_close)
        self.async_group.spawn(self._receive_loop)
        self.async_group.spawn(aio.call_on_done, conn.wait_closing(),
                               self.close)

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._async_group

    @property
    def info(self) -> acse.ConnectionInfo:
        """Connection info"""
        return self._conn.info

    async def send_unconfirmed(self, unconfirmed: common.Unconfirmed):
        """Send unconfirmed message"""
        if not self.is_open:
            raise ConnectionError()

        pdu = 'unconfirmed-PDU', {
            'service': encoder.encode_unconfirmed(unconfirmed)}
        data = _mms_syntax_name, _encode(pdu)
        await self._conn.send(data)

    async def send_confirmed(self,
                             req: common.Request
                             ) -> common.Response | common.Error:
        """Send confirmed request and wait for response"""
        if not self.is_open:
            raise ConnectionError()

        invoke_id = next(self._next_invoke_ids)
        pdu = 'confirmed-RequestPDU', {
            'invokeID': invoke_id,
            'service': encoder.encode_request(req)}
        data = _mms_syntax_name, _encode(pdu)
        await self._conn.send(data)

        if not self.is_open:
            raise ConnectionError()

        try:
            future = self._loop.create_future()
            self._response_futures[invoke_id] = future
            return await future

        finally:
            self._response_futures.pop(invoke_id, None)

    async def _on_close(self):
        if self._conn.is_open:
            try:
                data = _mms_syntax_name, _encode(self._close_pdu)
                await self._conn.send(data)
                await self._conn.drain()

                # TODO: wait for response in case of conclude-RequestPDU

            except Exception as e:
                mlog.error("on close error: %s", e, exc_info=e)

        await self._conn.async_close()

    async def _receive_loop(self):
        try:
            while True:
                syntax_name, entity = await self._conn.receive()
                if syntax_name != _mms_syntax_name:
                    continue

                pdu = _decode(entity)
                name, data = pdu

                if name == 'unconfirmed-PDU':
                    await self._process_unconfirmed(data)

                elif name == 'confirmed-RequestPDU':
                    await self._process_request(data)

                elif name == 'confirmed-ResponsePDU':
                    await self._process_response(data)

                elif name == 'confirmed-ErrorPDU':
                    await self._process_error(data)

                elif name == 'conclude-RequestPDU':
                    self._close_pdu = 'conclude-ResponsePDU', None
                    break

                else:
                    raise Exception('unsupported pdu')

        except ConnectionError:
            pass

        except Exception as e:
            mlog.error("receive loop error: %s", e, exc_info=e)

        finally:
            self.close()

            for response_future in self._response_futures.values():
                if not response_future.done():
                    response_future.set_exception(ConnectionError())

    async def _process_unconfirmed(self, data):
        unconfirmed = encoder.decode_unconfirmed(data['service'])

        if self._unconfirmed_cb is None:
            raise Exception('unconfirmed_cb not defined')

        await aio.call(self._unconfirmed_cb, self, unconfirmed)

    async def _process_request(self, data):
        invoke_id = data['invokeID']
        req = encoder.decode_request(data['service'])

        if self._request_cb is None:
            raise Exception('request_cb not defined')

        res = await aio.call(self._request_cb, self, req)

        if isinstance(res, common.Response):
            res_pdu = 'confirmed-ResponsePDU', {
                'invokeID': invoke_id,
                'service': encoder.encode_response(res)}

        elif isinstance(res, common.Error):
            res_pdu = 'confirmed-ErrorPDU', {
                'invokeID': invoke_id,
                'serviceError': encoder.encode_error(res)}

        else:
            TypeError('unsupported response/error type')

        res_data = _mms_syntax_name, _encode(res_pdu)
        await self._conn.send(res_data)

    async def _process_response(self, data):
        invoke_id = data['invokeID']
        res = encoder.decode_response(data['service'])

        future = self._response_futures.get(invoke_id)
        if not future or future.done():
            mlog.warning("dropping confirmed response (invoke_id: %s)",
                         invoke_id)
            return

        future.set_result(res)

    async def _process_error(self, data):
        invoke_id = data['invokeID']
        error = encoder.decode_error(data['serviceError'])

        future = self._response_futures.get(invoke_id)
        if not future or future.done():
            mlog.warning("dropping confirmed error (invoke_id: %s)", invoke_id)
            return

        future.set_result(error)


def _encode(value):
    return _encoder.encode_value('ISO-9506-MMS-1', 'MMSpdu', value)


def _decode(entity):
    return _encoder.decode_value('ISO-9506-MMS-1', 'MMSpdu', entity)
