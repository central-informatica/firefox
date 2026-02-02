import os, base64, json
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def encrypt_pfx(pfx_data: bytes, master_key: bytes):
    aesgcm = AESGCM(master_key)
    nonce = os.urandom(12)
    encrypted = aesgcm.encrypt(nonce, pfx_data, None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(encrypted).decode()
    }

def decrypt_pfx(data: dict, master_key: bytes):
    aesgcm = AESGCM(master_key)
    nonce = base64.b64decode(data["nonce"])
    ciphertext = base64.b64decode(data["ciphertext"])
    return aesgcm.decrypt(nonce, ciphertext, None)
