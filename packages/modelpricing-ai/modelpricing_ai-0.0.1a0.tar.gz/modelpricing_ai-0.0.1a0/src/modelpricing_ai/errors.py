from typing import Optional


class ModelPricingError(Exception):
    """Base exception for ModelPricing client."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


class Unauthorized(ModelPricingError):
    """401 Unauthorized"""


class ValidationError(ModelPricingError):
    """422 Unprocessable Entity"""


class NotFound(ModelPricingError):
    """404 Not Found"""


class ServerError(ModelPricingError):
    """5xx Server error"""


