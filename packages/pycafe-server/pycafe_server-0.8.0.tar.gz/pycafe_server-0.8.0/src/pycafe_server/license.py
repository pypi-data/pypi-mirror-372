import sys
import jwt
from datetime import datetime, timedelta
import dataclasses
from . import config

PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA7rYmFUesizrMe9f0UOlV
arzt0CLW3Hlx/1z7sNAf6MET5ZV/1T5EbW87/537wrE+VQ7VfigVTvr60otIenbW
u1HAWRZMU95EL/cyxZFkjZ9lmbvTbJyn88h9b41tOCDFB3rD9HIUXIz7inphMgU4
d8Z0anmPJL02p8InIQGfzonenJPswj2sgYgkzXOJdGziYqs27bdZbz9VrVF8fdBJ
5W0m2csHXERwf4Rs75s+y65+npOA3oDIXMPXn89u82wk5HXOU7QB/Y8Y9Fm8ezmw
S96z6hqG4UUEECn5pn8iA2fMV7+SFFOU2uDjhxHiN14mDIw9xf+g1Y+aLIRCu1BO
/QIDAQAB
-----END PUBLIC KEY-----
"""


@dataclasses.dataclass
class License:
    sub: str
    max_editors: int
    customer_info: str
    exp: datetime

    @classmethod
    def from_jwt(cls, license_key):
        data = cls.verify_license_key(license_key)
        if data:
            return cls(**data)
        return None

    @classmethod
    # Verify JWT with public key
    def verify_license_key(cls, license_key):
        try:
            data = jwt.decode(license_key, PUBLIC_KEY, algorithms=["RS256"])
            # case exp to datetime
            data["exp"] = datetime.utcfromtimestamp(data["exp"])
            print("License information:", data)
            return data
        except jwt.ExpiredSignatureError:
            print("ERROR: License has expired.", file=sys.stderr)
            return False
        except jwt.InvalidTokenError:
            print("ERROR: Invalid license key.", file=sys.stderr)
            return False


license = License.from_jwt(config.PYCAFE_SERVER_LICENSE_KEY)
if license:
    print("License information:", license)
    days_to_expire = (license.exp - datetime.utcnow()).days
    print("Days to expire:", days_to_expire)
    print("Maximal number of editors:", license.max_editors)
    print("Customer information:", license.customer_info)


if __name__ == "__main__":
    import sys

    # Load the private key
    with open("pycafe_server_private_key.pem", "rb") as f:
        private_key = f.read()

    sub = sys.argv[1]
    max_editors = int(sys.argv[2])
    customer_info = sys.argv[3]
    # parse date if given, otherwise 1 year
    exp = (
        datetime.utcnow() + timedelta(days=365)
        if len(sys.argv) < 5
        else datetime.strptime(sys.argv[4], "%Y-%m-%d")
    )
    # Define payload
    license = License(
        sub=sub, max_editors=max_editors, customer_info=customer_info, exp=exp
    )

    # Generate JWT with private key
    license_key = jwt.encode(
        dataclasses.asdict(license), private_key, algorithm="RS256"
    )
    print("License Key:", license_key)
    # copy to clipboard
    try:
        import pyperclip

        pyperclip.copy(license_key)
        print("License copied to clipboard.")
    except ImportError:
        print("pyperclip not installed, not copying to clipboard")

    license_key_check = License.from_jwt(license_key)
    if license_key_check:
        print("License key is valid.")
    else:
        print("License key is invalid.")
