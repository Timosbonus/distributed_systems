from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import asyncio
import json

from src.adapters.database import Database
from src.adapters.scraper import Scraper
from src.domain.services import PricingService, AuthService


db = Database()
scraper = Scraper()
pricing_service = PricingService(database=db, scraper=scraper)
auth_service = AuthService(database=db)

scheduler_running = True


async def scheduler_loop():
    while scheduler_running:
        try:
            await pricing_service.run_scheduled_updates()
        except Exception as e:
            print(f"Scheduler error: {e}")

        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):

    task = asyncio.create_task(scheduler_loop())

    yield

    global scheduler_running
    scheduler_running = False

    task.cancel()

    await scraper.close()


app = FastAPI(title="Pricing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductCreate(BaseModel):
    name: str
    idealo_link: str
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None


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
        cost_per_unit=product.cost_per_unit
    )

    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        lowest_seller=new_product.lowest_seller,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        sell_price=new_product.sell_price,
        last_price_update=new_product.last_price_update.isoformat() if new_product.last_price_update else None
    )


@app.get("/products", response_model=List[ProductResponse])
def get_products():

    products = pricing_service.get_all_products()

    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            idealo_link=p.idealo_link,
            lowest_price=p.lowest_price,
            lowest_seller=p.lowest_seller,
            quantity=p.quantity,
            cost_per_unit=p.cost_per_unit,
            sell_price=p.sell_price,
            last_price_update=p.last_price_update.isoformat() if p.last_price_update else None
        )
        for p in products
    ]


@app.post("/products/{product_id}/update-price", response_model=ProductResponse)
async def update_price(product_id: int):

    result = await pricing_service.scrape_and_update_price(product_id)

    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")

    product = pricing_service.get_product(product_id)

    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        lowest_seller=product.lowest_seller,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        sell_price=product.sell_price,
        last_price_update=product.last_price_update.isoformat() if product.last_price_update else None
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