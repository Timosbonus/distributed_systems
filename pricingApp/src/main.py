from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json

from src.adapters.database import Database
from src.adapters.scraper import Scraper
from src.domain.services import PricingService, AuthService


db = Database()
scraper = Scraper()
pricing_service = PricingService(database=db, scraper=scraper)
auth_service = AuthService(database=db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    
    scheduler = AsyncIOScheduler()
    scheduler.add_job(pricing_service.run_scheduled_updates, "interval", minutes=1)
    scheduler.start()
    
    yield
    
    scheduler.shutdown()
    await scraper.close()


app = FastAPI(title="Pricing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductCreate(BaseModel):
    name: str
    idealo_link: str
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    image_data: Optional[List[str]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    idealo_link: str
    lowest_price: Optional[float] = None
    lowest_seller: Optional[str] = None
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    sell_price: Optional[float] = None
    last_price_update: Optional[str] = None
    image_data: Optional[List[str]] = None


class PriceHistoryResponse(BaseModel):
    price: float
    seller: Optional[str]
    timestamp: str


class UserCreate(BaseModel):
    username: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


@app.post("/products", response_model=ProductResponse)
def add_product(product: ProductCreate):

    new_product = pricing_service.add_product(
        name=product.name,
        idealo_link=product.idealo_link,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        image_data=product.image_data
    )

    image_data_list = []
    if new_product.image_data:
        try:
            image_data_list = json.loads(new_product.image_data)
        except:
            image_data_list = []

    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        lowest_seller=new_product.lowest_seller,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        sell_price=new_product.sell_price,
        last_price_update=new_product.last_price_update.isoformat() if new_product.last_price_update else None,
        image_data=image_data_list
    )


@app.get("/products", response_model=List[ProductResponse])
def get_products():

    products = pricing_service.get_all_products()

    result = []
    for p in products:
        image_data_list = []
        if p.image_data:
            try:
                image_data_list = json.loads(p.image_data)
            except:
                pass
        
        result.append(ProductResponse(
            id=p.id,
            name=p.name,
            idealo_link=p.idealo_link,
            lowest_price=p.lowest_price,
            lowest_seller=p.lowest_seller,
            quantity=p.quantity,
            cost_per_unit=p.cost_per_unit,
            sell_price=p.sell_price,
            last_price_update=p.last_price_update.isoformat() if p.last_price_update else None,
            image_data=image_data_list
        ))
    
    return result


@app.post("/products/{product_id}/update-price", response_model=ProductResponse)
async def update_price(product_id: int):

    result = await pricing_service.scrape_and_update_price(product_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product = pricing_service.get_product(product_id)

    image_data_list = []
    if product.image_data:
        try:
            image_data_list = json.loads(product.image_data)
        except:
            pass

    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        lowest_seller=product.lowest_seller,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        sell_price=product.sell_price,
        last_price_update=product.last_price_update.isoformat() if product.last_price_update else None,
        image_data=image_data_list
    )


@app.get("/products/{product_id}/history", response_model=List[PriceHistoryResponse])
def price_history(product_id: int):

    history = pricing_service.get_price_history(product_id)

    return [
        PriceHistoryResponse(
            price=h.price,
            seller=h.seller,
            timestamp=h.timestamp.isoformat()
        )
        for h in history
    ]


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    deleted = pricing_service.delete_product(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@app.post("/auth/register")
def register(user: UserCreate):

    created = auth_service.register(user.username, user.password)

    if not created:
        raise HTTPException(status_code=400, detail="Username exists")

    return {"id": created.id, "username": created.username}


@app.post("/auth/login")
def login(data: LoginRequest):

    user = auth_service.login(data.username, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"id": user.id, "username": user.username}