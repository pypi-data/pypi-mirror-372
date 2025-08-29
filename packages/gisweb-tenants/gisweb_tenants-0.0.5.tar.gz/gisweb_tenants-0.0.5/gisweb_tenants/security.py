# gisweb_tenants/security.py
from __future__ import annotations
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from uuid import uuid4
from typing import Optional, Set

import jwt
from fastapi import HTTPException
from redis.asyncio import Redis
from redis.exceptions import RedisError
from .config import AuthConfig

class TokenType:
    ACCESS = "access"
    REFRESH = "refresh"

def _utcnow() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp())

class SessionStoreUnavailable(HTTPException):
    def __init__(self):
        super().__init__(status_code=503, detail="Session store (Redis) non disponibile")
        
        
def _resolve_secret_value(val: str) -> str:
    """
    Se `val` è il contenuto, lo restituisce.
    Se `val` è un path a un file esistente, legge e restituisce il contenuto strip-pato.
    """
    try:
        p = Path(val)
        if p.exists() and p.is_file():
            return p.read_text().strip()
    except Exception:
        pass
    return val

class TenantSecurity:
    def __init__(self, *, redis: Redis, tenant: str, cfg: AuthConfig):
        self.redis = redis
        self.tenant = tenant.strip().lower() or "default"
        self.cfg = cfg
        
        # # 👇 risolvi subito i segreti (contenuto, non path)
        # self._access_secret = _resolve_secret_value(cfg.access_secret)
        # self._refresh_secret = _resolve_secret_value(cfg.refresh_secret)
        # if not self._access_secret or not self._refresh_secret:
        #     raise RuntimeError("ACCESS/REFRESH token secret non configurati")

    def _k_userinfo(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:userinfo"
    def _k_access_set(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:access_jti"
    def _k_refresh_cur(self, userid: str) -> str:
        return f"tenant:{self.tenant}:user:{userid}:refresh_jti"
    def _k_refresh_revoked(self) -> str:
        return f"tenant:{self.tenant}:revoked_refresh_jti"

    # 👇 alias richiesto
    def userinfo_key(self, userid: str) -> str:
        return self._k_userinfo(userid)

    def _base_payload(self, sub: str, token_type: str, exp_min: int, extra: Optional[dict]) -> dict:
        now = _utcnow()
        exp_ts = now + int(timedelta(minutes=exp_min).total_seconds())
        payload = {
            "sub": sub, "type": token_type, "iat": now, "exp": exp_ts,
            "iss": self.cfg.issuer, "jti": str(uuid4()), "tenant": self.tenant,
        }
        if extra:
            payload.update(extra)
        return payload

    def _secret_for(self, token_type: str) -> str:
        # 👇 ora restituisce la CHIAVE, non il path
        return self.cfg.access_secret if token_type == TokenType.ACCESS else self.cfg.refresh_secret

    def create_access_token(self, subject: str, data: Optional[dict] = None) -> str:
        payload = self._base_payload(subject, TokenType.ACCESS, self.cfg.access_exp_minutes, data or {})
        return jwt.encode(payload, self.cfg.access_secret, algorithm=self.cfg.algorithm)

    def create_refresh_token(self, subject: str, data: Optional[dict] = None) -> str:
        payload = self._base_payload(subject, TokenType.REFRESH, self.cfg.refresh_exp_minutes, data or {})
        return jwt.encode(payload, self.cfg.refresh_secret, algorithm=self.cfg.algorithm)

    def decode_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        try:
            if expected_type:
                secret = self._secret_for(expected_type)
                payload = jwt.decode(
                    token, secret, algorithms=[self.cfg.algorithm],
                    issuer=self.cfg.issuer, leeway=self.cfg.leeway_seconds,
                    options={"require": ["exp", "iat", "iss", "sub", "type"]},
                )
            else:
                payload = None
                for t in (TokenType.ACCESS, TokenType.REFRESH):
                    try:
                        secret = self._secret_for(t)
                        payload = jwt.decode(
                            token, secret, algorithms=[self.cfg.algorithm],
                            issuer=self.cfg.issuer, leeway=self.cfg.leeway_seconds,
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

        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(status_code=403, detail=f"Token non valido per tipo {expected_type}")

        if self.cfg.require_tenant_claim:
            claim_tenant = payload.get("tenant")
            if not claim_tenant or claim_tenant != self.tenant:
                raise HTTPException(status_code=401, detail="Tenant mismatch")
        return payload

    async def verify_token(self, token: str, token_type: str, *, enforce_membership: bool = False) -> dict:
        try:
            p = self.decode_token(token, expected_type=token_type)
            sub = p.get("sub"); jti = p.get("jti")
            if not sub or not jti:
                raise HTTPException(status_code=401, detail="Token incompleto")

            if token_type == TokenType.REFRESH:
                cur = await self.redis.get(self._k_refresh_cur(sub))
                if cur is None or cur != jti:
                    raise HTTPException(status_code=401, detail="Refresh token non riconosciuto o ruotato")
                if await self.redis.sismember(self._k_refresh_revoked(), jti):
                    raise HTTPException(status_code=401, detail="Refresh token revocato")
                return p

            if token_type == TokenType.ACCESS and enforce_membership:
                if not await self.redis.sismember(self._k_access_set(sub), jti):
                    raise HTTPException(status_code=401, detail="Access token non riconosciuto o revocato")

            return p
        except RedisError:
            raise SessionStoreUnavailable()

    async def store_session(self, user_dict: dict, access_token: str, refresh_token: str):
        try:
            a = self.decode_token(access_token, expected_type=TokenType.ACCESS)
            r = self.decode_token(refresh_token, expected_type=TokenType.REFRESH)

            userid = user_dict.get("userid")
            if not userid:
                raise HTTPException(status_code=400, detail="Userid mancante")

            access_ttl = timedelta(minutes=self.cfg.access_exp_minutes)
            refresh_ttl = timedelta(minutes=self.cfg.refresh_exp_minutes)

            await self.redis.set(self._k_userinfo(userid), json.dumps(user_dict), ex=int(refresh_ttl.total_seconds()))
            await self.redis.sadd(self._k_access_set(userid), a["jti"])
            await self.redis.expire(self._k_access_set(userid), int(access_ttl.total_seconds()))

            old = await self.redis.getset(self._k_refresh_cur(userid), r["jti"])
            await self.redis.expire(self._k_refresh_cur(userid), int(refresh_ttl.total_seconds()))
            if old and old != r["jti"]:
                await self.redis.sadd(self._k_refresh_revoked(), old)
                await self.redis.expire(self._k_refresh_revoked(), int(refresh_ttl.total_seconds()))
        except RedisError:
            raise SessionStoreUnavailable()

    async def revoke_refresh(self, payload: dict):
        try:
            if (jti := payload.get("jti")):
                await self.redis.sadd(self._k_refresh_revoked(), jti)
            if (sub := payload.get("sub")):
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
