# gisweb_tenants/dsn.py
from __future__ import annotations
from typing import Tuple
from urllib.parse import quote

from .crypto import is_encrypted, decrypt_secret
from .config import CryptoConfig, DbDefaults
from .registry import TenantsRegistry

class DsnBuilder:
    def __init__(self, registry: TenantsRegistry, db_defaults: DbDefaults, crypto: CryptoConfig | None = None):
        self._reg = registry
        self._def = db_defaults
        self._crypto = crypto

    def _resolve_triplet(self, tenant: str) -> Tuple[str, str, str]:
        """
        db_name, db_user, db_password per il tenant.
        user/pass possono essere cifrati nel YAML.
        """
        cfg = self._reg.get(tenant).config
        db_name = cfg.get("db_name", tenant)

        db_user = cfg.get("db_user")
        db_password = cfg.get("db_password")

        # Decrypt se necessario
        if is_encrypted(db_user):
            if not self._crypto:
                raise RuntimeError("Credenziali cifrate ma manca CryptoConfig")
            db_user = decrypt_secret(db_user, f"{tenant}|db|user", self._crypto)

        if is_encrypted(db_password):
            if not self._crypto:
                raise RuntimeError("Credenziali cifrate ma manca CryptoConfig")
            db_password = decrypt_secret(db_password, f"{tenant}|db|password", self._crypto)

        if not db_user or not db_password:
            raise RuntimeError(f"Credenziali DB mancanti per tenant '{tenant}'")
        return db_name, db_user, db_password

    def build(self, tenant: str) -> str:
        db_name, db_user, db_password = self._resolve_triplet(tenant)
        u = quote(str(db_user), safe="")
        p = quote(str(db_password), safe="")
        print (f"{self._def.scheme}://{u}:{p}@{self._def.host}:{self._def.port}/{db_name}")
        return f"{self._def.scheme}://{u}:{p}@{self._def.host}:{self._def.port}/{db_name}"







    # def build_dsn(tenant: str) -> str:
    #     """
    #     Costruisce DSN Postgres per asyncpg via SQLAlchemy.
    #     Priorità: ENV -> defaults YAML -> override per-tenant.
    #     Nessuna query string: asyncpg usa connect_args.
    #     """
    #     reg = get_registry()
    #     t = reg["tenants"].get(tenant, {})
    #     d = reg.get("defaults", {}) or {}

    #     scheme = os.getenv("DATABASE_SCHEME", d.get("scheme", "postgresql+asyncpg"))
    #     host   = os.getenv("DATABASE_HOST",   d.get("host", "postgres"))
    #     port   = int(os.getenv("DATABASE_PORT", d.get("port", 5432)))

    #     # override specifici del tenant
    #     host   = t.get("host", host)
    #     port   = int(t.get("port", port))
    #     scheme = t.get("scheme", scheme)
        
    #     # triplet (db, user, pass)
    #     db_name, db_user, db_password = resolve_db_triplet(tenant)
    #     dsn = PostgresDsn.build(
    #         scheme=scheme,
    #         username=db_user,
    #         password=db_password,
    #         host=host,
    #         port=port,
    #         path=db_name,
    #     )
    #     logger.info(dsn)
    #     return str(dsn)
