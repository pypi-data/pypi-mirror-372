import base64
import hashlib
try:
    from Crypto import Random
    from Crypto.Cipher import AES
except ImportError:
    raise Exception("need to install pycryptodome")

class AESCipherManager:
    def __init__(self, key: str):
        self.bs = AES.block_size
        self.mode = AES.MODE_OFB
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw: str) -> str:
        raw = self._pad(raw)
        iv = Random.new().read(self.bs)
        cipher = AES.new(self.key, self.mode, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode())).decode()

    def decrypt(self, enc: str) -> str:
        enc = base64.b64decode(enc)
        iv = enc[:self.bs]
        cipher = AES.new(self.key, self.mode, iv)
        return AESCipherManager._unpad(cipher.decrypt(enc[self.bs:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]
