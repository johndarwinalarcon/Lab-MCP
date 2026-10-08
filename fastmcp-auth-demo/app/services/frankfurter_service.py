from __future__ import annotations

from typing import Any, TypedDict

import httpx
import truststore

from app.auth.exceptions import FrankfurterApiError
from app.config.settings import get_settings
from app.logging_config import logger


class ExchangeRateResponse(TypedDict):
    amount: float
    base: str
    date: str
    rates: dict[str, float]


class FrankfurterService:
    def __init__(self, client: httpx.Client | None = None) -> None:
        settings = get_settings()
        self.base_url = settings.frankfurter_base_url.rstrip("/")
        self.timeout = settings.frankfurter_timeout_seconds
        self.client = client or httpx.Client(
            timeout=self.timeout,
            verify=truststore.SSLContext(),
        )

    def get_exchange_rate(self, currency_from: str, currency_to: str) -> ExchangeRateResponse:
        normalized_from = currency_from.upper()
        normalized_to = currency_to.upper()

        url = f"{self.base_url}/latest"
        params = {"from": normalized_from, "to": normalized_to}

        logger.info(
            "Calling Frankfurter API",
            extra={
                "currency_from": normalized_from,
                "currency_to": normalized_to,
            },
        )

        try:
            response = self.client.get(url, params=params)
            response.raise_for_status()
            payload = response.json()
        except httpx.TimeoutException as exc:
            raise FrankfurterApiError(
                "The Frankfurter API request timed out after 10 seconds"
            ) from exc
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text or "Frankfurter API returned an error"
            raise FrankfurterApiError(f"Frankfurter API error: {detail}") from exc
        except (ValueError, TypeError) as exc:
            raise FrankfurterApiError("Frankfurter API returned an invalid JSON response") from exc
        except httpx.HTTPError as exc:
            raise FrankfurterApiError("Unable to access the Frankfurter API") from exc

        required_fields = {"amount", "base", "date", "rates"}
        if not isinstance(payload, dict) or not required_fields.issubset(payload):
            raise FrankfurterApiError("Frankfurter API response is incomplete")

        rates = payload["rates"]
        if not isinstance(rates, dict) or normalized_to not in rates:
            raise FrankfurterApiError(f"No exchange rate found for {normalized_from} to {normalized_to}")

        result = {
            "amount": float(payload["amount"]),
            "base": str(payload["base"]),
            "date": str(payload["date"]),
            "rates": {str(code): float(value) for code, value in rates.items()},
        }
        logger.info("Frankfurter response received", extra={"result": result})
        return result
