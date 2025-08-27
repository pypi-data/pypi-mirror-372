from __future__ import annotations
import os
from typing import Any, Dict, Tuple
from pydantic.networks import PostgresDsn
from .crypto import decrypt_secret, is_encrypted
from .registry import get_registry
import logging
logger = logging.getLogger('uvicorn.error')


# Helpers
def _parse_query(val: Any) -> Dict[str, Any]:
    # Mantenuto per eventuali estensioni future; oggi non usiamo query nel DSN asyncpg
    if not val or not isinstance(val, dict):
        return {}
    return {k: v for k, v in val.items() if v is not None}

def resolve_db_triplet(tenant: str) -> Tuple[str, str, str]:
    reg = get_registry()
    t = reg["tenants"].get(tenant, {})
    d = reg["defaults"] or {}

    db_name = t.get("db_name", tenant)

    db_user = t.get("db_user", d.get("db_user"))
    if is_encrypted(db_user):
        db_user = decrypt_secret(db_user, f"{tenant}|db|user")

    db_password = t.get("db_password", d.get("db_password"))
    if is_encrypted(db_password):
        db_password = decrypt_secret(db_password, f"{tenant}|db|password")

    if not db_user or not db_password:
        raise RuntimeError(f"Credenziali DB mancanti per tenant '{tenant}'")
    return db_name, db_user, db_password

def build_dsn(tenant: str) -> str:
    """
    Costruisce DSN Postgres per asyncpg via SQLAlchemy.
    Priorità: ENV -> defaults YAML -> override per-tenant.
    Nessuna query string: asyncpg usa connect_args.
    """
    reg = get_registry()
    t = reg["tenants"].get(tenant, {})
    d = reg.get("defaults", {}) or {}

    scheme = os.getenv("DATABASE_SCHEME", d.get("scheme", "postgresql+asyncpg"))
    host   = os.getenv("DATABASE_HOST",   d.get("host", "postgres"))
    port   = int(os.getenv("DATABASE_PORT", d.get("port", 5432)))

    # override specifici del tenant
    host   = t.get("host", host)
    port   = int(t.get("port", port))
    scheme = t.get("scheme", scheme)
    
    # triplet (db, user, pass)
    db_name, db_user, db_password = resolve_db_triplet(tenant)
    dsn = PostgresDsn.build(
        scheme=scheme,
        username=db_user,
        password=db_password,
        host=host,
        port=port,
        path=db_name,
    )
    logger.info(dsn)
    return str(dsn)
