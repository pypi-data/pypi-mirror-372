import jc.solara
import jc.bootstrap as cafe

jc.solara.patch()


async def test_solara_root():
    await jc.solara.init()
    jc.solara.patch()
    await jc.solara.run()
    body, headers, status = await jc.solara.fetch(
        cafe.Request(
            url="/_app/",
            method="GET",
        )
    )
    assert b"Solara" in body
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "text/html; charset=utf-8"


async def test_solara_static():
    await jc.solara.init()
    await jc.solara.run()
    body, headers, status = await jc.solara.fetch(
        cafe.Request(
            url="/_app/static/highlight.css",
            method="GET",
        )
    )
    assert b"la" in body
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "text/css; charset=utf-8"


async def test_solara_websocket():
    await jc.solara.init()
    await jc.solara.run()
    reply = await jc.solara.websocket_connect(
        cafe.Request(
            url="/_ws/jupyter/api/kernels/solara-id/channels?session_id=1e80eec6-2e1e-4688-b34c-cb05e2a21977",
            method="GET",
            headers=[
                ("cookie", "solara-session-id=a7834b71-3247-426b-b9dd-5b2e5329c53c;")
            ],
        )
    )
    assert reply["uuid"]
    assert reply["status"] == 200
    # assert reply["headers"]
    import json

    msg = json.dumps(
        {
            "buffers": [],
            "channel": "shell",
            "content": {},
            "header": {
                "date": "2023-07-06T09:45:04.804Z",
                "msg_id": "5374ed6a-3a39-401a-9fd9-9603d7ff9c70",
                "msg_type": "kernel_info_request",
                "session": "1e80eec6-2e1e-4688-b34c-cb05e2a21977",
                "username": "",
                "version": "5.2",
            },
            "metadata": {},
            "parent_header": {},
        }
    )
    await jc.solara.websocket_send(reply["uuid"], msg)
    reply = await jc.solara.js.send_queue.get()
    reply = json.loads(reply)
    assert "header" in reply
    # assert len(reply) > 10
    # assert reply
