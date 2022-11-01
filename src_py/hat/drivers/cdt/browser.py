from hat.drivers.cdt.connection import Connection


class Browser:

    def __init__(self, conn: Connection):
        self._conn = conn

    @property
    def conn(self) -> Connection:
        return self._conn

    async def close(self):
        await self._conn.call('Browser.close')
