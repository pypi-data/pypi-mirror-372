# app/crypto.py
import os, base64, secrets
from typing import Any, Dict
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def _load_key() -> bytes:
    k = os.getenv("ENCRYPT_KEY") or ""
    try: raw = base64.urlsafe_b64decode(k + "===")
    except Exception: raw = bytes.fromhex(k) if k else b""
    if len(raw) != 32:
        raise RuntimeError("ENCRYPT_KEY deve essere 32 bytes (base64url o hex).")
    return raw

_AES = AESGCM(_load_key())

def encrypt_secret(plain: str, aad: str, v: int = 1) -> Dict[str, Any]:
    nonce = secrets.token_bytes(12)
    ct = _AES.encrypt(nonce, plain.encode(), aad.encode())
    enc = {"$enc":"aesgcm","v":v,
           "n": base64.urlsafe_b64encode(nonce).decode().rstrip("="),
           "ct": base64.urlsafe_b64encode(ct).decode().rstrip("=")}
    return enc

def is_encrypted(x: Any) -> bool:
    return isinstance(x, dict) and x.get("$enc")=="aesgcm" and "n" in x and "ct" in x

def decrypt_secret(enc: Dict[str, Any], aad: str) -> str:
    n = base64.urlsafe_b64decode(enc["n"] + "===")
    ct= base64.urlsafe_b64decode(enc["ct"] + "===")
    pt= _AES.decrypt(n, ct, aad.encode())
    return pt.decode()
