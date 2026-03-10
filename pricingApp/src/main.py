from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

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


class ProductResponse(BaseModel):
    id: int
    name: str
    idealo_link: str
    lowest_price: Optional[float] = None
    quantity: Optional[int] = 0
    cost_per_unit: Optional[float] = None
    description: Optional[str] = None


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
        description=product.description
    )
    return ProductResponse(
        id=new_product.id,
        name=new_product.name,
        idealo_link=new_product.idealo_link,
        lowest_price=new_product.lowest_price,
        quantity=new_product.quantity,
        cost_per_unit=new_product.cost_per_unit,
        description=new_product.description
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
            description=p.description
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
