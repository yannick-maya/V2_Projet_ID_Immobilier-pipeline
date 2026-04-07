import base64
import hashlib
import hmac
import os


def _hash_pbkdf2(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return "pbkdf2$" + base64.b64encode(salt + digest).decode("utf-8")


def _verify_pbkdf2(plain: str, hashed: str) -> bool:
    if not hashed.startswith("pbkdf2$"):
        return False
    raw = base64.b64decode(hashed.split("$", 1)[1].encode("utf-8"))
    salt, digest = raw[:16], raw[16:]
    test = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, 200_000)
    return hmac.compare_digest(digest, test)


def hash_password(password: str) -> str:
    return _hash_pbkdf2(password)


def verify_password(plain: str, hashed: str) -> bool:
    return _verify_pbkdf2(plain, hashed)
