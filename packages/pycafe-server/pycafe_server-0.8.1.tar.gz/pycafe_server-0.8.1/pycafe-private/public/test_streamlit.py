import jc.streamlit
import jc.tornado
import jc.bootstrap as cafe
from streamlit.web.server.browser_websocket_handler import BrowserWebSocketHandler


jc.tornado.patch()
jc.streamlit.patch()


async def test_tornado_websocket_streamlit():
    await jc.streamlit.init()
    await jc.streamlit.run()
    reply = await jc.streamlit.websocket_connect(
        cafe.Request(
            url="/_ws/_stcore/stream",
            method="GET",
            headers=[("X-Websocket-Id", "1")],
        )
    )
    assert reply["uuid"]
    # assert reply["body"] == b'Can "Upgrade" only to "WebSocket".'
    assert reply["status"] == 200
    # assert reply["headers"]

    await jc.streamlit.websocket_send(
        reply["uuid"], b'Z\x08\n\x00\x12\x00\x1a\x00"\x00'
    )
    reply = await jc.tornado.js.send_queue.get()
    # assert len(reply) > 10
    # assert reply
