import json
from pathlib import Path
from functools import cached_property
import collections
#import httpx
import aiohttp

import sanic
from sanic.log import logger as log
#from sanic_ext import Extend

app = sanic.Sanic("proxy")

#app.config.CORS_ORIGINS = "http://foobar.com,http://bar.com"
#Extend(app)

#app.config.cors_origins = "*"
#from sanic_ext.extensions.http.cors import add_cors
#app.config.CORS_ORIGINS = ["*"]
#add_cors(app)

#@app.get("/test/")
#def test(request):
#    return sanic.response.json({'hello': 'world'})

#@app.get("/")
#async def root(request):
#    return sanic.response.redirect('/static/proxy-frontend.html')

#app.static("/static/", ".")


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
        params = request.json
        self.routes[params['host']] = params['target']
        return sanic.response.json({}, status=201)

    async def delete(self, request):
        params = request.json
        del self.routes[params['host']]
        return sanic.response.json({}, status=201)

proxy_routes = ProxyRoutes(Path('proxy-routing.json'))
app.add_route(proxy_routes.as_view(), "/_proxy")


@app.route("/<path:path>", methods=tuple(map(str, sanic.HTTPMethod)))
async def proxy(request: sanic.Request, path: str):
    host = request.headers.pop('host', '')
    log.info(f'Lookup {host=} {path=}')

    new_host = proxy_routes.routes.get(host)
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

    # HTTPX
    # always decodes gzip response, making this problematic for passthough
    # async with httpx.AsyncClient() as client:
    #     response = await client.request(
    #         method=request.method,
    #         url=f"{new_host}{request.raw_url.decode('utf8')}",
    #         headers=request.headers,
    #         content=request.body
    #     )
    #     return sanic.response.ResponseStream(status=response.status_code, headers=response.headers, streaming_fn=response.aiter_raw())
    #     #return sanic.response.HTTPResponse(status=response.status_code, headers=response.headers, body=response.aiter_raw())
    #breakpoint()

    #return sanic.response.json({'path': path})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, dev=True, access_log=True)  #workers=4, auto_reload=True
