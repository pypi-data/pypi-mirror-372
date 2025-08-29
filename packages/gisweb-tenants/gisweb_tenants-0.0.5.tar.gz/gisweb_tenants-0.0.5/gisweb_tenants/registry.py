# gisweb_tenants/registry.py
from __future__ import annotations
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any

@dataclass(frozen=True)
class TenantRecord:
    name: str
    config: Dict[str, Any]  # es: {"db_name": "...", "db_user": {...}, "db_password": {...}}

class TenantsRegistry:
    def __init__(self, tenants: Dict[str, TenantRecord]):
        self._tenants = tenants

    @classmethod
    def from_yaml(cls, path: Path) -> "TenantsRegistry":
        data = yaml.safe_load(Path(path).read_text()) or {}
        tenants: Dict[str, TenantRecord] = {}
        for name, cfg in (data.get("tenants") or {}).items():
            tenants[name.lower().strip()] = TenantRecord(name=name, config=cfg or {})
        return cls(tenants)

    def exists(self, name: str) -> bool:
        return name.lower().strip() in self._tenants

    def get(self, name: str) -> TenantRecord:
        key = name.lower().strip()
        rec = self._tenants.get(key)
        if not rec:
            raise KeyError(f"Tenant '{name}' non trovato")
        return rec

    @property
    def names(self) -> list[str]:
        return list(self._tenants.keys())
