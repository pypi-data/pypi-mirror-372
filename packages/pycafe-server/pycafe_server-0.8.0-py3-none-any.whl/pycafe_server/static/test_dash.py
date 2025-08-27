import jc.dash
import jc.bootstrap as cafe


async def test_dash_main():
    await jc.dash.init()
    jc.dash.patch()
    await jc.dash.run()
    body, headers, status = await jc.dash.fetch(
        cafe.Request(
            url="/_app/",
            method="GET",
            headers=[("Host", "localhost")],
        )
    )
    # assert reply["body"] == b"Hello, world"
    assert b"DashRenderer" in body
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "text/html; charset=utf-8"


async def test_dash_callback():
    await jc.dash.init()
    jc.dash.patch()
    await jc.dash.run()
    body, headers, status = await jc.dash.fetch(
        cafe.Request(
            url="/_app/_dash-update-component",
            method="POST",
            headers=[
                ("accept", "application/json"),
                ("content-type", "application/json"),
            ],
            body=b'{"output":"markdown.style","outputs":{"id":"markdown","property":"style"},"inputs":[{"id":"dropdown","property":"value"}],"changedPropIds":[]}',
        )
    )
    assert b"markdown" in body
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "application/json"


async def test_dash_dcc():
    await jc.dash.init()
    jc.dash.patch()
    await jc.dash.run()
    body, headers, status = await jc.dash.fetch(
        cafe.Request(
            url="/_app/_dash-component-suites/dash/dcc/async-dropdown.js",
            method="GET",
            headers=[("Host", "localhost")],
        )
    )
    # assert reply["body"] == b"Hello, world"
    assert b"handleTouchStart" in body
    assert status == 200
    headers = dict(headers)
    assert headers["content-type"] == "application/javascript; charset=utf-8"
