# app/security/tenant_security.py
from __future__ import annotations

import json
import os
from datetime import timedelta, timezone, datetime
from pathlib import Path
from typing import Optional, Set
from uuid import uuid4

import jwt
from redis.asyncio import Redis
from redis.exceptions import RedisError
from fastapi import HTTPException

# ------------------------------------------------------------
# utility
# ------------------------------------------------------------
class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"

def _utcnow() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp())

def _as_minutes(v: int | float) -> int:
    return int(v)

def _read_secret_env(var: str, *, default_secret_path: Optional[str] = None) -> Optional[str]:
    """
    Priorità:
      1) VAR (stringa diretta)
      2) VAR_FILE (percorso file)
      3) default_secret_path (es. /run/secrets/<nome>)
    """
    val = os.getenv(var)
    if val:
        return val.strip()

    file_path = os.getenv(f"{var}_FILE")
    if file_path and Path(file_path).is_file():
        return Path(file_path).read_text().strip()

    if default_secret_path and Path(default_secret_path).is_file():
        return Path(default_secret_path).read_text().strip()

    return None

# carica una volta a import-time, così non leggi file ad ogni request
ACCESS_TOKEN_SECRET = _read_secret_env("ACCESS_TOKEN_SECRET", default_secret_path="/run/secrets/access_token")
REFRESH_TOKEN_SECRET = _read_secret_env("REFRESH_TOKEN_SECRET", default_secret_path="/run/secrets/refresh_token")

if not ACCESS_TOKEN_SECRET or not REFRESH_TOKEN_SECRET:
    # In produzione vuoi fallire duro. In dev… fai come credi, ma non piangere poi.
    raise RuntimeError("Mancano ACCESS_TOKEN_SECRET e/o REFRESH_TOKEN_SECRET")

# ------------------------------------------------------------
# eccezioni di comodo
# ------------------------------------------------------------
class SessionStoreUnavailable(HTTPException):
    def __init__(self):
        super().__init__(status_code=503, detail="Session store (Redis) non disponibile")

# ------------------------------------------------------------
# implementazione
# ------------------------------------------------------------
class TenantSecurity:
    """
    Gestione JWT + sessione Redis per tenant specifico.
    Firma i token con segreti distinti:
      - ACCESS_TOKEN_SECRET per 'access'
      - REFRESH_TOKEN_SECRET per 'refresh'
    """

    def __init__(
        self,
        *,
        redis: Redis,
        tenant: str,
        issuer: str = "istanzeonline",
        algorithm: str = "HS256",
        access_expires_minutes: int = 60,
        refresh_expires_minutes: int = 60 * 24 * 30,
        require_tenant_claim: bool = True,
        leeway_seconds: int = 10,
    ):
        self.redis = redis
        self.tenant = (tenant or "default").strip().lower()
        self.issuer = issuer
        self.algorithm = algorithm
        self.access_exp = access_expires_minutes
        self.refresh_exp = refresh_expires_minutes
        self.require_tenant_claim = require_tenant_claim
        self.leeway = leeway_seconds

        # segreti già risolti a import-time
        self.access_secret = ACCESS_TOKEN_SECRET
        self.refresh_secret = REFRESH_TOKEN_SECRET

    # ---- keys (namespaced) ----
    def _k_userinfo(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:userinfo"

    def _k_access_set(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:access_jti"

    def _k_refresh_cur(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:refresh_jti"

    def _k_refresh_revoked(self) -> str:
        return f"tenant:{self.tenant}:revoked_refresh_jti"

    def userinfo_key(self, userid: str) -> str:
        return self._k_userinfo(userid=userid)

    # ---- jwt helpers ----
    def _base_payload(self, sub: str, token_type: str, exp_min: int, extra: Optional[dict] = None) -> dict:
        now = _utcnow()
        exp_ts = now + int(timedelta(minutes=exp_min).total_seconds())
        payload = {
            "sub": sub,
            "type": token_type,
            "iat": now,
            "exp": exp_ts,
            "iss": self.issuer,
            "jti": str(uuid4()),
            "tenant": self.tenant,
        }
        if extra:
            payload.update(extra)
        return payload

    def _secret_for(self, token_type: str) -> str:
        if token_type == TokenType.ACCESS:
            return self.access_secret
        if token_type == TokenType.REFRESH:
            return self.refresh_secret
        raise ValueError("token_type sconosciuto")

    def create_access_token(self, subject: str, data: Optional[dict] = None) -> str:
        payload = self._base_payload(subject, TokenType.ACCESS, self.access_exp, data or {})
        return jwt.encode(payload, self._secret_for(TokenType.ACCESS), algorithm=self.algorithm)

    def create_refresh_token(self, subject: str, data: Optional[dict] = None) -> str:
        payload = self._base_payload(subject, TokenType.REFRESH, self.refresh_exp, data or {})
        return jwt.encode(payload, self._secret_for(TokenType.REFRESH), algorithm=self.algorithm)

    def decode_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        try:
            if expected_type:
                # via rapida: decodifica con il segreto del tipo atteso
                secret = self._secret_for(expected_type)
                payload = jwt.decode(
                    token,
                    secret,
                    algorithms=[self.algorithm],
                    issuer=self.issuer,
                    leeway=self.leeway,
                    options={"require": ["exp", "iat", "iss", "sub", "type"]},
                )
            else:
                # expected_type ignoto: prova entrambi, poi valida 'type'
                for t in (TokenType.ACCESS, TokenType.REFRESH):
                    try:
                        secret = self._secret_for(t)
                        payload = jwt.decode(
                            token,
                            secret,
                            algorithms=[self.algorithm],
                            issuer=self.issuer,
                            leeway=self.leeway,
                            options={"require": ["exp", "iat", "iss", "sub", "type"]},
                        )
                        break
                    except jwt.PyJWTError:
                        payload = None
                if not payload:
                    raise jwt.InvalidTokenError("Impossibile verificare il token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token scaduto")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token non valido")

        # controllo tipo
        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(status_code=403, detail=f"Token non valido per tipo {expected_type}")

        # controllo tenant
        if self.require_tenant_claim:
            claim_tenant = payload.get("tenant")
            if not claim_tenant:
                raise HTTPException(status_code=401, detail="Token senza tenant")
            if claim_tenant != self.tenant:
                raise HTTPException(status_code=401, detail="Tenant mismatch")

        return payload

    async def verify_token(self, token: str, token_type: str, *, enforce_membership: bool = False) -> dict:
        try:
            payload = self.decode_token(token, expected_type=token_type)
            sub = payload.get("sub")
            jti = payload.get("jti")
            if not sub or not jti:
                raise HTTPException(status_code=401, detail="Token incompleto")

            # refresh checks
            if token_type == TokenType.REFRESH:
                cur = await self.redis.get(self._k_refresh_cur(sub))
                if cur is None or cur != jti:
                    raise HTTPException(status_code=401, detail="Refresh token non riconosciuto o ruotato")
                if await self.redis.sismember(self._k_refresh_revoked(), jti):
                    raise HTTPException(status_code=401, detail="Refresh token revocato")
                return payload

            # access checks (opzionali)
            if token_type == TokenType.ACCESS and enforce_membership:
                if not await self.redis.sismember(self._k_access_set(sub), jti):
                    raise HTTPException(status_code=401, detail="Access token non riconosciuto o revocato")

            return payload
        except RedisError:
            raise SessionStoreUnavailable()

    async def store_session(self, user_dict: dict, access_token: str, refresh_token: str):
        try:
            a_payload = self.decode_token(access_token, expected_type=TokenType.ACCESS)
            r_payload = self.decode_token(refresh_token, expected_type=TokenType.REFRESH)

            userid = user_dict.get("userid")
            if not userid:
                raise HTTPException(status_code=400, detail="Userid mancante")

            user_key = self._k_userinfo(userid)
            access_set = self._k_access_set(userid)
            refresh_cur = self._k_refresh_cur(userid)
            refresh_revoked = self._k_refresh_revoked()

            access_ttl_min = _as_minutes(self.access_exp)
            refresh_ttl_min = _as_minutes(self.refresh_exp)

            await self.redis.set(user_key, json.dumps(user_dict), ex=refresh_ttl_min * 60)

            await self.redis.sadd(access_set, a_payload["jti"])
            await self.redis.expire(access_set, timedelta(minutes=access_ttl_min))

            old_jti = await self.redis.getset(refresh_cur, r_payload["jti"])
            await self.redis.expire(refresh_cur, timedelta(minutes=refresh_ttl_min))
            if old_jti and old_jti != r_payload["jti"]:
                await self.redis.sadd(refresh_revoked, old_jti)
                await self.redis.expire(refresh_revoked, timedelta(minutes=refresh_ttl_min))

        except RedisError:
            raise SessionStoreUnavailable()

    async def revoke_refresh(self, payload: dict):
        try:
            jti = payload.get("jti")
            sub = payload.get("sub")
            if jti:
                await self.redis.sadd(self._k_refresh_revoked(), jti)
            if sub:
                await self.redis.delete(self._k_refresh_cur(sub))
        except RedisError:
            raise SessionStoreUnavailable()

    async def delete_tokens(self, userid: str, token_type: str):
        try:
            if token_type == TokenType.ACCESS:
                await self.redis.delete(self._k_access_set(userid))
            elif token_type == TokenType.REFRESH:
                await self.redis.delete(self._k_refresh_cur(userid))
        except RedisError:
            raise SessionStoreUnavailable()

    async def get_valid_tokens(self, userid: str, token_type: str) -> Set[str]:
        try:
            if token_type == TokenType.ACCESS:
                return set(await self.redis.smembers(self._k_access_set(userid)))
            elif token_type == TokenType.REFRESH:
                cur = await self.redis.get(self._k_refresh_cur(userid))
                return {cur} if cur else set()
            return set()
        except RedisError:
            raise SessionStoreUnavailable()
