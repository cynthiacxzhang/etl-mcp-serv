"""Core application glue for the ETL MCP server.

This module exposes a minimal `run(config)` function used by the main
entrypoint. It will attempt to start a FastMCP server when `mcp` is available,
otherwise it logs and returns — useful for local development.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def run(config: Any) -> None:
	"""Start the core application.

	If an MCP server implementation is available we delegate to it. For now
	this function acts as a safe stub that logs the received config.
	"""
	logger.info("Core.run invoked")
	try:
		# Try to import and start a FastMCP server if available
		from mcp.server.fastmcp import FastMCP  # type: ignore

		logger.info("FastMCP available — creating server (development stub)")
		# Create a minimal server instance (not fully wired)
		server = FastMCP()
		logger.info("FastMCP instance created: %s", server)
		# In a real app we'd register tools and start serving here.
	except Exception:
		logger.info("mcp.FastMCP not available or failed to import — running stub loop")
		# For a stubbed run we just log the config and return
		logger.info("Config: %s", getattr(config, "_data", "<no-config>"))
