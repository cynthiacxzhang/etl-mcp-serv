"""Entrypoint module that mirrors the original `src/main.py` but lives under
the `etl_mcp_serv` package so the Dockerfile command `python -m etl_mcp_serv.core.main`
works when `/app/src` is on PYTHONPATH.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys

from etl_mcp_serv.configs import Config
from etl_mcp_serv.core import app


# ---------- Logging Configuration ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Parse args, load config, and start the ETL MCP Server.

    This mirrors the original project's behavior but uses the internal
    `etl_mcp_serv.configs.Config` class.
    """
    parser = argparse.ArgumentParser(description="ETL MCP Server")
    parser.add_argument(
        "--config",
        "-c",
        default=os.getenv("ETL_MCP_CONFIG", "config.yaml"),
        help="Path to config file (default: config.yaml, env: ETL_MCP_CONFIG)",
    )
    args = parser.parse_args()

    try:
        logger.info("Starting ETL MCP Server...")
        logger.info(f"Using config file: {args.config}")

        # Load configuration
        config = Config.from_file(args.config)

        # Adjust log level if debug is set in config
        if getattr(config.mcp, "debug", False):
            logger.setLevel(logging.DEBUG)

        # Pretty-print config for debugging
        try:
            logger.debug(json.dumps(json.loads(config.model_dump_json()), indent=4))
        except Exception:
            logger.debug("Config loaded (unable to pretty-print)")

        # Start the core application
        app.run(config)

    except Exception as e:
        logger.error(f"Failed to start MCP server: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
