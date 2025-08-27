import asyncio
import json
import jc.ipykernel
import jc.jupyterlab
import jc.tornado
import logging
import jc.bootstrap as cafe

logger = logging.getLogger(__name__)


async def test_jupyterlab():
    await jc.ipykernel.init()
    jc.ipykernel.patch()

    await jc.jupyterlab.init()
    jc.jupyterlab.patch()
    await jc.jupyterlab.run()
    assert jc.tornado.tornado_app is not None

    # uncomment this to check if we are blocking the asyncio loop
    # async def log():
    #     while 1:
    #         jc.jupyterlab.logger.info("running")
    #         await asyncio.sleep(1)

    # task = asyncio.create_task(log())

    body, headers, status = await jc.jupyterlab.fetch(
        cafe.Request(
            url="/_app/api/kernels",
            method="POST",
            headers=[],
        )
    )
    assert status == 201
    headers = dict(headers)
    assert headers["Content-Type"] == "application/json"
    msg = json.loads(body)
    kernel_id = msg["id"]
    assert headers["Location"] == f"/_app/api/kernels/{kernel_id}"

    reply = await jc.jupyterlab.websocket_connect(
        cafe.Request(
            url=f"/_ws/api/kernels/{kernel_id}/channels",
            method="GET",
            headers=[],
        )
    )
    assert reply["uuid"]
    assert reply["status"] == 200
