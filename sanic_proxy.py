from abc import ABC, abstractmethod
from collections.abc import Mapping
from types import MappingProxyType
from typing import override

import sanic


class AbstractSanicProxy(ABC):
    @abstractmethod
    async def proxy(
        self,
        request: sanic.Request,
        url: str,
        additional_headers: Mapping[str, str] = MappingProxyType({}),
    ) -> None: ...


class HTTPXSanicProxy(AbstractSanicProxy):
    def __init__(self, timeout=3.0):
        import httpx
        self.session = httpx.AsyncClient(
            timeout=timeout,
            verify=False,
            follow_redirects=True,
        )

    @override
    async def proxy(
        self,
        request: sanic.Request,
        url: str,
        additional_headers: Mapping[str, str] = MappingProxyType({}),
    ) -> None:
        async with self.session.stream(
            url=url,
            method=request.method,
            headers={**request.headers, **additional_headers},
            content=request.body,
        ) as _response:
            # `request.respond` is a special case stream and does not need to be `return`ed
            response_from_sanic = await request.respond(
                status=_response.status_code,
                headers=_response.headers,
            )
            try:
                async for chunk in _response.aiter_raw(pow(2, 16)):
                    await response_from_sanic.send(chunk)
            except Exception as ex:
                await _response.aclose()
                raise ex  # with raise an exception though sanic's normal flow
            else:  # the stream completed successfully without exception
                await response_from_sanic.eof()


class AioHttpSanicProxy(AbstractSanicProxy):
    def __init__(self, timeout=3.0):
        import aiohttp
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            auto_decompress=False,
        )
        # follow_redirects=True,

    @override
    async def proxy(
        self,
        request: sanic.Request,
        url: str,
        additional_headers: Mapping[str, str] = MappingProxyType({}),
    ) -> None:
        async with self.session.request(
            method=request.method,
            url=url,
            headers={**request.headers, **additional_headers},
            data=request.body,
            ssl=False,  # Ignore all SSL certificates
        ) as response:
            response_from_sanic = await request.respond(
                status=response.status,
                headers=response.headers,
            )
            async for chunk in response.content.iter_chunked(pow(2, 16)):
                await response_from_sanic.send(chunk)
            await response_from_sanic.eof()
