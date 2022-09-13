import asyncio
import itertools
import logging
import typing

from hat import aio
from hat.drivers import tcp
from hat.drivers.pnetgateway import common
from hat.drivers.pnetgateway import encoder
from hat.drivers.pnetgateway import transport


mlog = logging.getLogger(__name__)


StatusCb = aio.AsyncCallable[[common.Status], None]
"""Status change callback"""

DataCb = aio.AsyncCallable[[typing.List[common.Data]], None]
"""Data change callback"""


async def connect(addr: tcp.Address,
                  username: str,
                  password: str,
                  status_cb: StatusCb,
                  data_cb: DataCb,
                  subscriptions: typing.Optional[typing.List[str]] = None,
                  ) -> 'Connection':
    """Connect to PNET Gateway server

    Args:
        address: PNET Gateway server address
        username: user name
        password: password
        status_cb: status change callback
        data_cb: data change callback
        subscriptions: list of data keys for subscriptions

    If subscription is ``None``, client is subscribed to all data changes
    from the server.

    """
    conn = Connection()
    conn._pnet_status = common.Status.DISCONNECTED
    conn._data = {}
    conn._status_cb = status_cb
    conn._data_cb = data_cb
    conn._next_ids = itertools.count(0)
    conn._id_futures = {}

    conn._conn = transport.Transport(await tcp.connect(addr))

    try:
        conn._conn.send({'type': 'authentication_request',
                         'body': {'username': username,
                                  'password': password,
                                  'subscriptions': subscriptions}})

        msg = None
        while msg is None or msg['type'] != 'authentication_response':
            msg = await conn._conn.receive()

        if not msg['body']['success']:
            raise Exception('authentication failed')

        conn._pnet_status = common.Status(msg['body']['status'])
        for i in msg['body']['data']:
            data = encoder.data_from_json(i)
            conn._data[data.key] = data

    except BaseException:
        await aio.uncancellable(conn.async_close())
        raise

    conn.async_group.spawn(conn._read_loop)

    return conn


class Connection(aio.Resource):
    """PNET Gateway connection

    For creating new connection see :func:`connect`

    """

    @property
    def async_group(self) -> aio.Group:
        """Async group"""
        return self._conn.async_group

    @property
    def pnet_status(self) -> common.Status:
        """PNET Gateway server's status"""
        return self._pnet_status

    @property
    def data(self) -> typing.Dict[str, common.Data]:
        """Subscribed data"""
        return self._data

    async def change_data(self,
                          changes: typing.Iterable[common.Change]
                          ) -> typing.List[bool]:
        """Send change data request to PNET Gateway server"""
        return await self._send_with_response(
            'change_data_request',
            [encoder.change_to_json(i) for i in changes])

    async def send_commands(self,
                            commands: typing.Iterable[common.Command]
                            ) -> typing.List[bool]:
        """Send commands to PNET Gateway"""
        return await self._send_with_response(
            'command_request',
            [encoder.command_to_json(i) for i in commands])

    async def _send_with_response(self, msg_type, msg_data):
        if not self.is_open:
            raise ConnectionError()

        msg_id = next(self._next_ids)
        msg = {'type': msg_type,
               'body': {'id': msg_id,
                        'data': msg_data}}

        future = asyncio.Future()
        self._id_futures[msg_id] = future

        try:
            self._conn.send(msg)
            return await future

        finally:
            self._id_futures.pop(msg_id)

    async def _read_loop(self):
        try:
            while True:
                msg = await self._conn.receive()

                if msg['type'] == 'change_data_response':
                    self._on_change_data_response(msg['body'])

                elif msg['type'] == 'command_response':
                    self._on_command_response(msg['body'])

                elif msg['type'] == 'data_changed_unsolicited':
                    await self._on_data_changed_unsolicited(msg['body'])

                elif msg['type'] == 'status_changed_unsolicited':
                    await self._on_status_changed_unsolicited(msg['body'])

        except ConnectionError:
            pass

        except Exception as e:
            mlog.warning('read loop error: %s', e, exc_info=e)

        finally:
            self.close()
            for future in self._id_futures.values():
                if not future.done():
                    future.set_exception(ConnectionError())

    def _on_change_data_response(self, body):
        future = self._id_futures.get(body.get('id'))
        if not future or future.done():
            return

        mlog.debug('received change data response for %s', body.get('id'))
        future.set_result(body['success'])

    def _on_command_response(self, body):
        future = self._id_futures.get(body.get('id'))
        if not future or future.done():
            return

        mlog.debug('received command response for %s', body.get('id'))
        future.set_result(body['success'])

    async def _on_data_changed_unsolicited(self, body):
        if not body['data']:
            return

        mlog.debug('received data change unsolicited')
        data = [encoder.data_from_json(i) for i in body['data']]
        for i in data:
            self._data[i.key] = i
        await aio.call(self._data_cb, data)

    async def _on_status_changed_unsolicited(self, body):
        mlog.debug('received status changed unsolicited')
        self._pnet_status = common.Status(body['status'])

        self._data = {}
        for i in body['data']:
            data = encoder.data_from_json(i)
            self._data[data.key] = data

        await aio.call(self._status_cb, self._pnet_status)
