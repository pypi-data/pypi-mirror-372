import jc.ipykernel
import logging

logger = logging.getLogger(__name__)


async def test_ipykernel() -> None:
    await jc.ipykernel.init()
    jc.ipykernel.patch()
    await jc.ipykernel.run()

    import jupyter_client.manager

    # TODO: we disabled in HB channel in ipykernel for now
    import jupyter_client.channels

    def start(self):
        pass

    jupyter_client.channels.HBChannel.start = start
    jupyter_client.channels.HBChannel.is_beating = lambda self: True

    km = jupyter_client.manager.AsyncKernelManager(
        connection_file=jc.ipykernel.connection_file_path
    )

    async def _async_is_alive(self):
        return True

    jupyter_client.manager.AsyncKernelManager._async_is_alive = _async_is_alive
    logger.info("got kernel %s", km)
    client: jupyter_client.asynchronous.client.AsyncKernelClient = km.client()
    client.load_connection_file()
    logger.info("got client %s", client)
    client.start_channels()
    logger.info("started channels")
    await client.wait_for_ready(timeout=1)
    client.execute("1+1")
    reply = await client.shell_channel.get_msg(timeout=1)
    assert reply["content"]["status"] == "ok"
