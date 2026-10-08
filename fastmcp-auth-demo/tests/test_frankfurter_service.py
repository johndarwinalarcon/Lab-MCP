from unittest.mock import Mock

import httpx

from app.services.frankfurter_service import FrankfurterService


def test_get_exchange_rate_returns_typed_response():
    response = Mock(spec=httpx.Response)
    response.json.return_value = {
        "amount": 1.0,
        "base": "USD",
        "date": "2025-01-01",
        "rates": {"EUR": 0.92},
    }
    response.raise_for_status.return_value = None

    client = Mock(spec=httpx.Client)
    client.get.return_value = response
    service = FrankfurterService(client=client)

    result = service.get_exchange_rate("USD", "EUR")

    assert result["amount"] == 1.0
    assert result["base"] == "USD"
    assert result["rates"]["EUR"] == 0.92
    client.get.assert_called_once_with(
        "https://api.frankfurter.dev/v1/latest",
        params={"from": "USD", "to": "EUR"},
    )


def test_get_exchange_rate_raises_for_missing_target_rate():
    response = Mock(spec=httpx.Response)
    response.json.return_value = {
        "amount": 1.0,
        "base": "USD",
        "date": "2025-01-01",
        "rates": {"CHF": 0.89},
    }
    response.raise_for_status.return_value = None

    client = Mock(spec=httpx.Client)
    client.get.return_value = response
    service = FrankfurterService(client=client)

    try:
        service.get_exchange_rate("USD", "EUR")
        assert False, "FrankfurterApiError was not raised"
    except Exception as exc:  # pytest will report the precise exception type
        assert "No exchange rate found" in str(exc)
