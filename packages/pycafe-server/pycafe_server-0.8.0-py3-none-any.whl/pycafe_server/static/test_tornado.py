import asyncio
import jc.tornado
import jc.bootstrap as cafe
import tornado.websocket
import tornado
import tornado.web


jc.tornado.patch()


async def test_tornado_http_basic():
    class MainHandler(tornado.web.RequestHandler):
        async def get(self):
            # self.write("Hello, world")
            self.write("Hello, world")
            self.flush()
            await asyncio.sleep(1)
            self.write("Hello, world2")
            self.finish()

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
        ]
    )

    jc.tornado.tornado_app = app
    await jc.tornado.init()
    body, headers, status = await jc.tornado.fetch(
        cafe.Request(
            url="/",
            method="GET",
            headers=[("Host", "localhost")],
        )
    )
    # assert reply["body"] == b"Hello, world"
    assert body == b"Hello, world"
    assert status == 200
    assert headers[1] == ("Content-Type", "text/html; charset=UTF-8")


# async def test_tornado_http_websocket_patch():
#     # first js assets needs to be patched
#     class MainHandler(tornado.web.RequestHandler):
#         def get(self):
#             self.set_header("Content-Type", "application/javascript")
#             self.write("---")

#     app = tornado.web.Application([
#         ("/", MainHandler),
#     ])
#     jc.tornado.tornado_app = app
#     await jc.tornado.init()
#     body, headers, status = await jc.tornado.fetch(cafe.Request(
#         url = "/",
#         method = "GET",
#         headers = [],
#     ))
#     assert b"WebSocket" in body


# async def test_tornado_websocket():
#     class EchoWebSocket(tornado.websocket.WebSocketHandler):
#         def open(self):
#             print("WebSocket opened")

#         def on_message(self, message):
#             self.write_message(u"You said: " + message)

#         def on_close(self):
#             print("WebSocket closed")

#     app = tornado.web.Application([
#         ("/ws", EchoWebSocket),
#     ])

#     jc.tornado.tornado_app = app
#     await jc.tornado.init()
#     reply = await jc.tornado.websocket_connect(cafe.Request(
#         url = "/ws",
#         method = "GET",
#         headers = [],
#     ))
#     assert reply["uuid"]
#     assert reply["status"] == 200
#     assert reply["headers"]

#     await jc.tornado.websocket_send(reply["uuid"], 'cafe!')
#     await jc.tornado.websocket_send(reply["uuid"], 'cafe2!')
#     reply1 = await jc.tornado.js.send_queue.get()
#     assert reply1 == 'You said: cafe!'
#     reply2 = await jc.tornado.js.send_queue.get()
#     assert reply2 == 'You said: cafe2!'
