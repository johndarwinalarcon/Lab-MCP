from __future__ import annotations

from typing import Any
from app.auth.exceptions import (
    FrankfurterApiError,
    InvalidCredentialsError,
    InvalidTokenError,
)
from fastmcp import FastMCP
from httpx import TimeoutException, HTTPStatusError, HTTPError

from app.auth.auth_controller import AuthenticationService, create_authentication_service
from app.auth.auth_models import LoginRequest
from app.auth.exceptions import InvalidCredentialsError, InvalidTokenError
from app.logging_config import logger
from app.services.frankfurter_service import FrankfurterService


mcp = FastMCP("CurrencyMCPServer")
auth_service: AuthenticationService = create_authentication_service()
frankfurter_service = FrankfurterService()


@mcp.tool()
def login(username: str, password: str) -> dict[str, str]:
    """Authenticate a user and return a JWT access token."""
    try:
        response = auth_service.login(LoginRequest(username=username, password=password))
        return {
            "access_token": response.access_token,
            "token_type": response.token_type,
        }
    except InvalidCredentialsError as exc:
        raise ValueError(str(exc)) from exc


@mcp.tool()
def get_exchange_rate(
    token: str,
    currency_from: str,
    currency_to: str,
) -> dict[str, Any]:
    """Return the exchange rate from the Frankfurter API after JWT validation."""
    try:
        auth_service.get_current_user(token)
    except InvalidTokenError as exc:
        logger.warning("Protected MCP tool rejected an invalid token")
        raise ValueError(str(exc)) from exc

    try:
        result = frankfurter_service.get_exchange_rate(currency_from, currency_to)
    except TimeoutException as exc:
        raise FrankfurterApiError(f"Timeout al consultar Frankfurter: {exc}") from exc
    except HTTPStatusError as exc:
        raise FrankfurterApiError(
            f"Frankfurter respondió con HTTP {exc.response.status_code}: "
            f"{exc.response.text}"
        ) from exc
    except HTTPError as exc:
        raise FrankfurterApiError(f"Error HTTP de Frankfurter: {type(exc).__name__}: {exc}") from exc

    return {
        "amount": result["amount"],
        "base": result["base"],
        "date": result["date"],
        "rates": result["rates"],
    }
