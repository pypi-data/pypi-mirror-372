from starlette.applications import Starlette
from starlette.responses import JSONResponse, HTMLResponse, Response
from starlette.routing import Route

import jc.starlette
import jc.bootstrap as cafe
import asgi


jc.starlette.patch()


async def homepage(request):
    return JSONResponse({"hello": "world"})


async def html(request):
    return HTMLResponse("<html><head></head><body><h1>Hello, world!</h1></body></html>")


async def js_snippet(request):
    return Response('console.log("hello world")', media_type="application/javascript")


app = Starlette(
    debug=True,
    routes=[
        Route("/", homepage),
        Route("/js", js_snippet),
        Route("/html", html),
    ],
)
asgi.app = app


async def test_starlette_http():
    await jc.starlette.init()
    body, headers, status = await jc.starlette.fetch(
        cafe.Request(
            url="/_app/",
            method="GET",
            headers=[("Host", "localhost")],
        )
    )
    # assert reply["body"] == b"Hello, world"
    assert status == 200
    assert body == b'{"hello":"world"}'
    headers = dict(headers)
    assert headers["content-type"] == "application/json"


async def test_starlette_websocket_patch():
    jc.starlette.tornado_app = app
    await jc.starlette.init()
    body, headers, status = await jc.starlette.fetch(
        cafe.Request(
            url="/_app/html",
            method="GET",
            headers=[],
        )
    )
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "text/html; charset=utf-8"
    assert b"WebSocket" in body
