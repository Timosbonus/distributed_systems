import sys
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import json
import threading
import time

from src.adapters.database import Database
from src.adapters.scraper import Scraper
from src.domain.services import PricingService, AuthService
from src.domain.entities import Product

db = Database()
scraper = Scraper()
pricing_service = PricingService(database=db, scraper=scraper)
auth_service = AuthService(database=db)

scheduler_running = True


def scheduler_loop():
    """Background scheduler that runs every minute and checks for updates."""
    while scheduler_running:
        try:
            pricing_service.run_scheduled_updates()
        except Exception as e:
            print(f"Scheduler error: {e}")
        time.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    global scheduler_running
    scheduler_running = False
    await scraper.close()


app = FastAPI(title="Pricing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()


class ProductCreate(BaseModel):
    name: str
    idealo_link: str
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None
    update_interval_hours: Optional[int] = 24


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    idealo_link: Optional[str] = None
    quantity: Optional[int] = None
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None
    sell_price: Optional[float] = None
    update_interval_hours: Optional[int] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    idealo_link: str
    lowest_price: Optional[float] = None
    lowest_seller: Optional[str] = None
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None
    sell_price: Optional[float] = None
    update_interval_hours: Optional[int] = 24
    last_price_update: Optional[str] = None


class PriceHistoryResponse(BaseModel):
    id: int
    product_id: int
    price: float
    seller: Optional[str] = None
    timestamp: str


def parse_images(images_json: Optional[str]) -> Optional[List[str]]:
    if not images_json:
        return None
    try:
        return json.loads(images_json)
    except:
        return None


def serialize_images(images: Optional[List[str]]) -> Optional[str]:
    if not images:
        return None
    return json.dumps(images)


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str


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
        description=product.description,
        image_data=serialize_images(product.image_data),
        update_interval_hours=product.update_interval_hours
    )
    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        lowest_seller=new_product.lowest_seller,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        description=new_product.description,
        image_data=parse_images(new_product.image_data),
        sell_price=new_product.sell_price,
        update_interval_hours=new_product.update_interval_hours,
        last_price_update=new_product.last_price_update.isoformat() if new_product.last_price_update else None
    )


@app.get("/products", response_model=list[ProductResponse])
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
            description=p.description,
            image_data=parse_images(p.image_data),
            sell_price=p.sell_price,
            update_interval_hours=p.update_interval_hours,
            last_price_update=p.last_price_update.isoformat() if p.last_price_update else None
        )
        for p in products
    ]


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate):
    updated = pricing_service.update_product(
        product_id=product_id,
        name=product.name,
        idealo_link=product.idealo_link,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        image_data=serialize_images(product.image_data),
        sell_price=product.sell_price,
        update_interval_hours=product.update_interval_hours
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=updated.id,
        name=updated.name,
        idealo_link=updated.idealo_link,
        lowest_price=updated.lowest_price,
        lowest_seller=updated.lowest_seller,
        quantity=updated.quantity,
        cost_per_unit=updated.cost_per_unit,
        description=updated.description,
        image_data=parse_images(updated.image_data),
        sell_price=updated.sell_price,
        update_interval_hours=updated.update_interval_hours,
        last_price_update=updated.last_price_update.isoformat() if updated.last_price_update else None
    )


@app.post("/products/{product_id}/update-price", response_model=ProductResponse)
def update_product_price(product_id: int):
    result = pricing_service.scrape_and_update_price(product_id)
    if result is None:
        product = pricing_service.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=503, detail="Could not fetch prices from idealo. The website may be blocking requests or is unavailable.")
    product = pricing_service.get_product(product_id)
    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        lowest_seller=product.lowest_seller,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        image_data=parse_images(product.image_data),
        sell_price=product.sell_price,
        update_interval_hours=product.update_interval_hours,
        last_price_update=product.last_price_update.isoformat() if product.last_price_update else None
    )


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int):
    product = pricing_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        lowest_seller=product.lowest_seller,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        image_data=parse_images(product.image_data),
        sell_price=product.sell_price,
        update_interval_hours=product.update_interval_hours,
        last_price_update=product.last_price_update.isoformat() if product.last_price_update else None
    )


@app.get("/products/{product_id}/history", response_model=List[PriceHistoryResponse])
def get_product_history(product_id: int, limit: int = 10):
    product = pricing_service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    history = pricing_service.get_price_history(product_id, limit)
    return [
        PriceHistoryResponse(
            id=h.id,
            product_id=h.product_id,
            price=h.price,
            seller=h.seller,
            timestamp=h.timestamp.isoformat()
        )
        for h in history
    ]


@app.post("/scheduler/run")
def run_scheduler():
    results = pricing_service.run_scheduled_updates()
    return results


@app.get("/scheduler/status")
def get_scheduler_status():
    products = pricing_service.get_products_needing_update()
    return {
        "products_needing_update": len(products),
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "last_update": p.last_price_update.isoformat() if p.last_price_update else None,
                "interval_hours": p.update_interval_hours
            }
            for p in products
        ]
    }


@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    success = pricing_service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}


@app.post("/auth/register", response_model=UserResponse)
def register(user: UserCreate):
    new_user = auth_service.register(username=user.username, password=user.password)
    if not new_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    return UserResponse(id=new_user.id, username=new_user.username)


@app.post("/auth/login")
def login(request: LoginRequest):
    user = auth_service.login(username=request.username, password=request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id, "username": user.username}
