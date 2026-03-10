from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json

from src.adapters.database import Database
from src.adapters.scraper import Scraper
from src.domain.services import PricingService, AuthService
from src.domain.entities import Product

app = FastAPI(title="Pricing App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()
scraper = Scraper()
pricing_service = PricingService(database=db, scraper=scraper)
auth_service = AuthService(database=db)


class ProductCreate(BaseModel):
    name: str
    idealo_link: str
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    idealo_link: Optional[str] = None
    quantity: Optional[int] = None
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    idealo_link: str
    lowest_price: Optional[float] = None
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None
    image_data: Optional[List[str]] = None


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
        image_data=serialize_images(product.image_data)
    )
    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        description=new_product.description,
        image_data=parse_images(new_product.image_data)
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
            quantity=p.quantity,
            cost_per_unit=p.cost_per_unit,
            description=p.description,
            image_data=parse_images(p.image_data)
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
        image_data=serialize_images(product.image_data)
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(
        id=updated.id,
        name=updated.name,
        idealo_link=updated.idealo_link,
        lowest_price=updated.lowest_price,
        quantity=updated.quantity,
        cost_per_unit=updated.cost_per_unit,
        description=updated.description,
        image_data=parse_images(updated.image_data)
    )


@app.post("/products/{product_id}/update-price", response_model=ProductResponse)
def update_product_price(product_id: int):
    price = pricing_service.update_price(product_id)
    if price is None:
        raise HTTPException(status_code=404, detail="Product not found")
    product = pricing_service.get_product(product_id)
    return ProductResponse(
        id=product.id,
        name=product.name,
        idealo_link=product.idealo_link,
        lowest_price=product.lowest_price,
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        image_data=parse_images(product.image_data)
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
        quantity=product.quantity,
        cost_per_unit=product.cost_per_unit,
        description=product.description,
        image_data=parse_images(product.image_data)
    )


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
