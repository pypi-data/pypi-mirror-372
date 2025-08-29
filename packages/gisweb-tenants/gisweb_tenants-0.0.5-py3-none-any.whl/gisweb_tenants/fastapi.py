# gisweb_tenants/fastapi.py
from __future__ import annotations
from typing import Optional
import bcrypt, json
from fastapi import Request, HTTPException, status
from redis.asyncio import Redis

from .config import TenantsConfig, AuthConfig, CryptoConfig, DbDefaults
from .registry import TenantsRegistry
from .dsn import DsnBuilder
from .engine import session_for_tenant, configure_engine, EngineSettings
from .security import TenantSecurity, TokenType

_registry: TenantsRegistry | None = None
_cfg: TenantsConfig | None = None
_auth: AuthConfig | None = None
_crypto: CryptoConfig | None = None
_dbdef: DbDefaults | None = None
_dsn_builder: DsnBuilder | None = None
_redis: Redis | None = None

def bootstrap_fastapi_integration(
    *,
    registry: TenantsRegistry,
    tenants_cfg: TenantsConfig,
    auth_cfg: AuthConfig,
    redis_client: Optional[Redis],
    crypto_cfg: Optional[CryptoConfig],
    db_defaults: DbDefaults,                     # 👈 nuovo arg obbligatorio
    engine_settings: Optional[EngineSettings] = None,
):
    global _registry, _cfg, _auth, _redis, _crypto, _dbdef, _dsn_builder
    _registry = registry
    _cfg = tenants_cfg
    _auth = auth_cfg
    _redis = redis_client
    _crypto = crypto_cfg
    _dbdef = db_defaults
    _dsn_builder = DsnBuilder(registry, db_defaults, crypto_cfg)
    if engine_settings:
        configure_engine(engine_settings)

def _ensure_ready():
    if not all([_registry, _cfg, _auth, _dsn_builder, _dbdef]):
        raise RuntimeError("gisweb_tenants non inizializzato (bootstrap_fastapi_integration)")

def get_tenant_name(request: Request) -> str:
    _ensure_ready()
    t = (request.headers.get(_cfg.tenant_header)  # type: ignore
         or request.query_params.get("tenant")
         or _cfg.default_tenant)                  # type: ignore
    t = (t or "").strip().lower() or _cfg.default_tenant  # type: ignore

    if _cfg.allowed_tenants_csv:  # type: ignore
        allowed = {x.strip().lower() for x in _cfg.allowed_tenants_csv.split(",") if x.strip()}  # type: ignore
        if allowed and t not in allowed:
            if _cfg.strict_whitelist:  # type: ignore
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Tenant non autorizzato")
            t = _cfg.default_tenant  # type: ignore

    if not _registry.exists(t):  # type: ignore
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tenant '{t}' non trovato")
    return t

async def get_session(request: Request):
    _ensure_ready()
    tenant = get_tenant_name(request)
    dsn = _dsn_builder.build(tenant)  # type: ignore
    async with session_for_tenant(tenant, dsn) as session:
        yield session

def get_security(request: Request) -> TenantSecurity:
    _ensure_ready()
    if not _redis:
        raise RuntimeError("Redis non configurato")
    tenant = get_tenant_name(request)
    return TenantSecurity(redis=_redis, tenant=tenant, cfg=_auth)  # type: ignore


async def resolve_current_user(request: Request, token: str, required_roles: Optional[list[str]] = None):
    sec = get_security(request)
    if not token:
        raise HTTPException(status_code=401, detail="Missing Bearer token", headers={"WWW-Authenticate": "Bearer"})
    p = await sec.verify_token(token, TokenType.ACCESS, enforce_membership=False)
    user_id = p.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user id", headers={"WWW-Authenticate": "Bearer"})
    raw = await sec.redis.get(f"tenant:{sec.tenant}:user:{user_id}:userinfo")
    if not raw:
        raise HTTPException(status_code=401, detail="Sessione scaduta", headers={"WWW-Authenticate": "Bearer"})
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    user_data = json.loads(raw)
    if not user_data.get("is_active", True):
        raise HTTPException(status_code=403, detail="Utente non attivo")
    if required_roles and not user_data.get("is_superuser", False):
        roles = set(user_data.get("roles") or [])
        if not roles.intersection(required_roles):
            raise HTTPException(status_code=403, detail=f"Richiesto uno dei ruoli: {required_roles}")
    return user_data



def verify_password(plain: str | bytes, hashed: str | bytes) -> bool:
    return bcrypt.checkpw(
        plain.encode() if isinstance(plain, str) else plain,
        hashed.encode() if isinstance(hashed, str) else hashed
    )

def get_password_hash(plain: str | bytes) -> str:
    pw = plain.encode() if isinstance(plain, str) else plain
    return bcrypt.hashpw(pw, bcrypt.gensalt()).decode()