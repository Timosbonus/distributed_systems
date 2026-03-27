from pydantic import BaseModel
from typing import Optional


class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    seller: Optional[str]
    timestamp: str

    class Config:
        from_attributes = True