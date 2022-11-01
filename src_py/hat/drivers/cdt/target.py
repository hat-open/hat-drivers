import typing

from hat import json
from hat.drivers.cdt.connection import SessionId, Connection


TargetId = str


class TargetInfo(typing.NamedTuple):
    target_id: TargetId
    type: str
    title: str
    url: str
    attached: bool


async def getTargetInfos(conn: Connection
                         ) -> typing.List[TargetInfo]:
    res = await conn.call('Target.getTargets')
    return [TargetInfo(target_id=i['targetId'],
                       type=i['type'],
                       title=i['title'],
                       url=i['url'],
                       attached=i['attached'])
            for i in res['targetInfos']]


async def createTarget(conn: Connection,
                       url: str = '',
                       width: typing.Optional[int] = None,
                       height: typing.Optional[int] = None,
                       new_window: bool = False,
                       background: bool = False
                       ) -> 'Target':
    req = {'url': url,
           'new_window': new_window,
           'background': background}
    if width is not None:
        req['width'] = width
    if height is not None:
        req['height'] = height
    res = await conn.call('Target.createTarget', req)
    return Target(conn, res['targetId'])


class Session:

    def __init__(self,
                 conn: Connection,
                 session_id: SessionId):
        self._conn = conn
        self._session_id = session_id

    @property
    def conn(self) -> Connection:
        return self._conn

    @property
    def session_id(self) -> SessionId:
        return self._session_id

    async def call(self,
                   method: str,
                   params: json.Data = {}
                   ) -> json.Data:
        return await self._conn.call(method, params, self._session_id)

    async def detach(self):
        await self._conn.call('Target.detachFromTarget',
                              {'sessionId': self._session_id})


class Target:

    def __init__(self,
                 conn: Connection,
                 target_id: TargetId):
        self._conn = conn
        self._target_id = target_id

    @property
    def conn(self) -> Connection:
        return self._conn

    @property
    def target_id(self):
        return self._target_id

    async def activate(self):
        await self._conn.call('Target.activateTarget',
                              {'targetId': self._target_id})

    async def attach(self) -> Session:
        res = await self._conn.call('Target.attachToTarget',
                                    {'targetId': self._target_id,
                                     'flatten': True})
        return Session(self._conn, res['sessionId'])

    async def close(self):
        await self._conn.call('Target.closeTarget',
                              {'targetId': self._target_id})
