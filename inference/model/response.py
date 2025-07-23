from pydantic import BaseModel, Field


class ResponseBody(BaseModel):
    rent_price: int = Field(..., ge=6000, le=100000)
    predicted_rent_price: int = Field(..., ge=6000, le=100000)
    pct_diff: float
