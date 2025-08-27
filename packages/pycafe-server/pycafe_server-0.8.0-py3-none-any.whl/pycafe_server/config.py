from ast import literal_eval
import os

import requests


if os.environ.get("ENV", "dev") == "dev":
    try:
        from dotenv import find_dotenv, load_dotenv
    except ModuleNotFoundError:
        print("WARNING: python-dotenv not installed, not using .env file")
    else:
        ENV_FILE = find_dotenv(usecwd=True)
        print("ENV_FILE", ENV_FILE)
        if ENV_FILE:
            load_dotenv(ENV_FILE)


def _raw_get(key, default=None):
    return os.environ.get(key, default)


def get(key, default=None, **kwargs):
    value = _raw_get(key, default=default)
    if key == "PYCAFE_SERVER_CLIENT_KWARGS" and value is not None:
        value = literal_eval(value)
    return value


PYCAFE_COOKIE_MAX_AGE = get("PYCAFE_COOKIE_MAX_AGE", default="1209600")  # 14 days
PYCAFE_SESSION_SECRET_KEY = get("PYCAFE_SESSION_SECRET_KEY")
PYCAFE_SERVER_SIGN_PUBLIC_KEY = get("PYCAFE_SERVER_SIGN_PUBLIC_KEY")
PYCAFE_SERVER_SIGN_PRIVATE_KEY = get("PYCAFE_SERVER_SIGN_PRIVATE_KEY")
PYCAFE_SERVER_CLIENT_ID = get("PYCAFE_SERVER_CLIENT_ID")
PYCAFE_SERVER_SERVER_METADATA_URL = get("PYCAFE_SERVER_SERVER_METADATA_URL")
default_oauth_base_url = None
if (
    PYCAFE_SERVER_SERVER_METADATA_URL is not None
    and "/.well-known" in PYCAFE_SERVER_SERVER_METADATA_URL
):
    default_oauth_base_url = PYCAFE_SERVER_SERVER_METADATA_URL.split("/.well-known")[0]

PYCAFE_SERVER_OAUTH_BASE_URL = get(
    "PYCAFE_SERVER_OAUTH_BASE_URL", default_oauth_base_url
)
PYCAFE_SERVER_OAUTH_LOGOUT_PATH = get("PYCAFE_SERVER_OAUTH_LOGOUT_PATH", "/v2/logout")

PYCAFE_SERVER_JWKS_URL = get("PYCAFE_SERVER_JWKS_URL")
if PYCAFE_SERVER_JWKS_URL is None and PYCAFE_SERVER_SERVER_METADATA_URL:
    data = requests.get(PYCAFE_SERVER_SERVER_METADATA_URL).json()
    # using jwks_uri from server metadata
    PYCAFE_SERVER_JWKS_URL = data.get("jwks_uri")
    print(
        "Auto detecting JWKS URL from",
        PYCAFE_SERVER_SERVER_METADATA_URL,
        "to",
        PYCAFE_SERVER_JWKS_URL,
    )
if PYCAFE_SERVER_JWKS_URL is None and PYCAFE_SERVER_OAUTH_BASE_URL:
    PYCAFE_SERVER_JWKS_URL = PYCAFE_SERVER_OAUTH_BASE_URL + "/.well-known/jwks.json"
    print(
        "Auto detecting JWKS URL from",
        PYCAFE_SERVER_OAUTH_BASE_URL,
        "to",
        PYCAFE_SERVER_JWKS_URL,
    )
if PYCAFE_SERVER_JWKS_URL:
    jwks_client = requests.get(PYCAFE_SERVER_JWKS_URL).json()
else:
    jwks_client = None

PYCAFE_SERVER_AWS_REGION = get("PYCAFE_SERVER_AWS_REGION")


PYCAFE_SERVER_EDITORS = get("PYCAFE_SERVER_EDITORS", default="").split(",")
PYCAFE_SERVER_ADMINS = get("PYCAFE_SERVER_ADMINS", default="").split(",")
PYCAFE_SERVER_DATABASE_URL = os.environ.get(
    "PYCAFE_SERVER_DATABASE_URL", "sqlite:///./pycafe-server.db"
)
PYCAFE_SERVER_FRAMEWORKS = get(
    "PYCAFE_SERVER_FRAMEWORKS", default="streamlit,shiny,vizro,solara,dash,panel"
).split(",")
PYCAFE_SERVER_ENABLE_SNIPPETS = get(
    "PYCAFE_SERVER_ENABLE_SNIPPETS", default="true"
) in ["1", "True", "true", "yes"]
PYCAFE_SERVER_ENABLE_EXPORT = get("PYCAFE_SERVER_ENABLE_EXPORT", default="true") in [
    "1",
    "True",
    "true",
    "yes",
]
PYCAFE_SERVER_LICENSE_KEY = get("PYCAFE_SERVER_LICENSE_KEY")

PYCAFE_SERVER_INSECURE_MODE_DONT_USE_IN_PRODUCTION = get(
    "PYCAFE_SERVER_INSECURE_MODE_DONT_USE_IN_PRODUCTION", default="false"
) in ["1", "True", "true", "yes"]

PYCAFE_SERVER_PRE_AUTH = get("PYCAFE_SERVER_PRE_AUTH", default="false") in [
    "1",
    "True",
    "true",
    "yes",
]

# configure either these
PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY = get(
    "PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY"
)
PYCAFE_SERVER_PROXY_AUTH_HEADER_EMAIL = get(
    "PYCAFE_SERVER_PROXY_AUTH_HEADER_EMAIL", "x-forwarded-email"
)
# or this one
PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT = get(
    "PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT"
)

PYCAFE_SERVER_NO_ANON_BRANDING = get(
    "PYCAFE_SERVER_NO_ANON_BRANDING", default="false"
) in [
    "1",
    "True",
    "true",
    "yes",
]

PYCAFE_SERVER_GROUP_KEY = get("PYCAFE_SERVER_GROUP_KEY", default="groups")
PYCAFE_SERVER_GROUP_EDITOR_VALUE = get("PYCAFE_SERVER_GROUP_EDITOR_VALUE")
PYCAFE_SERVER_GROUP_ADMIN_VALUE = get("PYCAFE_SERVER_GROUP_ADMIN_VALUE")
PYCAFE_SERVER_BECOME_EDITOR_URL = get("PYCAFE_SERVER_BECOME_EDITOR_URL")


def auth_using_proxy():
    return bool(PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY) or bool(
        PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT
    )


def auth_is_configured():
    return bool(PYCAFE_SERVER_CLIENT_ID)


def signing_is_configured():
    return bool(PYCAFE_SERVER_SIGN_PUBLIC_KEY) and bool(PYCAFE_SERVER_SIGN_PRIVATE_KEY)


def get_settings():
    # should match src/data.ts
    return dict(
        insecureModeDontUseInProduction=PYCAFE_SERVER_INSECURE_MODE_DONT_USE_IN_PRODUCTION,
        requireAuth=auth_is_configured(),
        # we only document preAuth when using a proxy, but for testing it is convenient
        # not to have to run the proxy, so you can also force it by setting PYCAFE_SERVER_PRE_AUTH=1
        preAuth=PYCAFE_SERVER_PRE_AUTH or auth_using_proxy(),
        enableLogin=auth_is_configured(),
        enableLogout=False,
        enableProfile=False,
        enableProjects=False,
        enableSnippets=PYCAFE_SERVER_ENABLE_SNIPPETS,
        enableExport=PYCAFE_SERVER_ENABLE_EXPORT,
        isPublic=False,
        frameworks=PYCAFE_SERVER_FRAMEWORKS,
        instanceId=None,  # only filled in if not requires_auth() or when an admin
        trialmode=False,  # filled in in asgi.py
        signPublicKey=PYCAFE_SERVER_SIGN_PUBLIC_KEY
        if PYCAFE_SERVER_SIGN_PUBLIC_KEY
        else None,
        noAnonBranding=PYCAFE_SERVER_NO_ANON_BRANDING,
        becomeEditorUrl=PYCAFE_SERVER_BECOME_EDITOR_URL,
    )


print("PyCafe server configuration:")
print(
    "  Auth is configured:",
    auth_is_configured(),
    f"based on {PYCAFE_SERVER_CLIENT_ID=}",
)
print(
    "  Auth using proxy:",
    auth_using_proxy(),
    f"based on {PYCAFE_SERVER_PROXY_AUTH_HEADER_IDENTITY=} and {PYCAFE_SERVER_PROXY_AUTH_HEADER_USER_JWT=}",
)
print(
    "  Signing is configured:",
    signing_is_configured(),
    f"based on PYCAFE_SERVER_SIGN_PRIVATE_KEY={'***' if PYCAFE_SERVER_SIGN_PRIVATE_KEY else None} and PYCAFE_SERVER_SIGN_PUBLIC_KEY={PYCAFE_SERVER_SIGN_PUBLIC_KEY[:10] + '...' + PYCAFE_SERVER_SIGN_PUBLIC_KEY[-10:] if PYCAFE_SERVER_SIGN_PUBLIC_KEY else None}",
)
if PYCAFE_SERVER_EDITORS:
    print("  Editors:", PYCAFE_SERVER_EDITORS)
