from __future__ import annotations
import json
import os
from typing import Any, Mapping, Optional
import bcrypt
from fastapi import HTTPException, Request, status
from redis import Redis
from .engine import session_for_tenant, dispose_all_engines
from .exceptions import TenantForbidden, TenantNotFound
from .registry import get_registry
from .security import TenantSecurity, TokenType

TENANT_HEADER = os.getenv("TENANT_HEADER", "X-Tenant")
DEFAULT_TENANT = os.getenv("DEFAULT_TENANT", "istanze")
ALLOWED_TENANTS = {x.strip().lower() for x in (os.getenv("ALLOWED_TENANTS", "") or "").split(",") if x.strip()}
STRICT_TENANT_WHITELIST = os.getenv("STRICT_TENANT_WHITELIST", "false").lower() in ("1", "true", "yes", "on")

def get_tenant_from_request(request: Request) -> str:
    t = (request.headers.get(TENANT_HEADER)
         or request.query_params.get("tenant")
         or DEFAULT_TENANT)
    t = (t or "").strip().lower() or DEFAULT_TENANT

    if ALLOWED_TENANTS and t not in ALLOWED_TENANTS:
        if STRICT_TENANT_WHITELIST:
            raise TenantForbidden()
        # fallback soft al default
        t = DEFAULT_TENANT

    # opzionale: verifica che esista nel registry
    reg = get_registry()
    if t not in reg.get("tenants", {}):
        raise TenantNotFound(t)
    return t

# ---- Dipendenze FastAPI ----
async def get_session(request: Request):
    tenant = get_tenant_from_request(request)
    async with session_for_tenant(tenant) as session:
        yield session

def get_security(redis, request: Request, *, secret: str,
                            issuer: str = "istanzeonline",
                            access_exp_min: int = 60,
                            refresh_exp_min: int = 60 * 24 * 30,
                            require_tenant_claim: bool = True):
    tenant = get_tenant_from_request(request)
    return TenantSecurity(
        redis=redis,
        tenant=tenant,
        secret=secret,
        issuer=issuer,
        access_expires_minutes=access_exp_min,
        refresh_expires_minutes=refresh_exp_min,
        require_tenant_claim=require_tenant_claim,
    )

def verify_password(plain: str | bytes, hashed: str | bytes) -> bool:
    return bcrypt.checkpw(
        plain.encode() if isinstance(plain, str) else plain,
        hashed.encode() if isinstance(hashed, str) else hashed
    )

def get_password_hash(plain: str | bytes) -> str:
    pw = plain.encode() if isinstance(plain, str) else plain
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode()


async def resolve_current_user(*, request:Request, token: str, redis: Redis, secret: str, required_roles: Optional[list[str]] = None):
    """
    Factory per dipendenza FastAPI: ritorna un callable da usare con Depends.
    - `secret`: chiave JWT
    - `get_redis_client`: dipendenza per ottenere Redis
    - `required_roles`: lista di ruoli minimi richiesti
    Ritorna un dict con i dati utente.
    """
    tenant = get_tenant_from_request(request)
    security = TenantSecurity(redis=redis, tenant=tenant, secret=secret, require_tenant_claim=True)
        
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = await security.verify_token(token, TokenType.ACCESS, enforce_membership=False)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail, headers={"WWW-Authenticate": "Bearer"})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token non valido o scaduto",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user id", headers={"WWW-Authenticate": "Bearer"})

    raw = await redis.get(security.userinfo_key(user_id))
    if not raw:
        raise HTTPException(status_code=401, detail="Sessione scaduta", headers={"WWW-Authenticate": "Bearer"})
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")

    user_data = json.loads(raw)

    # check flag attivo
    if not user_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="Utente non attivo")

    # check ruoli (solo se richiesti)
    if required_roles and not user_data.get("is_superuser", False):
        roles = set(user_data.get("roles") or [])
        if not roles.intersection(required_roles):
            raise HTTPException(status_code=403, detail=f"Richiesto uno dei ruoli: {required_roles}")

    return user_data



# re-export utility
dispose_all_engines = dispose_all_engines
