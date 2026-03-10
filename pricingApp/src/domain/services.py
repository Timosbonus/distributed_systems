from src.domain.entities import Product, User
from src.ports.interfaces import PricePort, DatabasePort
import hashlib
from typing import Optional


class PricingService:
    def __init__(self, database: DatabasePort, scraper: PricePort):
        self.database = database
        self.scraper = scraper

    def add_product(self, name: str, idealo_link: str, quantity: Optional[int] = 0, cost_per_unit: Optional[float] = None, description: Optional[str] = None) -> Product:
        session = self.database.get_session()
        product = Product(name=name, idealo_link=idealo_link, lowest_price=None, quantity=quantity, cost_per_unit=cost_per_unit, description=description)
        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def calculate_lowest_price(self, product_id: int) -> float | None:
        session = self.database.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            session.close()
            return None

        price = self.scraper.scrape_price(product.idealo_link)
        if price is not None:
            product.lowest_price = price
            session.commit()
        
        session.close()
        return price

    def get_all_products(self) -> list[Product]:
        session = self.database.get_session()
        products = session.query(Product).all()
        session.close()
        return products

    def get_product(self, product_id: int) -> Product | None:
        session = self.database.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        session.close()
        return product


class AuthService:
    def __init__(self, database: DatabasePort):
        self.database = database

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str) -> User | None:
        session = self.database.get_session()
        existing = session.query(User).filter(User.username == username).first()
        if existing:
            session.close()
            return None
        
        user = User(username=username, password_hash=self.hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return user

    def login(self, username: str, password: str) -> User | None:
        session = self.database.get_session()
        user = session.query(User).filter(User.username == username).first()
        if not user or user.password_hash != self.hash_password(password):
            session.close()
            return None
        session.close()
        return user
