from src.domain.entities import Product, User, PriceHistory
from src.ports.interfaces import PricePort, DatabasePort

from typing import Optional, List, Union
from datetime import datetime, timedelta
import hashlib
import json


class PricingService:

    def __init__(self, database: DatabasePort, scraper: PricePort):
        self.database = database
        self.scraper = scraper


    def calculate_sell_price(self, lowest_price: float, cost: float) -> float:

        if lowest_price <= cost:
            return round(cost * 1.01, 2)

        return round(lowest_price - 0.01, 2)


    def add_product(
        self,
        name: str,
        idealo_link: str,
        quantity: Optional[int] = 0,
        cost_per_unit: Optional[float] = None,
        image_data: Optional[List[str]] = None
    ) -> Product:

        session = self.database.get_session()

        image_json = json.dumps(image_data) if image_data else None

        product = Product(
            name=name,
            idealo_link=idealo_link,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            image_data=image_json
        )

        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()

        return product


    async def scrape_and_update_price(self, product_id: int):

        session = self.database.get_session()

        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            session.close()
            return None

        result = await self.scraper.fetch_and_scrape(product.idealo_link)

        if not result:
            session.close()
            return None

        price = result["price"]
        seller = result["seller"]

        product.lowest_price = price
        product.lowest_seller = seller
        product.last_price_update = datetime.utcnow()

        if product.cost_per_unit is not None:
            product.sell_price = self.calculate_sell_price(price, product.cost_per_unit)

        history = PriceHistory(
            product_id=product_id,
            price=price,
            seller=seller,
            timestamp=datetime.utcnow()
        )

        session.add(history)

        session.commit()
        session.refresh(product)
        session.close()

        return result


    def get_products_needing_update(self):

        session = self.database.get_session()

        products = session.query(Product).all()

        now = datetime.utcnow()

        result = []

        for p in products:

            if not p.last_price_update:
                result.append(p)
                continue

            interval = timedelta(hours=p.update_interval_hours or 24)

            if now - p.last_price_update >= interval:
                result.append(p)

        session.close()

        return result


    async def run_scheduled_updates(self):

        products = self.get_products_needing_update()

        for p in products:
            try:
                await self.scrape_and_update_price(p.id)
            except Exception as e:
                print(f"Update failed for {p.name}: {e}")


    def get_price_history(self, product_id: int, limit: int = 10):

        session = self.database.get_session()

        history = (
            session.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.timestamp.desc())
            .limit(limit)
            .all()
        )

        session.close()

        return history


    def get_all_products(self):

        session = self.database.get_session()

        products = session.query(Product).all()

        session.close()

        return products


    def get_product(self, product_id: int):

        session = self.database.get_session()

        product = session.query(Product).filter(Product.id == product_id).first()

        session.close()

        return product


    def delete_product(self, product_id: int) -> bool:

        session = self.database.get_session()

        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            session.close()
            return False

        session.delete(product)
        session.commit()
        session.close()

        return True


class AuthService:

    def __init__(self, database: DatabasePort):
        self.database = database


    def hash_password(self, password: str):

        return hashlib.sha256(password.encode()).hexdigest()


    def register(self, username: str, password: str):

        session = self.database.get_session()

        existing = session.query(User).filter(User.username == username).first()

        if existing:
            session.close()
            return None

        user = User(
            username=username,
            password_hash=self.hash_password(password)
        )

        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()

        return user


    def login(self, username: str, password: str):

        session = self.database.get_session()

        user = session.query(User).filter(User.username == username).first()

        if not user or user.password_hash != self.hash_password(password):
            session.close()
            return None

        session.close()

        return user