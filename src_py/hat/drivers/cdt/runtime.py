import typing

from hat import json

from hat.drivers.cdt.target import Session


RemoteObjectId = str


class RemoteObject(typing.NamedTuple):
    type: str
    subtype: str | None
    value: json.Data | None
    id: RemoteObjectId | None


class Runtime:

    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self):
        return self._session12

    async def enable(self):
        await self._session.call('Runtime.enable')

    async def disable(self):
        await self._session.call('Runtime.disable')

    async def evaluate(self,
                       expression: str,
                       await_promise: bool = False
                       ) -> RemoteObject:
        res = await self._session.call('Runtime.evaluate',
                                       {'expression': expression,
                                        'awaitPromise': await_promise})
        if 'exceptionDetails' in res:
            raise Exception(res['exceptionDetails']['text'])
        return RemoteObject(type=res['result']['type'],
                            subtype=res['result'].get('subtype'),
                            value=res['result'].get('value'),
                            id=res['result'].get('objectId'))
