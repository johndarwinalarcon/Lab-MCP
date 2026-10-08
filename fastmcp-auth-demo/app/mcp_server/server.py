from __future__ import annotations

from app.config.settings import get_settings
from app.logging_config import logger
from app.mcp_server.tools import mcp


def main() -> None:
    settings = get_settings()
    logger.info("Starting MCP server", extra={"app_name": settings.app_name})
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
