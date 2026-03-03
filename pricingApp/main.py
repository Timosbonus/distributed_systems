from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

from pricingApp.adapters.database import Database
from pricingApp.adapters.scraper import Scraper
from pricingApp.domain.services import PricingService
from pricingApp.domain.entities import Product

app = FastAPI(title="Pricing App")

db = Database()
scraper = Scraper()
pricing_service = PricingService(database=db, scraper=scraper)


class ProductCreate(BaseModel):
    name: str
    idealo_link: str


class ProductResponse(BaseModel):
    id: int
    name: str
    idealo_link: str
    lowest_price: Optional[float] = None


@app.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate):
    new_product = pricing_service.add_product(
        name=product.name,
        idealo_link=product.idealo_link
    )
    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price
    )


@app.get("/products", response_model=list[ProductResponse])
def get_products():
    products = pricing_service.get_all_products()
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            idealo_link=p.idealo_link,
            lowest_price=p.lowest_price
        )
        for p in products
    ]


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = pricing_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price
    )
