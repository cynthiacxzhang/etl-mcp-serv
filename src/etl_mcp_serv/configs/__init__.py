"""Configuration utilities for etl_mcp_serv.

Provides a minimal `Config` class with `from_file` and `model_dump_json()` so the
project can start without depending on Pydantic during initial development.
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from typing import Any


class _MCPSettings(SimpleNamespace):
    def __init__(self, debug: bool = False):
        super().__init__(debug=debug)


class Config:
    """Lightweight config object used by the main entrypoint.

    - from_file(path): attempts to load YAML (if PyYAML installed) or JSON.
    - model_dump_json(): returns a JSON string representation for debugging.
    """

    def __init__(self, data: dict[str, Any] | None = None):
        data = data or {}
        # expected top-level 'mcp' key with optional 'debug'
        mcp = data.get("mcp") or {}
        self.mcp = _MCPSettings(debug=bool(mcp.get("debug", False)))
        # preserve raw data for diagnostics
        self._data = data

    @classmethod
    def from_file(cls, path: str) -> "Config":
        try:
            import yaml

            with open(path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            return cls(data)
        except Exception:
            # fallback to JSON if YAML not available
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                return cls(data)
            except Exception:
                # return empty config if file missing or unparseable
                return cls()

    def model_dump_json(self) -> str:
        return json.dumps(self._data or {})


__all__ = ["Config"]
