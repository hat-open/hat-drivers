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
        help='server TCP port, defaults to 1883')
    parser.add_argument(
        '--qos', type=int, metavar='QoS', dest='qos', default=0,
        help='quality of service, defaults to 0 (values: 0, 1, 2)')

    parser.add_argument(
        'host', metavar='HOST',
        help='server hostname')

    subparsers = parser.add_subparsers(
        dest='action',
        help='available commands')

    subparser_publish = subparsers.add_parser(
        'publish',
        help='publish message')

    subparser_subscribe = subparsers.add_parser(
        'subscribe',
        help='subscribe to message notifications')
    subparser_subscribe.add_argument(
        '--retain', action='store_true',
        help='receive retained messages')
    subparser_subscribe.add_argument(
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
        await _act_publish(addr, qos, args)

    elif args.action == 'subscribe':
        await _act_subscribe(addr, qos, args)

    else:
        raise ValueError('unsupported action')


async def _act_publish(addr, qos, args):
    pass


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
            return

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
    main()
