from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
import httpx
from urllib.parse import unquote, urlencode


# equivalent to /app/i/request_proxy/route.ts
async def handle(request: Request) -> Response:
    # Extract the "uri" parameter from the query string.
    # In the Next.js code, the URL’s search part is sliced off after "?uri=".
    # Here we assume the URL is like: /?uri=encoded_base_url&key1=value1&key2=value2
    uri = request.query_params.get("uri", "")
    # Decode the entire uri string and split on "&"
    decoded = unquote(uri).split("&") if uri else []

    # Remove the first element as the base URL; the rest are key/value pairs.
    if decoded:
        base_url = decoded.pop(0)
    else:
        base_url = ""

    # Build additional query parameters from the remaining elements.
    params = {}
    for pair in decoded:
        if pair:  # skip empty strings
            # split only on the first "=" to allow "=" in values
            key, value = pair.split("=", 1)
            params[key] = value

    # Prepare the URL to forward the request to.
    forward_url = base_url + (("?" + urlencode(params)) if params else "")

    # Prepare headers for the forwarded request:
    forward_headers = {}
    for name, value in request.headers.items():
        # Look for headers starting with "pythonproxy-" and strip that prefix.
        if name.lower().startswith("pythonproxy-") and value is not None:
            new_name = name[len("pythonproxy-") :]
            forward_headers[new_name] = value

    # Get the request method and body (if not GET).
    forward_method = request.method
    forward_body = await request.body() if forward_method != "GET" else None

    # Forward the request using httpx.
    async with httpx.AsyncClient() as client:
        if forward_method == "GET":
            resp = await client.request(
                forward_method, forward_url, headers=forward_headers
            )
        else:
            resp = await client.request(
                forward_method,
                forward_url,
                headers=forward_headers,
                content=forward_body,
            )

    # Get the response content as bytes.
    response_content = resp.content

    # Prepare our response headers.
    our_response_headers = {}
    for name, value in resp.headers.items():
        # Skip headers that are not valid when content is uncompressed.
        if name.lower() not in [
            "content-encoding",
            "transfer-encoding",
            "content-length",
        ]:
            our_response_headers[f"pythonproxy-{name}"] = value

    # Set our response's content type and length.
    our_response_headers["content-type"] = "application/octet-stream;"
    our_response_headers["content-length"] = str(len(response_content))

    return Response(
        response_content, status_code=resp.status_code, headers=our_response_headers
    )
