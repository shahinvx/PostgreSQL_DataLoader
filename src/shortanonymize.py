# pip install pycryptodome
import base64, hashlib, os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def _kdf_16(secret: str | bytes) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    # 16-byte AES key derived from secret
    return hashlib.sha256(b"shortanon-kdf::" + secret).digest()[:16]

def b64u(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode("utf-8").rstrip("=")

def b64u_dec(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))

class ShortCBCAnonymizer:
    def __init__(self, secret: str | bytes):
        self.key = _kdf_16(secret)
        self.block = AES.block_size  # 16

    def encode(self, plaintext: str) -> str:
        cipher = AES.new(self.key, AES.MODE_CBC)  # random IV
        ct = cipher.encrypt(pad(plaintext.encode("utf-8"), self.block))
        # iv + ct, Base64URL (no truncation!)
        return b64u(cipher.iv + ct)

    def decode(self, token: str) -> str:
        raw = b64u_dec(token)
        iv, ct = raw[:16], raw[16:]
        cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
        return unpad(cipher.decrypt(ct), self.block).decode("utf-8")

# Usage:
# secret = os.environ.get("ANON_SECRET") or "dev-only-change-me"
# anon = ShortCBCAnonymizer(secret)
# t = anon.encode("12436")
# print(anon.decode(t))
