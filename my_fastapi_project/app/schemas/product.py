from pydantic import BaseModel
from typing import Optional, List


class ProductBase(BaseModel):
    name: str
    idealo_link: str
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    image_data: Optional[List[str]] = None
    description: Optional[str] = None
    update_interval_hours: Optional[int] = 24
    minimum_margin: Optional[float] = None
    manual_sell_price: Optional[float] = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    lowest_price: Optional[float] = None
    lowest_seller: Optional[str] = None
    sell_price: Optional[float] = None
    last_price_update: Optional[str] = None

    class Config:
        from_attributes = True