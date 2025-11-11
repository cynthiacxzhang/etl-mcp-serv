"""Compatibility shim: re-export the real core.app implementation located under `src/core`.

This avoids duplicating logic while making the package importable as
`etl_mcp_serv.core.app`.
"""

from __future__ import annotations

from src.core.app import run  # re-export existing implementation

__all__ = ["run"]
