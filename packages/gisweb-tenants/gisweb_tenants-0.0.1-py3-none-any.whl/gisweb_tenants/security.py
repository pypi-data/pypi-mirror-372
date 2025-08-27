from __future__ import annotations
import json
from uuid import uuid4
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Set
import jwt
from redis.asyncio import Redis
from redis.exceptions import RedisError
from .exceptions import SessionStoreUnavailable
from fastapi import HTTPException

def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)

def _as_minutes(td_or_int) -> int:
    if isinstance(td_or_int, timedelta):
        return int(td_or_int.total_seconds() // 60)
    return int(td_or_int)

class TokenType:
    ACCESS = "ACCESS"
    REFRESH = "REFRESH"

class TenantSecurity:
    """
    Gestione JWT + sessione Redis per tenant specifico.
    """
    def __init__(
        self,
        *,
        redis: Redis,
        tenant: str,
        secret: str,
        issuer: str = "istanzeonline",
        algorithm: str = "HS256",
        access_expires_minutes: int = 60,
        refresh_expires_minutes: int = 60 * 24 * 30,
        require_tenant_claim: bool = True,
        leeway_seconds: int = 10,
    ):
        self.redis = redis
        self.tenant = (tenant or "default").strip().lower()
        self.secret = secret
        self.issuer = issuer
        self.algorithm = algorithm
        self.access_exp = access_expires_minutes
        self.refresh_exp = refresh_expires_minutes
        self.require_tenant_claim = require_tenant_claim
        self.leeway = leeway_seconds

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
        payload = {
            "sub": sub,
            "type": token_type,
            "iat": now,
            "exp": now + timedelta(minutes=exp_min),
            "iss": self.issuer,
            "jti": str(uuid4()),
            "tenant": self.tenant,
        }
        if extra:
            payload.update(extra)
        return payload

    def create_access_token(self, subject: str, data: Optional[dict] = None) -> str:
        return jwt.encode(self._base_payload(subject, TokenType.ACCESS, self.access_exp, data or {}),
                          self.secret, algorithm=self.algorithm)

    def create_refresh_token(self, subject: str, data: Optional[dict] = None) -> str:
        return jwt.encode(self._base_payload(subject, TokenType.REFRESH, self.refresh_exp, data or {}),
                          self.secret, algorithm=self.algorithm)

    def decode_token(self, token: str, expected_type: Optional[str] = None) -> dict:
        try:
            payload = jwt.decode(
                token, self.secret, algorithms=[self.algorithm],
                issuer=self.issuer, leeway=self.leeway,
                options={"require": ["exp", "iat", "iss", "sub", "type"]},
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token scaduto")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Token non valido")

        if expected_type and payload.get("type") != expected_type:
            raise HTTPException(status_code=403, detail=f"Token non valido per tipo {expected_type}")

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
