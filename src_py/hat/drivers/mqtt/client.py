from collections.abc import Collection
import asyncio
import collections
import contextlib
import itertools
import logging
import typing

from hat import aio
from hat import util

from hat.drivers import tcp
from hat.drivers.mqtt import common
from hat.drivers.mqtt import transport


mlog: logging.Logger = logging.getLogger(__name__)


class Msg(typing.NamedTuple):
    topic: common.String
    payload: str | util.Bytes
    qos: common.QoS = common.QoS.AT_MOST_ONCE
    retain: bool = True
    message_expiry_interval: common.UInt32 | None = None
    response_topic: common.String | None = None
    correlation_data: common.Binary | None = None
    user_properties: Collection[tuple[common.String, common.String]] = []
    content_type: common.String | None = None


MsgCb: typing.TypeAlias = aio.AsyncCallable[['Client', Msg], None]


async def connect(addr: tcp.Address,
                  msg_cb: MsgCb | None = None,
                  will_msg: Msg | None = None,
                  will_delay: common.UInt32 = 0,
                  client_id: common.String = '',
                  user_name: common.String | None = None,
                  password: common.Binary | None = None,
                  ping_delay: float | None = None,
                  response_timeout: float = 30,
                  **kwargs
                  ) -> 'Client':
    conn = await transport.connect(addr, **kwargs)

    try:
        req = _create_connect_packet(will_msg=will_msg,
                                     will_delay=will_delay,
                                     ping_delay=ping_delay,
                                     client_id=client_id,
                                     user_name=user_name,
                                     password=password)
        await conn.send(req)

        res = await aio.wait_for(conn.receive(), response_timeout)

        if isinstance(res, transport.DisconnectPacket):
            raise common.MqttError(res.reason, res.reason_string)

        if not isinstance(res, transport.ConnAckPacket):
            raise Exception('unexpected response')

        if res.reason != common.Reason.SUCCESS:
            raise common.MqttError(res.reason, res.reason_string)

    except BaseException:
        await aio.uncancellable(conn.async_close())
        raise

    client = Client()
    client._msg_cb = msg_cb
    client._response_timeout = response_timeout
    client._loop = asyncio.get_running_loop()
    client._async_group = aio.Group()
    client._conn = conn
    client._sent_event = asyncio.Event()
    client._ping_future = None
    client._disconnect_reason = common.Reason.SUCCESS
    client._disconnect_reason_string = None

    client._maximum_qos = res.maximum_qos
    client._client_id = (res.assigned_client_identifier
                         if res.assigned_client_identifier is not None
                         else client_id)
    client._keep_alive = (req.keep_alive if res.server_keep_alive is None
                          else res.server_keep_alive)
    client._response_information = res.response_information

    try:
        client.async_group.spawn(aio.call_on_cancel, client._on_close)

        client._identifier_registry = _IdentifierRegistry(
            client.async_group.create_subgroup())

        client.async_group.spawn(client._receive_loop)
        if client._keep_alive > 0:
            client.async_group.spawn(client._ping_loop)

    except BaseException:
        await aio.uncancellable(client.async_close())
        raise

    return client


class Client(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        return self._async_group

    @property
    def info(self) -> tcp.ConnectionInfo:
        return self._conn.info

    @property
    def maximum_qos(self) -> common.QoS:
        return self._maximum_qos

    @property
    def client_id(self) -> common.String:
        return self._client_id

    @property
    def response_information(self) -> common.String | None:
        return self._response_information

    async def publish(self, msg: Msg):
        if msg.qos.value > self._maximum_qos.value:
            raise Exception(f'maximum supported QoS is {self._maximum_qos}')

        if msg.qos == common.QoS.AT_MOST_ONCE:
            identifier = None

        elif msg.qos in (common.QoS.AT_LEAST_ONCE,
                         common.QoS.EXACLTY_ONCE):
            identifier = await self._identifier_registry.allocate_identifier()

        else:
            raise ValueError('unsupported QoS')

        try:
            req = transport.PublishPacket(
                duplicate=False,
                qos=self._maximum_qos,
                retain=msg.retain,
                topic_name=msg.topic,
                packet_identifier=identifier,
                message_expiry_interval=msg.message_expiry_interval,
                topic_alias=None,
                response_topic=msg.response_topic,
                correlation_data=msg.correlation_data,
                user_properties=msg.user_properties,
                subscription_identifiers=[],
                content_type=msg.content_type,
                payload=msg.payload)

            if msg.qos == common.QoS.AT_MOST_ONCE:
                await self._conn.send(req)
                return

            future = self._identifier_registry.create_future(identifier)
            await self._conn.send(req)
            res = await aio.wait_for(future, self._response_timeout)

            if msg.qos == common.QoS.AT_LEAST_ONCE:
                self._assert_res_type(res, transport.PubAckPacket)
                if common.is_error_reason(res.reason):
                    raise common.MqttError(res.reason, res.reason_string)

                return

            self._assert_res_type(res, transport.PubRecPacket)
            if common.is_error_reason(res.reason):
                raise common.MqttError(res.reason, res.reason_string)

            req = transport.PubRelPacket(packet_identifier=identifier,
                                         reason=common.Reason.SUCCESS,
                                         reason_string=None,
                                         user_properties=[])

            future = self._identifier_registry.create_future(identifier)
            await self._conn.send(req)
            res = await aio.wait_for(future, self._response_timeout)

            self._assert_res_type(res, transport.PubCompPacket)
            if common.is_error_reason(res.reason):
                raise common.MqttError(res.reason, res.reason_string)

        except asyncio.TimeoutError:
            mlog.error("response timeout exceeded")

            self._set_disconnect_reason(
                common.Reason.IMPLEMENTATION_SPECIFIC_ERROR,
                "response timeout exceeded")
            self.close()

            raise ConnectionError()

        finally:
            if identifier is not None:
                self._identifier_registry.release_identifier(identifier)

    async def subscribe(self,
                        subscriptions: Collection[common.Subscription]
                        ) -> Collection[common.Reason]:
        identifier = await self._identifier_registry.allocate_identifier()

        try:
            req = transport.SubscribePacket(packet_identifier=identifier,
                                            subscription_identifier=None,
                                            user_properties=[],
                                            subscriptions=subscriptions)

            future = self._identifier_registry.create_future(identifier)
            await self._conn.send(req)
            res = await aio.wait_for(future, self._response_timeout)

            self._assert_res_type(res, transport.SubAckPacket)
            return res.reasons

        except asyncio.TimeoutError:
            mlog.error("response timeout exceeded")

            self._set_disconnect_reason(
                common.Reason.IMPLEMENTATION_SPECIFIC_ERROR,
                "response timeout exceeded")
            self.close()

            raise ConnectionError()

        finally:
            self._identifier_registry.release_identifier(identifier)

    async def unsubscribe(self,
                          topic_filters: Collection[common.String]
                          ) -> Collection[common.Reason]:
        identifier = await self._identifier_registry.allocate_identifier()

        try:
            req = transport.UnsubscribePacket(packet_identifier=identifier,
                                              user_properties=[],
                                              topic_filters=topic_filters)

            future = self._identifier_registry.create_future(identifier)
            await self._conn.send(req)
            res = await aio.wait_for(future, self._response_timeout)

            self._assert_res_type(res, transport.UnsubAckPacket)
            return res.reasons

        except asyncio.TimeoutError:
            mlog.error("response timeout exceeded")

            self._set_disconnect_reason(
                common.Reason.IMPLEMENTATION_SPECIFIC_ERROR,
                "response timeout exceeded")
            self.close()

            raise ConnectionError()

        finally:
            self._identifier_registry.release_identifier(identifier)

    async def _on_close(self):
        if self._conn.is_open:
            with contextlib.suppress(Exception):
                await self._conn.send(
                    transport.DisconnectPacket(
                        reason=self._disconnect_reason,
                        session_expiry_interval=None,
                        reason_string=self._disconnect_reason_string,
                        user_properties=[],
                        server_reference=None))

        await self._conn.async_close()

    def _set_disconnect_reason(self, reason, reason_string):
        if common.is_error_reason(self._disconnect_reason):
            return

        self._disconnect_reason = reason
        self._disconnect_reason_string = reason_string

    async def _send(self, packet):
        await self._conn.send(packet)
        self._sent_event.set()

    def _assert_res_type(self, res, cls):
        if isinstance(res, cls):
            return

        mlog.error('received invalid response (expecting %s)', cls)

        self._set_disconnect_reason(common.Reason.PROTOCOL_ERROR,
                                    'invalid response type')
        self.close()

        raise ConnectionError()

    async def _receive_loop(self):
        try:
            mlog.debug('starting receive loop')

            while True:
                packet = await self._conn.receive()

                if isinstance(packet, transport.PublishPacket):
                    await self._process_publish_packet(packet)

                elif isinstance(packet, transport.PubRelPacket):
                    await self._process_publish_release_packet(packet)

                elif isinstance(packet, (transport.PubAckPacket,
                                         transport.PubRecPacket,
                                         transport.PubCompPacket,
                                         transport.SubAckPacket,
                                         transport.UnsubAckPacket)):
                    if not self._identifier_registry.register_packet(packet):
                        mlog.warning('packet identifier not expected - '
                                     'dropping packet')

                elif isinstance(packet, transport.PingResPacket):
                    if self._ping_future and not self._ping_future.done():
                        self._ping_future.set_result(None)

                elif isinstance(packet, transport.DisconnectPacket):
                    mlog.debug('received disconnect packet: %s: %s',
                               packet.reason, packet.reason_string)

                    self._conn.close()
                    break

                elif isinstance(packet, transport.AuthPacket):
                    raise common.MqttError(
                        common.Reason.IMPLEMENTATION_SPECIFIC_ERROR,
                        'auth packet not supported')

                else:
                    raise common.MqttError(common.Reason.PROTOCOL_ERROR,
                                           'unexpected packet')

        except ConnectionError:
            pass

        except common.MqttError as e:
            mlog.error('receive loop mqtt error: %s', e, exc_info=e)

            self._set_disconnect_reason(e.reason, e.description)

        except Exception as e:
            mlog.error('receive loop error: %s', e, exc_info=e)

            self._set_disconnect_reason(common.Reason.UNSPECIFIED_ERROR, None)

        finally:
            mlog.debug('stopping receive loop')

            self.close()

    async def _ping_loop(self):
        try:
            mlog.debug('starting ping loop')

            while True:
                self._sent_event.clear()

                with contextlib.suppress(asyncio.TimeoutError):
                    await aio.wait_for(self._sent_event.wait(),
                                       self._keep_alive)
                    continue

                self._ping_future = self._loop.create_future()
                await self._conn.send(transport.PingReqPacket())

                await aio.wait_for(self._ping_future, self._response_timeout)

        except ConnectionError:
            pass

        except asyncio.TimeoutError:
            mlog.error('ping response timeout')

            self._set_disconnect_reason(
                common.Reason.IMPLEMENTATION_SPECIFIC_ERROR,
                "response timeout exceeded")

        except Exception as e:
            mlog.error('ping loop error: %s', e, exc_info=e)

            self._set_disconnect_reason(common.Reason.UNSPECIFIED_ERROR, None)

        finally:
            mlog.debug('stopping ping loop')

            self.close()

    async def _process_publish_packet(self, packet):
        if self._msg_cb:
            msg = Msg(
                topic=packet.topic_name,
                payload=packet.payload,
                qos=packet.qos,
                retain=packet.retain,
                message_expiry_interval=packet.message_expiry_interval,
                response_topic=packet.response_topic,
                correlation_data=packet.correlation_data,
                user_properties=packet.user_properties,
                content_type=packet.content_type)

            await aio.call(self._msg_cb, self, msg)

        if msg.qos == common.QoS.AT_MOST_ONCE:
            return

        if msg.qos == common.QoS.AT_LEAST_ONCE:
            res = transport.PubAckPacket(
                packet_identifier=packet.packet_identifier,
                reason=common.Reason.SUCCESS,
                reason_string=None,
                user_properties=[])

            await self._send(res)
            return

        if msg.qos != common.QoS.EXACLTY_ONCE:
            raise ValueError('unsupported QoS')

        req = transport.PubRecPacket(
            packet_identifier=packet.packet_identifier,
            reason=common.Reason.SUCCESS,
            reason_string=None,
            user_properties=[])

        await self._conn.send(req)

    async def _process_publish_release_packet(self, packet):

        # TODO should remember previous publish packet and check response
        #      timeout

        if common.is_error_reason(packet.reason):
            mlog.warning('publish release error: %s: %s',
                         packet.reason, packet.reason_string)
            return

        req = transport.PubCompPacket(
            packet_identifier=packet.packet_identifier,
            reason=common.Reason.SUCCESS,
            reason_string=None,
            user_properties=[])

        await self._conn.send(req)


class _IdentifierRegistry(aio.Resource):

    def __init__(self,
                 async_group: aio.Group,
                 queue_size: int = 1024):
        self._async_group = async_group
        self._loop = asyncio.get_running_loop()
        self._next_identifier = 1
        self._identifier_futures = {}
        self._create_futures = aio.Queue(queue_size)

        self.async_group.spawn(aio.call_on_cancel, self._on_close)

    @property
    def async_group(self) -> aio.Group:
        return self._async_group

    async def allocate_identifier(self) -> common.UInt16:
        if not self.is_open:
            raise ConnectionError()

        if len(self._identifier_futures) >= 0xffff - 1:
            future = self._loop.create_future()

            try:
                await self._create_futures.put(future)

            except aio.QueueClosedError:
                raise ConnectionError()

            identifier = await future

        else:
            identifier = self._get_free_identifier()

        if not self.is_open:
            raise ConnectionError()

        self._identifier_futures[identifier] = collections.deque()
        return identifier

    def release_identifier(self, identifier: common.UInt16):
        futures = self._identifier_futures.pop(identifier, [])
        for future in futures:
            if not future.done():
                future.set_exception(ConnectionError())

        while not self._create_futures.empty():
            future = self._create_futures.get_nowait()
            if future.done():
                continue

            future.set_result(identifier)
            break

    def create_future(self, identifier: common.UInt16) -> asyncio.Future:
        if not self.is_open:
            raise ConnectionError()

        future = self._loop.create_future()
        self._identifier_futures[identifier].append(future)

        return future

    def register_packet(self, packet: (transport.PubAckPacket |
                                       transport.PubRecPacket |
                                       transport.PubCompPacket |
                                       transport.SubAckPacket |
                                       transport.UnsubAckPacket)) -> bool:
        if not self.is_open:
            raise ConnectionError()

        futures = self._identifier_futures.get(packet.packet_identifier)
        while futures:
            future = futures.popleft()
            if future.done():
                continue

            future.set_result(packet)
            return True

        return False

    def _on_close(self):
        self._create_futures.close()

        while not self._create_futures.empty():
            future = self._create_futures.get_nowait()
            if not future.done():
                future.set_exception(ConnectionError())

        for futures in self._identifier_futures.values():
            for future in futures:
                if not future.done():
                    future.set_exception(ConnectionError())

    def _get_free_identifier(self):
        for i in itertools.chain(range(self._next_identifier, 0x10000),
                                 range(1, self._next_identifier)):
            if i not in self._identifier_futures:
                self._next_identifier = i
                return i

        raise Exception('free identifier unavailable')


def _create_connect_packet(will_msg, will_delay, ping_delay, client_id,
                           user_name, password):
    if will_msg:
        will = transport.Will(
            qos=will_msg.qos,
            retain=will_msg.retain,
            delay_interval=will_delay,
            message_expiry_interval=will_msg.message_expiry_interval,
            content_type=will_msg.content_type,
            response_topic=will_msg.response_topic,
            correlation_data=will_msg.correlation_data,
            user_properties=will_msg.user_properties,
            topic=will_msg.topic,
            payload=will_msg.payload)

    else:
        will = None

    if ping_delay is None:
        keep_alive = 0

    elif ping_delay < 1:
        keep_alive = 1

    elif ping_delay > 0xffff:
        keep_alive = 0xffff

    else:
        keep_alive = round(ping_delay)

    return transport.ConnectPacket(
        clean_start=True,
        keep_alive=keep_alive,
        session_expiry_interval=0,
        receive_maximum=0xffff,
        maximum_packet_size=None,
        topic_alias_maximum=0,
        request_response_information=True,
        request_problem_information=True,
        user_properties=[],
        authentication_method=None,
        authentication_data=None,
        client_identifier=client_id,
        will=will,
        user_name=user_name,
        password=password)
