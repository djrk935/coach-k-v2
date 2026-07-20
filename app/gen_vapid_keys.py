"""Generate a VAPID keypair for web push. Run once, paste into .env.

    python -m app.gen_vapid_keys
"""

import base64

from py_vapid import Vapid


def main() -> None:
    v = Vapid()
    v.generate_keys()

    pub = v.public_key.public_numbers()
    pub_raw = b"\x04" + pub.x.to_bytes(32, "big") + pub.y.to_bytes(32, "big")
    pub_b64 = base64.urlsafe_b64encode(pub_raw).rstrip(b"=").decode()

    priv_raw = v.private_key.private_numbers().private_value.to_bytes(32, "big")
    priv_b64 = base64.urlsafe_b64encode(priv_raw).rstrip(b"=").decode()

    print(f"VAPID_PUBLIC_KEY={pub_b64}")
    print(f"VAPID_PRIVATE_KEY={priv_b64}")


if __name__ == "__main__":
    main()
