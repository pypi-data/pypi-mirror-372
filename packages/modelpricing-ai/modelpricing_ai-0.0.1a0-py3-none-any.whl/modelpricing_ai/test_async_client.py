import asyncio
from typing import Any

import pytest

from .async_client import AsyncModelPricingClient
from .models import EstimateResponse
from .errors import Unauthorized, ValidationError


class DummyAiohttpResponse:
    def __init__(self, status: int, json_data: Any = None, text: str = "") -> None:
        self.status = status
        self._json_data = json_data
        self._text = text

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def json(self):
        if self._json_data is None:
            raise ValueError("No JSON")
        return self._json_data

    async def text(self):
        return self._text


class DummyAiohttpSession:
    def __init__(self, response: DummyAiohttpResponse) -> None:
        self._response = response
        self.closed = False
        self.last_request = None

    async def close(self):
        self.closed = True

    def post(self, url, json=None, headers=None):
        self.last_request = {"url": url, "json": json, "headers": headers}
        return self._response


@pytest.mark.asyncio
async def test_async_estimate_success():
    response = DummyAiohttpResponse(
        200,
        {
            "total": 0.001,
            "breakdown": {
                "input": {"unit": "per-1M-input", "branch": "gpt-4o-mini", "qty": 10, "rate": 1, "subtotal": 0.00001},
                "output": {"unit": "per-1M-output", "branch": "gpt-4o-mini", "qty": 20, "rate": 2, "subtotal": 0.00002},
            },
            "model": "gpt-4o-mini",
            "traceId": None,
        },
    )
    session = DummyAiohttpSession(response)
    client = AsyncModelPricingClient(api_key="test", session=session)
    result = await client.estimate(model="gpt-4o-mini", tokens_in=10, tokens_out=20)
    assert isinstance(result, EstimateResponse)
    assert result.total == 0.001
    assert session.last_request["url"].endswith("/v1/estimate")
    assert session.last_request["headers"]["Authorization"] == "Bearer test"


@pytest.mark.asyncio
async def test_async_estimate_unauthorized():
    session = DummyAiohttpSession(DummyAiohttpResponse(401, {"error": "Unauthorized"}))
    client = AsyncModelPricingClient(api_key="bad", session=session)
    with pytest.raises(Unauthorized):
        await client.estimate(model="m", tokens_in=1, tokens_out=1)


@pytest.mark.asyncio
async def test_async_estimate_validation_error():
    session = DummyAiohttpSession(DummyAiohttpResponse(422, {"error": "Invalid request", "details": "model not found"}))
    client = AsyncModelPricingClient(api_key="test", session=session)
    with pytest.raises(ValidationError) as exc:
        await client.estimate(model="bad-model", tokens_in=1, tokens_out=1)
    assert "model not found" in str(exc.value)


