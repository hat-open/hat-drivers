from hat.drivers.cdt.target import Session


class Page:

    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self):
        return self._session

    async def enable(self):
        await self._session.call('Page.enable')

    async def disable(self):
        await self._session.call('Page.disable')

    async def navigate(self, url: str):
        await self._session.call('Page.navigate', {'url': url})

    async def reload(self, ignore_cache: bool = False):
        await self._session.call('Page.reload', {'ignoreCache': ignore_cache})
