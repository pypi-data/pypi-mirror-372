import micropip
import jc.cafe


async def init(pipliteWheelUrl=None, pipliteUrls=None):
    import js

    global kernel
    print("WebWorker: jc.jupyter_kernel: main 1")
    js.importScripts("/worker.iife.js")
    # js.importScripts("https://unpkg.com/comlink@4.4.1/dist/umd/comlink.js")
    print("WebWorker: jc.jupyter_kernel: main 2")
    # print("jc.jupyter_kernel.main")
    await micropip.install(
        "/jupyterlite_pyodide_kernel-0.0.8-py3-none-any.whl", keep_going=True
    )
    await micropip.install("/ipykernel-6.9.2-py3-none-any.whl", keep_going=True)
    await micropip.install("/pyodide_kernel-0.0.8-py3-none-any.whl", keep_going=True)
    await micropip.install(["sqlite3"], keep_going=True)
    await micropip.install(["ipython"], keep_going=True)
    print("WebWorker: jc.jupyter_kernel: main 3")
    # this causes sideffects we want


async def install():
    import pyodide_kernel

    # await jc.bootstrap.download_dev()
    # await jc.bootstrap.prepare_runtime(files)
    print("WebWorker: jc.jupyter_kernel: main 4")
    # TODO: should we change to /drive?
    # import os
    # os.chdir("${this._localPath}");

    # sys.modules["piplite"] = micropip
    # sys.modules["piplite.piplite"] = micropip

    # await micropip.install(['sqlite3'], keep_going=True);
    # await micropip.install(['ipykernel'], keep_going=True);
    # await micropip.install(['pyodide_kernel'], keep_going=True);
    # await micropip.install(['ipython'], keep_going=True);

    # await micropip.install(pipliteWheelUrl, keep_going=True)
    # import piplite.piplite
    # piplite.piplite._PIPLITE_DISABLE_PYPI =False # ${disablePyPIFallback ? 'True' : 'False'}
    # piplite.piplite._PIPLITE_URLS = pipliteUrls
    # await piplite.install(['sqlite3'], keep_going=True);
    # await piplite.install(['ipykernel'], keep_going=True);
    # await piplite.install(['pyodide_kernel'], keep_going=True);
    # await piplite.install(['ipython'], keep_going=True);
    # await jc.bootstrap.download_dev()
    # await jc.bootstrap.prepare_runtime()
