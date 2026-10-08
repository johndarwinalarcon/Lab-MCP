from __future__ import annotations

from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from app.logging_config import logger


class CurrencyMCPClient:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root

    def _create_client(self) -> Client:
        server_script = str(self.project_root / "app" / "mcp_server" / "server.py")
        transport = StdioTransport(
            command="python",
            args=[server_script],
            cwd=str(self.project_root),
        )
        return Client(transport)

    async def login(self, username: str, password: str) -> str:
        async with self._create_client() as client:
            result = await client.call_tool("login", {"username": username, "password": password})
            return str(result.data["access_token"])

    async def get_exchange_rate(self, token: str, currency_from: str, currency_to: str) -> dict:
        async with self._create_client() as client:
            result = await client.call_tool(
                "get_exchange_rate",
                {
                    "token": token,
                    "currency_from": currency_from,
                    "currency_to": currency_to,
                },
            )
            return dict(result.data)


async def demonstrate_flow() -> None:
    client = CurrencyMCPClient(Path(__file__).resolve().parents[2])
    token = await client.login("admin", "Admin123*")
    logger.info("JWT obtained from MCP server")

    result = await client.get_exchange_rate(token, "USD", "CAD")#CAD EUR
    rate = next(iter(result["rates"].values()))
    print(f"\nTasa actual: 1 {result['base']} = {rate:.4f} {next(iter(result['rates']))}")
    print(f"Fecha: {result['date']}")


def main() -> None:
    import asyncio

    asyncio.run(demonstrate_flow())


if __name__ == "__main__":
    main()
