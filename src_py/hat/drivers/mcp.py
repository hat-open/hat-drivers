import base64
import collections
import typing

import aiohttp.web

from hat import aio
from hat import json


class Tool(typing.NamedTuple):
    name: str
    title: str | None
    description: str | None
    input_schema: json.Object
    output_schema: json.Object | None
    call_cb: aio.AsyncCallable[[json.Object | None], json.Object]


class Server:

    def __init__(self,
                 name: str,
                 version: str = '1.0.0',
                 path: str = '/',
                 cache_ttl: float = 60 * 60):
        self._meta = {
            'io.modelcontextprotocol/serverInfo': {'name': name,
                                                   'version': version}}
        self._route = aiohttp.web.post(path, self._process)
        self._cache_ttl_ms = round(cache_ttl * 1000)
        self._tools = {}

    def route(self) -> aiohttp.web.RouteDef:
        return self._route

    def add_tool(self, tool: Tool):
        self._tools[tool.name] = tool

    async def _process(self, req):
        jsonrpc_id = None

        try:
            try:
                body = await req.json()

            except Exception:
                raise _McpParseError()

            if (not isinstance(body, dict) or
                    body.get('jsonrpc') != '2.0' or
                    not isinstance(body.get('method'), str)):
                raise _McpInvalidRequestError()

            if 'id' not in body:
                return aiohttp.web.Response(status=202)

            jsonrpc_id = body['id']
            if (not isinstance(jsonrpc_id, (str, int)) or
                    isinstance(jsonrpc_id, bool)):
                raise _McpInvalidRequestError()

            try:
                meta = body['params']['_meta']
                if not isinstance(meta, dict):
                    raise Exception()

            except Exception:
                raise _McpInvalidRequestError()

            try:
                version = req.headers.getone('MCP-Protocol-Version')

                if meta['io.modelcontextprotocol/protocolVersion'] != version:
                    raise Exception()

            except Exception:
                raise _McpHeaderMismatchError()

            if version != _supported_version:
                raise _McpUnsupportedProtocolVersionError(version)

            try:
                method = req.headers.getone('Mcp-Method')

                if method != body['method']:
                    raise Exception()

            except Exception:
                raise _McpHeaderMismatchError()

            try:
                if body['method'] == 'server/discover':
                    result = self._process_server_discover()

                elif body['method'] == 'tools/list':
                    result = self._process_tools_list()

                elif body['method'] == 'tools/call':
                    result = await self._process_tools_call(req.headers,
                                                            body['params'])

                else:
                    raise _McpMethodNotFoundError()

                data = {'jsonrpc': '2.0',
                        'id': jsonrpc_id,
                        'result': {
                            '_meta': self._meta,
                            'resultType': 'complete',
                            **result}}

                return aiohttp.web.json_response(data)

            except _McpError:
                raise

            except Exception:
                raise _McpInternalError()

        except _McpError as e:
            data = {'jsonrpc': '2.0',
                    'error': {'code': e.jsonrpc_code,
                              'message': e.message}}

            if jsonrpc_id is not None:
                data['id'] = jsonrpc_id

            if e.data is not None:
                data['error']['data'] = e.data

            return aiohttp.web.json_response(data, status=e.http_code)

        except Exception:
            raise aiohttp.web.HTTPInternalServerError()

    def _process_server_discover(self):
        capabilities = {}

        if self._tools:
            capabilities['tools'] = {'listChanged': False}

        return {'supportedVersions': [_supported_version],
                'capabilities': capabilities,
                'ttlMs': self._cache_ttl_ms,
                'cacheScope': 'public'}

    def _process_tools_list(self):
        tools = collections.deque()

        for tool in self._tools.values():
            data = {'name': tool.name,
                    'inputSchema': tool.input_schema}

            if tool.title is not None:
                data['title'] = tool.title

            if tool.description is not None:
                data['description'] = tool.description

            if tool.output_schema is not None:
                data['outputSchema'] = tool.output_schema

            tools.append(data)

        return {'tools': list(tools),
                'ttlMs': self._cache_ttl_ms,
                'cacheScope': 'public'}

    async def _process_tools_call(self, headers, params):
        try:
            tool = self._tools[params['name']]

            args = params.get('arguments')
            if args is not None and not isinstance(args, dict):
                raise Exception()

        except Exception:
            raise _McpInvalidParamsError()

        try:
            name = _decode_header_value(headers.getone('Mcp-Name'))

            if name != params['name']:
                raise Exception()

        except Exception:
            raise _McpHeaderMismatchError()

        try:
            result = await aio.call(tool.call_cb, args)

        except Exception as e:
            return {'content': [{'type': 'text',
                                 'text': str(e)}],
                    'isError': True}

        if not isinstance(result, dict):
            raise _McpInternalError()

        return {'content': [{'type': 'text',
                             'text': json.encode(result)}],
                'structuredContent': result}


def _decode_header_value(value):
    if value.startswith('=?base64?') and value.endswith('?='):
        return base64.b64decode(value[9:-2]).decode('utf-8')

    return value


class _McpError(Exception):

    def __init__(self,
                 http_code: int,
                 jsonrpc_code: int,
                 message: str,
                 data: json.Object | None = None):
        super().__init__(message)

        self._http_code = http_code
        self._jsonrpc_code = jsonrpc_code
        self._message = message
        self._data = data

    @property
    def http_code(self) -> int:
        return self._http_code

    @property
    def jsonrpc_code(self) -> int:
        return self._jsonrpc_code

    @property
    def message(self) -> str:
        return self._message

    @property
    def data(self) -> json.Object | None:
        return self._data


class _McpParseError(_McpError):

    def __init__(self):
        super().__init__(http_code=400,
                         jsonrpc_code=-32700,
                         message='Parse error')


class _McpInvalidRequestError(_McpError):

    def __init__(self):
        super().__init__(http_code=400,
                         jsonrpc_code=-32600,
                         message='Invalid request')


class _McpHeaderMismatchError(_McpError):

    def __init__(self):
        super().__init__(http_code=400,
                         jsonrpc_code=-32020,
                         message='Header mismatch')


class _McpUnsupportedProtocolVersionError(_McpError):

    def __init__(self, requested_version: str):
        super().__init__(http_code=400,
                         jsonrpc_code=-32022,
                         message='Unsupported protocol version',
                         data={'supported': [_supported_version],
                               'requested': requested_version})


class _McpMethodNotFoundError(_McpError):

    def __init__(self):
        super().__init__(http_code=404,
                         jsonrpc_code=-32601,
                         message='Method not found')


class _McpInvalidParamsError(_McpError):

    def __init__(self):
        super().__init__(http_code=400,
                         jsonrpc_code=-32602,
                         message='Invalid params')


class _McpInternalError(_McpError):

    def __init__(self):
        super().__init__(http_code=500,
                         jsonrpc_code=-32603,
                         message='Internal error')


_supported_version = '2026-07-28'
