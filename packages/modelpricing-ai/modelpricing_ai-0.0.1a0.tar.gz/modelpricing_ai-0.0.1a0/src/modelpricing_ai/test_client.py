import json
from typing import Any

import pytest

from .client import ModelPricingClient
from .models import EstimateResponse
from .errors import Unauthorized, ValidationError


class DummyResponse:
    def __init__(self, status_code: int, json_data: Any = None, text: str = "") -> None:
        self.status_code = status_code
        self._json_data = json_data
        self.text = text

    def json(self) -> Any:
        if self._json_data is None:
            raise ValueError("No JSON")
        return self._json_data


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self._response = response
        self.last_request = None

    def post(self, url, json=None, headers=None, timeout=None):
        self.last_request = {"url": url, "json": json, "headers": headers, "timeout": timeout}
        return self._response


def test_estimate_success():
    response = DummyResponse(
        200,
        {
            "total": 0.01234,
            "breakdown": {
                "input": {"unit": "per-1M-input", "branch": "gpt-4o-mini", "qty": 10, "rate": 1, "subtotal": 0.00001},
                "output": {"unit": "per-1M-output", "branch": "gpt-4o-mini", "qty": 20, "rate": 2, "subtotal": 0.00002},
            },
            "model": "gpt-4o-mini",
            "traceId": None,
        },
    )
    session = DummySession(response)
    client = ModelPricingClient(api_key="test", base_url="https://api.modelpricing.ai", session=session)
    result = client.estimate(model="gpt-4o-mini", tokens_in=10, tokens_out=20)
    assert isinstance(result, EstimateResponse)
    assert result.total == 0.01234
    assert session.last_request["url"].endswith("/v1/estimate")
    assert session.last_request["headers"]["Authorization"] == "Bearer test"
    assert session.last_request["json"]["metrics"] == {"tokensIn": 10, "tokensOut": 20}


def test_estimate_unauthorized():
    session = DummySession(DummyResponse(401, {"error": "Unauthorized"}))
    client = ModelPricingClient(api_key="bad", session=session)
    with pytest.raises(Unauthorized):
        client.estimate(model="m", tokens_in=1, tokens_out=1)


def test_estimate_validation_error():
    session = DummySession(DummyResponse(422, {"error": "Invalid request", "details": "model not found"}))
    client = ModelPricingClient(api_key="test", session=session)
    with pytest.raises(ValidationError) as exc:
        client.estimate(model="bad-model", tokens_in=1, tokens_out=1)
    assert "model not found" in str(exc.value)


