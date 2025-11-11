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

		# Attempt to discover and register tools from the project's tools package.
		tools_module = None
		for module_name in ("etl_mcp_serv.tools", "src.tools", "tools"):
			try:
				tools_module = __import__(module_name, fromlist=["*"])
				break
			except Exception:
				tools_module = None

		registered = 0
		if tools_module is not None and hasattr(tools_module, "list_tools"):
			try:
				names = tools_module.list_tools()
			except Exception:
				names = []

			for name in names:
				try:
					func = tools_module.get_tool(name)
				except Exception:
					func = None
				if not func:
					continue

				# Try multiple possible registration method names on the FastMCP
				reg_methods = [
					"register_tool",
					"register",
					"add_tool",
					"add_tools",
					"register_tools",
					"register_function",
				]
				was_registered = False
				for reg in reg_methods:
					if hasattr(server, reg):
						try:
							getattr(server, reg)(func)
							was_registered = True
							break
						except TypeError:
							try:
								getattr(server, reg)(name, func)
								was_registered = True
								break
							except Exception:
								# ignore and try next
								pass
						except Exception:
							pass

				if not was_registered:
					# best-effort fallback: attach on the server object for discovery
					try:
						setattr(server, name, func)
						was_registered = True
					except Exception:
						was_registered = False

				if was_registered:
					registered += 1

		logger.info("Registered %d tools on FastMCP (attempted)", registered)

		# Optionally start the server if config requests it (default: do not auto-start)
		auto_start = False
		try:
			auto_start = bool(getattr(config, "mcp", None) and getattr(config.mcp, "auto_start", False))
		except Exception:
			auto_start = False

		if auto_start:
			start_methods = ["serve", "run", "start", "start_server", "serve_forever"]
			for sm in start_methods:
				if hasattr(server, sm):
					logger.info("Starting FastMCP server via %s()", sm)
					getattr(server, sm)()
					return

		logger.info("FastMCP configured but not started (set mcp.auto_start=true to start automatically)")

	except Exception:
		logger.info("mcp.FastMCP not available or failed to import — running stub loop")
		# For a stubbed run we just log the config and return
		logger.info("Config: %s", getattr(config, "_data", "<no-config>"))
