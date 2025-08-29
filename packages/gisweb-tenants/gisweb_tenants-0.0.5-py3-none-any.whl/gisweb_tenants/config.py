# gisweb_tenants/config.py
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass(frozen=True, slots=True)
class AuthConfig:
    access_secret: str
    refresh_secret: str
    issuer: str = "istanzeonline"
    algorithm: str = "HS256"
    access_exp_minutes: int = 60
    refresh_exp_minutes: int = 60 * 24 * 30
    leeway_seconds: int = 10
    require_tenant_claim: bool = True

@dataclass(frozen=True, slots=True)
class TenantsConfig:
    tenants_file: Path                 # path a tenants.yml
    tenant_header: str = "X-Tenant"
    default_tenant: str = "istanze"
    allowed_tenants_csv: str = ""      # "a,b,c"
    strict_whitelist: bool = False     # se True -> 403 se non in allowed

@dataclass(frozen=True, slots=True)
class CryptoConfig:
    encrypt_key: bytes  # 32 bytes
    
@dataclass(frozen=True, slots=True)
class DbDefaults:
    scheme: str = "postgresql+asyncpg"
    host: str = "localhost"
    port: int = 6432