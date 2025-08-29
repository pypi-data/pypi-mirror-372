# gisweb_tenants/crypto.py
from __future__ import annotations
import base64, secrets
from typing import Any, Dict
from dataclasses import dataclass
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from .config import CryptoConfig

def _is_b64url(s: str) -> bool:
    return all(c.isalnum() or c in "-_" for c in s)

def coerce_key_to_bytes(key: str | bytes) -> bytes:
    if isinstance(key, bytes):
        raw = key
    else:
        k = key.strip()
        try:
            # prova base64url con padding
            raw = base64.urlsafe_b64decode(k + "===")
        except Exception:
            # fallback hex
            raw = bytes.fromhex(k)
    if len(raw) != 32:
        raise RuntimeError("ENCRYPT_KEY deve essere 32 bytes (base64url o hex).")
    return raw

def encrypt_secret(plain: str, aad: str, cfg: CryptoConfig, v: int = 1) -> Dict[str, Any]:
    _aes = AESGCM(cfg.encrypt_key)
    nonce = secrets.token_bytes(12)
    ct = _aes.encrypt(nonce, plain.encode(), aad.encode())
    return {
        "$enc": "aesgcm",
        "v": v,
        "n": base64.urlsafe_b64encode(nonce).decode().rstrip("="),
        "ct": base64.urlsafe_b64encode(ct).decode().rstrip("="),
    }

def is_encrypted(x: Any) -> bool:
    return isinstance(x, dict) and x.get("$enc") == "aesgcm" and "n" in x and "ct" in x

def decrypt_secret(enc: Dict[str, Any], aad: str, cfg: CryptoConfig) -> str:
    nonce = base64.urlsafe_b64decode(enc["n"] + "===")
    ct = base64.urlsafe_b64decode(enc["ct"] + "===")
    _aes = AESGCM(cfg.encrypt_key)
    pt = _aes.decrypt(nonce, ct, aad.encode())
    return pt.decode()
