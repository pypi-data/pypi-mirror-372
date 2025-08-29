import os
from typing import Any, Dict, Optional, Union

import requests

from .errors import ModelPricingError, NotFound, ServerError, Unauthorized, ValidationError
from .models import EstimateResponse


class ModelPricingClient:
    """Synchronous client for the ModelPricing.ai API."""

    def __init__(
        self,
        api_key: str,
        *,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not api_key or not isinstance(api_key, str):
            raise ValueError("api_key is required")
        self.api_key = api_key
        configured_base = base_url or os.environ.get(
            "MODELPRICING_BASE_URL", "https://api.modelpricing.ai"
        )
        # Normalize base URL (no trailing slash)
        self.base_url = configured_base.rstrip("/")
        self.timeout = timeout
        self._session = session or requests.Session()

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def estimate(
        self,
        *,
        model: str,
        tokens_in: int,
        tokens_out: int,
        trace_id: Optional[Dict[str, Any]] = None,
    ) -> Union[Dict[str, Any], EstimateResponse]:
        """
        Call POST /v1/estimate and return the response JSON.

        Returns dict with keys: total, breakdown, model, traceId.
        """
        if not model:
            raise ValueError("model is required")
        if tokens_in is None or tokens_out is None:
            raise ValueError("tokens_in and tokens_out are required")

        url = f"{self.base_url}/v1/estimate"
        payload: Dict[str, Any] = {
            "model": model,
            "metrics": {"tokensIn": int(tokens_in), "tokensOut": int(tokens_out)},
        }
        if trace_id is not None:
            payload["traceId"] = trace_id

        response = self._session.post(
            url, json=payload, headers=self._headers(), timeout=self.timeout
        )

        if response.status_code == 200:
            data = response.json()
            try:
                return EstimateResponse.model_validate(data)
            except Exception:
                return data
        if response.status_code == 401:
            raise Unauthorized("Unauthorized", status_code=401)
        if response.status_code == 404:
            raise NotFound("Not found", status_code=404)
        if response.status_code == 422:
            try:
                data = response.json()
                message = data.get("error") or "Unprocessable Entity"
                details = data.get("details")
                if details:
                    message = f"{message}: {details}"
            except Exception:
                message = "Unprocessable Entity"
            raise ValidationError(message, status_code=422)

        # Other 4xx/5xx
        try:
            data = response.json()
            message = data.get("error") or response.text or "HTTP error"
        except Exception:
            message = response.text or "HTTP error"

        if 500 <= response.status_code <= 599:
            raise ServerError(message, status_code=response.status_code)
        raise ModelPricingError(message, status_code=response.status_code)


