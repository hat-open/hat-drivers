from hat import aio


async def create_ping_endpoint(local_host: str | None = None):
    raise NotImplementedError()


class PingEndpoint(aio.Resource):

    @property
    def async_group(self) -> aio.Group:
        raise NotImplementedError()

    async def ping(self, remote_host: str):
        raise NotImplementedError()
