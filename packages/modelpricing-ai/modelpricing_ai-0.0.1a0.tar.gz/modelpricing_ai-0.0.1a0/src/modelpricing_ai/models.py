from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class EstimateBreakdown(BaseModel):
    unit: str
    branch: str
    qty: int
    rate: float
    subtotal: float


class EstimateBreakdownGroup(BaseModel):
    input: EstimateBreakdown
    output: EstimateBreakdown


class EstimateResponse(BaseModel):
    total: float
    breakdown: EstimateBreakdownGroup
    model: str
    traceId: Optional[Dict[str, Any]] = Field(default=None)


