"""Main entry point for JJ Multi-Database MCP server."""

import asyncio
import sys
import logging
from .server import main as async_main


def main():
    """Synchronous entry point for console scripts."""
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
