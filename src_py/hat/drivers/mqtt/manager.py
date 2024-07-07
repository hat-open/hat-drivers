import argparse
import asyncio
import contextlib
import sys

from hat import aio
from hat import json

from hat.drivers import mqtt
from hat.drivers import tcp


def create_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port', type=int, metavar='PORT', dest='port', default=1883,
        help='server TCP port (default 1883)')
    parser.add_argument(
        '--qos', type=int, metavar='QoS', dest='qos', default=0,
        help='quality of service (values 0, 1, 2) (default 0)')
    parser.add_argument(
        'host', metavar='HOST',
        help='server hostname')
    subparsers = parser.add_subparsers(
        title='actions', dest='action', required=True,
        help='available commands')

    publish_parser = subparsers.add_parser(  # NOQA
        'publish',
        description='publish message')

    subscrive_parser = subparsers.add_parser(
        'subscribe',
        description='subscribe to message notifications')
    subscrive_parser.add_argument(
        '--retain', action='store_true',
        help='receive retained messages')
    subscrive_parser.add_argument(
        'topics', metavar='TOPIC', nargs='+',
        help='subscription topic')

    return parser


def main():
    parser = create_argument_parser()
    args = parser.parse_args()

    aio.init_asyncio()
    with contextlib.suppress(asyncio.CancelledError):
        aio.run_asyncio(async_main(args))


async def async_main(args):
    addr = tcp.Address(args.host, args.port)
    qos = mqtt.QoS(args.qos)

    if args.action == 'publish':
        return await _act_publish(addr, qos, args)

    if args.action == 'subscribe':
        return await _act_subscribe(addr, qos, args)

    raise ValueError('unsupported action')


async def _act_publish(addr, qos, args):
    raise NotImplementedError()


async def _act_subscribe(addr, qos, args):
    msg_queue = aio.Queue(1024)

    async def on_msg(client, msg):
        await msg_queue.put(msg)

    retain_handling = (mqtt.RetainHandling.SEND_ON_SUBSCRIBE if args.retain
                       else mqtt.RetainHandling.DONT_SEND)
    subscriptions = [mqtt.Subscription(topic_filter=topic,
                                       maximum_qos=qos,
                                       no_local=False,
                                       retain_as_published=False,
                                       retain_handling=retain_handling)
                     for topic in args.topics]

    client = await mqtt.connect(addr=addr,
                                msg_cb=on_msg)

    try:
        reasons = await client.subscribe(subscriptions)

        if any(mqtt.is_error_reason(reason) for reason in reasons):
            print('subscription error:', reasons, file=sys.stderr)
            return 1

        while True:
            msg = await msg_queue.get()

            msg_json = _msg_to_json(msg)
            msg_json_str = json.encode(msg_json)

            print(msg_json_str)

    finally:
        await aio.uncancellable(client.async_close())


def _msg_to_json(msg):

    if isinstance(msg.payload, str):
        payload = msg.payload

    else:
        try:
            payload = str(msg.payload, encoding='utf-8')

        except UnicodeError:
            payload = bytes(msg.payload).hex()

    return {'topic': msg.topic,
            'payload': payload,
            'qos': msg.qos.name,
            'retain': msg.retain,
            'message_expiry_interval': msg.message_expiry_interval,
            'response_topic': msg.response_topic,
            'correlation_data': msg.correlation_data,
            'user_properties': [list(i) for i in msg.user_properties],
            'content_type': msg.content_type}


if __name__ == '__main__':
    sys.argv[0] = 'hat-mqtt-manager'
    sys.exit(main())
