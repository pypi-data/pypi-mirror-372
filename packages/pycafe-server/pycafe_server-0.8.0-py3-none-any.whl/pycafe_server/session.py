from __future__ import annotations

import json
import typing
from base64 import b64decode, b64encode

import itsdangerous
from itsdangerous.exc import BadSignature

from starlette.datastructures import MutableHeaders, Secret
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .cookie import Cookie


class SessionMiddleware:
    def __init__(self, app: ASGIApp, cookie: Cookie) -> None:
        self.app = app
        self.cookie = cookie

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        initial_session_was_empty = True
        initial_data: bytes | None = None

        if self.cookie.exists(connection):
            initial_session_was_empty = False  # set to False early
            # so we clear the cookie if decoding fails
            try:
                initial_data = data = self.cookie.get(connection)
                if data is not None:
                    scope["session"] = json.loads(b64decode(data))
                else:
                    scope["session"] = {}
            except BadSignature:
                scope["session"] = {}
        else:
            scope["session"] = {}

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                if scope["session"]:
                    data = b64encode(json.dumps(scope["session"]).encode("utf-8"))
                    # never set cookies if they are the same, this can otherwise clear cookies
                    # when race conditions occur (e.g. multiple requests in parallel)
                    if initial_data != data:
                        self.cookie.set(headers, data)
                elif not initial_session_was_empty:
                    self.cookie.clear(headers)
            await send(message)

        await self.app(scope, receive, send_wrapper)
