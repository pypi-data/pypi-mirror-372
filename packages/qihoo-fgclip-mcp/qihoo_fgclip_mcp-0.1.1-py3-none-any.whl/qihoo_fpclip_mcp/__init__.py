"""MCP Server for 360 Research embedding services."""


import logging
import sys
import asyncio

from .server import run_stdio_server

logger = logging.getLogger(__name__)


def main():
    # Set log level
    logging.getLogger().setLevel("INFO")
    
    try:
        logger.info("Starting stdio server")
        asyncio.run(run_stdio_server())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
