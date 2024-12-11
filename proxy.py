import json
from pathlib import Path
import collections

import aiohttp
import sanic
from sanic.log import logger as log


app = sanic.Sanic("proxy")


@app.get("/static/proxy-frontend.html")
def proxy_frontend(request: sanic.Request):
    return sanic.response.file("proxy-frontend.html")


class DictPersisted(collections.abc.MutableMapping):
    """
    [How to correctly implement the mapping protocol in Python?](https://stackoverflow.com/a/19775773/3356840)
    """
    def __init__(self, data_source: Path):
        self.data_source = data_source
        with self.data_source.open() as f:
            self.routes = json.load(f)

    def _persist(self):
        with self.data_source.open('w') as f:
            json.dump(self.routes, f)

    def __getitem__(self, key):
        return self.routes.__getitem__(key)

    def __setitem__(self, key, value):
        self.routes.__setitem__(key, value)
        self._persist()

    def __delitem__(self, key):
        self.routes.__delitem__(key)
        self._persist()

    def __iter__(self):
        return self.routes.__iter__()

    def __len__(self):
        return self.routes.__len__()



from sanic.views import HTTPMethodView

class ProxyRoutes(HTTPMethodView):
    def __init__(self, data_source: Path):
        self.routes = DictPersisted(data_source)

    async def get(self, request):
        return sanic.response.json(dict(self.routes))

    async def post(self, request):
        self.routes.clear()
        self.routes.update(request.json)
        return sanic.response.json({}, status=201)

    async def put(self, request):
        self.routes.update(request.json)
        return sanic.response.json({}, status=201)

    async def delete(self, request):
        for key in request.json.keys():
            del self.routes[key]
        return sanic.response.json({}, status=201)

# BROKEN :( I want a view with state ... gonna have to punch this ...
proxy_routes = ProxyRoutes(Path('proxy-routing.json'))
app.add_route(ProxyRoutes.as_view(), "/_proxy")


@app.route("/<path:path>", methods=tuple(map(str, sanic.HTTPMethod)))
async def proxy(request: sanic.Request, path: str):
    host = request.headers.pop('host', '')
    log.info(f'Lookup {host=} {path=}')

    new_host = proxy_routes.routes.get(host)  # BROKEN
    if not new_host:
        message = f'FAIL: no route setup for {host=}'
        log.info(message)
        return sanic.response.json({'error': message}, status=400)

    url = f"{new_host}{request.raw_url.decode('utf8')}"
    log.info(f'Routing {host=} {new_host=} {path=} {url=}')

    # AIOHTTP
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.method,
            url=url,
            headers=request.headers,
            data=request.body,
            #auto_decompress=False,
            ssl=False,  # Ignore all SSL certificates
        ) as response:
            _response = await request.respond(
                status=response.status,
                headers=response.headers,
            )
            async for chunk in response.content.iter_chunked(pow(2, 16)):
                await _response.send(chunk)
            await _response.eof()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, dev=True, access_log=True)  #workers=4, auto_reload=True
