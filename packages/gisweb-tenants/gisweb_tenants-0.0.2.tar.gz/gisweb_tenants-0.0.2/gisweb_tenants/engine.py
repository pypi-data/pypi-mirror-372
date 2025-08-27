from __future__ import annotations
import hashlib
import os
from contextlib import asynccontextmanager
from typing import Dict, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import AsyncAdaptedQueuePool
from sqlalchemy.pool import NullPool
from .dsn import build_dsn

# ENV opzionali (fall-back se l’app non passa config):
def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")

PGBOUNCER_ENABLED = _bool_env("PGBOUNCER_ENABLED", True)
ECHO_SQL = _bool_env("ECHO_SQL", False)
POOL_SIZE = int(os.getenv("POOL_SIZE", "10"))
APP_NAME_BASE = os.getenv("DB_APP_NAME", "app")
STATEMENT_CACHE_SIZE = int(os.getenv("PGBOUNCER_STATEMENT_CACHE_SIZE", "0"))

# Cache { (tenant, dsn_hash): engine }
_engine_registry: Dict[Tuple[str, str], AsyncEngine] = {}
_session_registry: Dict[Tuple[str, str], async_sessionmaker[AsyncSession]] = {}

def _dsn_hash(dsn: str) -> str:
    return hashlib.sha256(dsn.encode()).hexdigest()[:16]

def _engine_args(app_name: str) -> dict:
    use_nullpool = PGBOUNCER_ENABLED
    poolclass = NullPool if use_nullpool else AsyncAdaptedQueuePool
    return {
        "echo": ECHO_SQL,
        "poolclass": poolclass,
        "pool_pre_ping": False if poolclass is NullPool else True,
        "pool_size": None if poolclass is NullPool else POOL_SIZE,
        "max_overflow": None if poolclass is NullPool else 64,
        "connect_args": {
            "statement_cache_size": STATEMENT_CACHE_SIZE,
            "server_settings": {"application_name": app_name},
        },
    }

def _get_engine(tenant: str, dsn: str) -> AsyncEngine:
    key = (tenant, _dsn_hash(dsn))
    eng = _engine_registry.get(key)
    if eng is None:
        app_name = f"{APP_NAME_BASE}:{tenant}"
        args = _engine_args(app_name)
        eng = create_async_engine(dsn, **{k: v for k, v in args.items() if v is not None})
        _engine_registry[key] = eng
    return eng

def _get_sessionmaker(tenant: str, dsn: str) -> async_sessionmaker[AsyncSession]:
    key = (tenant, _dsn_hash(dsn))
    sm = _session_registry.get(key)
    if sm is None:
        eng = _get_engine(tenant, dsn)
        sm = async_sessionmaker(bind=eng, expire_on_commit=False, autoflush=False)
        _session_registry[key] = sm
    return sm

@asynccontextmanager
async def session_for_tenant(tenant: str):
    dsn = build_dsn(tenant)
    SessionLocal = _get_sessionmaker(tenant, dsn)
    async with SessionLocal() as session:
        yield session

async def dispose_all_engines():
    for eng in list(_engine_registry.values()):
        try:
            eng.dispose()
        except Exception:
            pass
    _engine_registry.clear()
    _session_registry.clear()
