from base64 import b64decode, b64encode
import json
import typing
import itsdangerous
from starlette.datastructures import MutableHeaders, Secret
from starlette.types import ASGIApp, Message, Receive, Scope, Send
from starlette.requests import HTTPConnection


class Cookie:
    def __init__(
        self,
        name: str,
        max_age: int | None = 14 * 24 * 60 * 60,  # 14 days, in seconds
        path: str = "/",
        same_site: typing.Literal["lax", "strict", "none"] = "lax",
        secure: bool = False,
        domain: str | None = None,
        secret_key: str | Secret | None = None,
    ):
        self.name = name
        self.max_age = max_age
        self.path = path
        self.signer = (
            itsdangerous.TimestampSigner(str(secret_key)) if secret_key else None
        )
        self.security_flags = "httponly; samesite=" + same_site
        if secure:  # Secure flag can be used HTTPS or localhost
            self.security_flags += "; secure"
        if domain is not None:
            self.security_flags += f"; domain={domain}"

    def get_dict(self, connection: "HTTPConnection") -> dict | None:
        data = self.get(connection)
        return json.loads(b64decode(data)) if data else None

    def set_dict(self, headers: MutableHeaders, data: dict) -> None:
        bytes_data = b64encode(json.dumps(data).encode("utf-8"))
        self.set(headers, bytes_data)

    def set(self, headers: MutableHeaders, data: bytes) -> None:
        data_cookie = self.signer.sign(data) if self.signer else data
        header_value = (
            "{session_cookie}={data}; path={path}; {max_age}{security_flags}".format(
                session_cookie=self.name,
                data=data_cookie.decode("utf-8"),
                path=self.path,
                max_age=f"Max-Age={self.max_age}; " if self.max_age else "",
                security_flags=self.security_flags,
            )
        )
        headers.append("Set-Cookie", header_value)

    def exists(self, connection: "HTTPConnection") -> bool:
        return self.name in connection.cookies

    def get(self, connection: "HTTPConnection") -> bytes | None:
        if not self.exists(connection):
            return None
        data = connection.cookies[self.name].encode("utf-8")
        if self.signer:
            try:
                return self.signer.unsign(data, max_age=self.max_age)
            except itsdangerous.SignatureExpired:
                return None
        else:
            return data

    def clear(self, headers: MutableHeaders) -> None:
        header_value = (
            "{session_cookie}={data}; path={path}; {expires}{security_flags}".format(
                session_cookie=self.name,
                data="null",
                path=self.path,
                expires="expires=Thu, 01 Jan 1970 00:00:00 GMT; ",
                security_flags=self.security_flags,
            )
        )
        headers.append("Set-Cookie", header_value)
