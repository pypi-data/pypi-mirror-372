from functools import cache
import json
import logging
import sys
import jwt
import typing
import requests
from starlette.authentication import (
    AuthCredentials,
    AuthenticationBackend,
    AuthenticationError,
    SimpleUser,
)
from starlette.routing import Router
from starlette.requests import HTTPConnection
from starlette.types import ASGIApp, Receive, Scope, Send
from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from starlette.datastructures import MutableHeaders


from starlette.responses import (
    PlainTextResponse,
    Response,
    RedirectResponse,
    JSONResponse,
)
from starlette.authentication import UnauthenticatedUser
from starlette.requests import Request
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import base64

from .cookie import Cookie
from . import config

logger = logging.getLogger(__name__)

access_token_cookie = Cookie(
    "pycafe_access_token",
    same_site="none",
    secure=True,
    secret_key=config.PYCAFE_SESSION_SECRET_KEY,
    max_age=int(config.PYCAFE_COOKIE_MAX_AGE),
)
id_token_cookie = Cookie(
    "pycafe_id_token",
    same_site="none",
    secure=True,
    secret_key=config.PYCAFE_SESSION_SECRET_KEY,
    max_age=int(config.PYCAFE_COOKIE_MAX_AGE),
)
refresh_token_cookie = Cookie(
    "pycafe_refresh_token",
    same_site="none",
    secure=True,
    secret_key=config.PYCAFE_SESSION_SECRET_KEY,
    max_age=int(config.PYCAFE_COOKIE_MAX_AGE),
)
userinfo_cookie = Cookie(
    "pycafe_userinfo",
    same_site="none",
    secure=True,
    secret_key=config.PYCAFE_SESSION_SECRET_KEY,
    max_age=int(config.PYCAFE_COOKIE_MAX_AGE),
)


def load_rsa_key(n, e):
    """Construct an RSA public key from modulus and exponent in JWKS format."""
    modulus = int.from_bytes(base64.urlsafe_b64decode(n + "=="), "big")
    exponent = int.from_bytes(base64.urlsafe_b64decode(e + "=="), "big")
    public_key = rsa.RSAPublicNumbers(exponent, modulus).public_key(default_backend())
    return public_key


@cache
def get_aws_alb_public_key(kid: str, region: str) -> str:
    url = "https://public-keys.auth.elb." + region + ".amazonaws.com/" + kid
    req = requests.get(url)
    pub_key = req.text
    return pub_key


def decode_jwt_on_alb(encoded_jwt: str, region=config.PYCAFE_SERVER_AWS_REGION):
    # Step 1: Validate the signer
    expected_alb_arn = "arn:aws:elasticloadbalancing:region-code:account-id:loadbalancer/app/load-balancer-name/load-balancer-id"

    jwt_headers = encoded_jwt.split(".")[0]
    decoded_jwt_headers_bytes = base64.b64decode(jwt_headers + "==")
    decoded_jwt_headers = decoded_jwt_headers_bytes.decode("utf-8")
    decoded_json = json.loads(decoded_jwt_headers)
    received_alb_arn = decoded_json["signer"]

    # TODO: we need to verify the signer
    # assert expected_alb_arn == received_alb_arn, "Invalid Signer"

    # Step 2: Get the key id from JWT headers (the kid field)
    kid = decoded_json["kid"]

    # Step 3: Get the public key from regional endpoint
    pub_key = get_aws_alb_public_key(kid, region)

    # Step 4: Get the payload
    # TODO: we want to know if aud and iss are set in the jwt
    return jwt.decode(
        encoded_jwt,
        pub_key,
        algorithms=["ES256", "RS256"],
        options={"verify_aud": False, "verify_iss": False},
    )


def decode_jwt(token):
    rsa_key = {}
    headers = jwt.get_unverified_header(token)
    if config.jwks_client is None:
        raise ValueError(
            "No JWKS client available to verify the token, please set PYCAFE_SERVER_JWKS_URL"
        )
    for key in config.jwks_client["keys"]:
        if key["kid"] == headers["kid"]:
            rsa_key = load_rsa_key(key["n"], key["e"])
            break

    if not rsa_key:
        raise ValueError("Public key not found for the provided token.")

    # Decode the JWT and verify its claims
    decoded = jwt.decode(
        token,
        rsa_key,
        algorithms=["RS256"],
        audience=config.PYCAFE_SERVER_CLIENT_ID,
    )
    return decoded


def get_userinfo(request: HTTPConnection) -> dict | None:
    if config.auth_using_proxy():
        headers = request.headers

        identity: str | None = None
        email: str | None = None
        userinfo: dict | None = None

        if config.PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY:
            identity = headers.get(config.PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY)
            if identity is None:
                print(
                    f"No header {config.PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY} found, possible headers are {list(headers.keys())}",
                    file=sys.stderr,
                )

        if config.PYCAFE_SERVER_PROXY_AUTH_HEADER_EMAIL:
            email = headers.get(config.PYCAFE_SERVER_PROXY_AUTH_HEADER_EMAIL)
            if email is None:
                print(
                    f"No header {config.PYCAFE_SERVER_PROXY_AUTH_HEADER_EMAIL} found, possible headers are {list(headers.keys())}",
                    file=sys.stderr,
                )

        if config.PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT:
            jwt_data = headers.get(config.PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT)
            if jwt_data is None:
                print(
                    f"No header {config.PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT} found, possible headers are {list(headers.keys())}",
                    file=sys.stderr,
                )
            if jwt_data:
                if jwt_data.startswith("Bearer "):
                    jwt_data = jwt_data[7:].strip()
                userinfo = decode_jwt(jwt_data)

        if userinfo is None:
            if identity is None:
                return None
                # we previously raised an error here, but for the signing from the command line using api keys
                # we need to support unauthenticated users as well
                # raise ValueError(
                #     "No identity found in headers or PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY not configured, and not userinfo found or PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT not configured"
                # )
            else:
                userinfo = {
                    "user_id": identity,
                    "email": email,
                }
    else:
        userinfo = userinfo_cookie.get_dict(request)
        if userinfo is None:
            return None
        else:
            client_id = request.session.get("client_id")
            # if we changed the oauth provider, we should not use the old user
            if client_id is not None and client_id != config.PYCAFE_SERVER_CLIENT_ID:
                logger.error(
                    "OIDC error, client id mismatch (%s != %s), did you change the oauth provider? We are assuming you are not logged in now",
                    client_id,
                    config.PYCAFE_SERVER_CLIENT_ID,
                )
                userinfo = None
            else:
                assert userinfo is not None
                aud = userinfo.get("aud")
                if aud is not None and aud != config.PYCAFE_SERVER_CLIENT_ID:
                    logger.error(
                        "OIDC error, audience mismatch (%s != %s), did you change the oauth provider? We are assuming you are not logged in now",
                        aud,
                        config.PYCAFE_SERVER_CLIENT_ID,
                    )
                    userinfo = None

    return userinfo


# only provides request.user.is_authenticated
class AuthBackend(AuthenticationBackend):
    async def authenticate(self, conn: HTTPConnection):
        userinfo = get_userinfo(conn)
        if userinfo is None:
            return AuthCredentials(), UnauthenticatedUser()
        else:
            username = "noname"
            return AuthCredentials(["authenticated"]), SimpleUser(username)


oauth = OAuth(config)
oauth.register(name="pycafe_server")

app = Router()


@app.route("/_login")
async def login_via_pycafe(request: Request):
    if "next_url" in request.query_params:
        request.session["next_url"] = request.query_params["next_url"]
    client: StarletteOAuth2App = oauth.create_client("pycafe_server")
    redirect_uri = request.url_for("authorize_pycafe")
    # we send the client id, since that might change during testing, and that means
    # get_userinfo should not return a userinfo if the client id does not match
    request.session["client_id"] = config.PYCAFE_SERVER_CLIENT_ID
    return await client.authorize_redirect(request, redirect_uri)


@app.route("/_authorize")
async def authorize_pycafe(request: Request):
    client: StarletteOAuth2App = oauth.create_client("pycafe_server")
    base_url = str(request.base_url)
    org_url = request.session.pop("next_url", base_url)
    token = await client.authorize_access_token(request)
    headers = MutableHeaders(scope=request.scope)

    id_token = token.get("id_token")
    if id_token is None:
        raise ValueError("No id_token found in token")
    id_token_cookie.set_dict(headers, id_token)
    access_token = token.get("access_token")
    if access_token is None:
        raise ValueError("No access_token found in token")
    access_token_cookie.set_dict(headers, access_token)
    refresh_token = token.get("refresh_token")
    if refresh_token is None:
        refresh_token_cookie.clear(headers)
    else:
        refresh_token_cookie.set_dict(headers, refresh_token)
    # we might be able to skip the userinfo, but we'd have to look into
    # what authorize_access_token does exactly
    userinfo = token.get("userinfo")
    if userinfo is None:
        raise ValueError(
            "No userinfo found in token, did you forgot to configure PYCAFE_SERVER_CLIENT_KWARGS?"
        )
    userinfo_cookie.set_dict(headers, userinfo)
    id_field = config.get("PYCAFE_SERVER_USER_ID_FIELD", default="email")
    user_id = userinfo.get(id_field)
    if user_id is None:
        print(
            f"no value found in userinfo with key PYCAFE_SERVER_USER_ID_FIELD={id_field}, possible fields are {list(userinfo.keys())}"
        )
        return JSONResponse(
            {
                "error": "Could not find a field in the auth data to uniquely describe the user, see server logs and configuration"
            },
            status_code=500,
        )
    else:
        return RedirectResponse(url=org_url, headers=headers)


@app.route("/_logout")
async def logout(request: Request):
    client_id = config.PYCAFE_SERVER_CLIENT_ID
    logout_url = (
        config.PYCAFE_SERVER_OAUTH_BASE_URL + config.PYCAFE_SERVER_OAUTH_LOGOUT_PATH
    )
    if "next_url" in request.query_params:
        request.session["next_url"] = request.query_params["next_url"]
    redirect_uri = request.url_for("logout_callback")
    # there is no standard for logout urls, so we
    # use the most common url parameters to get back to the /_logout_return endpoint
    # works for auth0 and fief, maybe more?
    return RedirectResponse(
        f"{logout_url}?returnTo={redirect_uri}&redirect_uri={redirect_uri}&post_logout_redirect_uri={redirect_uri}&client_id={client_id}"
    )


@app.route("/_logout_callback")
async def logout_callback(request: Request):
    next_url = request.session.pop("next_url", "/")
    # ideally, we only remove these:
    headers = MutableHeaders()
    access_token_cookie.clear(headers)
    id_token_cookie.clear(headers)
    refresh_token_cookie.clear(headers)
    userinfo_cookie.clear(headers)
    # authlib sometimes leaves some stuff in the session on failed logins
    # so we clear it all
    request.session.clear()
    return RedirectResponse(next_url, headers=headers)
