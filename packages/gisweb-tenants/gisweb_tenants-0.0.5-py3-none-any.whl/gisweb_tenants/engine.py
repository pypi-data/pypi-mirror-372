# gisweb_tenants/engine.py
from __future__ import annotations
import hashlib
from contextlib import asynccontextmanager
from typing import Dict, Tuple, Optional

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import exc as sa_exc
from sqlalchemy.pool import NullPool
from sqlalchemy import AsyncAdaptedQueuePool

# Parametri runtime (saranno impostati da bootstrap)
class EngineSettings:
    def __init__(self, *, app_name_base: str = "app", pgbouncer_enabled: bool = True,
                 echo_sql: bool = False, pool_size: int = 10, statement_cache_size: int = 0):
        self.app_name_base = app_name_base
        self.pgbouncer_enabled = pgbouncer_enabled
        self.echo_sql = echo_sql
        self.pool_size = pool_size
        self.statement_cache_size = statement_cache_size

_engine_settings = EngineSettings()

def configure_engine(settings: EngineSettings):
    global _engine_settings
    _engine_settings = settings

_engine_registry: Dict[Tuple[str, str], AsyncEngine] = {}
_session_registry: Dict[Tuple[str, str], async_sessionmaker[AsyncSession]] = {}

def _dsn_hash(dsn: str) -> str:
    return hashlib.sha256(dsn.encode()).hexdigest()[:16]

def _connect_args_for_asyncpg(app_name: str) -> dict:
    return {
        "statement_cache_size": _engine_settings.statement_cache_size,
        "server_settings": {"application_name": app_name},
    }

def _engine_args(app_name: str, dsn: str) -> dict:
    use_nullpool = _engine_settings.pgbouncer_enabled
    poolclass = NullPool if use_nullpool else AsyncAdaptedQueuePool
    args = {
        "echo": _engine_settings.echo_sql,
        "poolclass": poolclass,
    }
    if poolclass is AsyncAdaptedQueuePool:
        args.update({
            "pool_pre_ping": True,
            "pool_size": _engine_settings.pool_size,
            "max_overflow": 64,
        })

    # Se usi asyncpg
    if dsn.startswith("postgresql+asyncpg://"):
        args["connect_args"] = _connect_args_for_asyncpg(app_name)

    return args

def _get_engine(tenant: str, dsn: str) -> AsyncEngine:
    key = (tenant, _dsn_hash(dsn))
    eng = _engine_registry.get(key)
    if eng is None:
        app_name = f"{_engine_settings.app_name_base}:{tenant}"
        args = _engine_args(app_name, dsn)
        eng = create_async_engine(dsn, **args)
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
async def session_for_tenant(tenant: str, dsn: str):
    SessionLocal = _get_sessionmaker(tenant, dsn)
    async with SessionLocal() as session:
        yield session

async def dispose_all_engines():
    for eng in list(_engine_registry.values()):
        try:
            await eng.dispose()
        except Exception:
            pass
    _engine_registry.clear()
    _session_registry.clear()
