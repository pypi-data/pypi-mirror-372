from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict
import os
import yaml

# ENV: TENANT_REGISTRY_PATH -> path del file YAML
def _registry_path() -> Path:
    return Path(os.getenv("TENANT_REGISTRY_PATH", "/run/secrets/tenants.yml"))

def _load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Registry tenant YAML non trovato: {path}")
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    data.setdefault("tenants", {})
    data.setdefault("defaults", {})
    return data

@lru_cache(maxsize=1)
def _load_registry_cached(mtime: float) -> Dict[str, Any]:
    return _load_yaml(_registry_path())

def get_registry() -> Dict[str, Any]:
    p = _registry_path()
    return _load_registry_cached(p.stat().st_mtime)
