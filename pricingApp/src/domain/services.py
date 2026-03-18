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


    def calculate_sell_price(self, lowest_price: float, cost: float, minimum_margin: Optional[float] = None) -> float:
        if lowest_price is None:
            if cost and minimum_margin:
                return round(cost * (1 + minimum_margin / 100), 2)
            elif cost:
                return round(cost * 1.01, 2)
            return None

        if lowest_price <= cost:
            if minimum_margin:
                return round(cost * (1 + minimum_margin / 100), 2)
            return round(cost * 1.01, 2)

        margin = lowest_price - cost
        if minimum_margin and margin < (lowest_price * minimum_margin / 100):
            return round(lowest_price - (lowest_price * minimum_margin / 100) + 0.01, 2)

        return round(lowest_price - 0.01, 2)


    def add_product(
        self,
        name: str,
        idealo_link: str,
        quantity: Optional[int] = 0,
        cost_per_unit: Optional[float] = None,
        image_data: Optional[List[str]] = None,
        description: Optional[str] = None,
        update_interval_hours: Optional[int] = 24,
        minimum_margin: Optional[float] = None,
        manual_sell_price: Optional[float] = None
    ) -> Product:

        session = self.database.get_session()

        image_json = json.dumps(image_data) if image_data else None

        product = Product(
            name=name,
            idealo_link=idealo_link,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            image_data=image_json,
            description=description,
            update_interval_hours=update_interval_hours,
            minimum_margin=minimum_margin,
            manual_sell_price=manual_sell_price
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
            if product.cost_per_unit is not None and product.minimum_margin is not None:
                product.sell_price = round(product.cost_per_unit * (1 + product.minimum_margin / 100), 2)
                product.last_price_update = datetime.utcnow()
                session.commit()
                session.close()
                return None
            session.close()
            return None

        price = result["price"]
        seller = result["seller"]

        product.lowest_price = price
        product.lowest_seller = seller
        product.last_price_update = datetime.utcnow()

        if product.manual_sell_price is not None:
            product.sell_price = product.manual_sell_price
        elif product.cost_per_unit is not None:
            product.sell_price = self.calculate_sell_price(price, product.cost_per_unit, product.minimum_margin)

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


    def update_product(self, product_id: int, name: str = None, idealo_link: str = None, quantity: int = None, cost_per_unit: float = None, description: str = None, update_interval_hours: int = None, minimum_margin: float = None, image_data: List[str] = None, manual_sell_price: float = None):
        session = self.database.get_session()

        product = session.query(Product).filter(Product.id == product_id).first()

        if not product:
            session.close()
            return None

        if name is not None:
            product.name = name
        if idealo_link is not None:
            product.idealo_link = idealo_link
        if quantity is not None:
            product.quantity = quantity
        if cost_per_unit is not None:
            product.cost_per_unit = cost_per_unit
        if description is not None:
            product.description = description
        if update_interval_hours is not None:
            product.update_interval_hours = update_interval_hours
        if minimum_margin is not None:
            product.minimum_margin = minimum_margin
        if image_data is not None:
            product.image_data = json.dumps(image_data)
        product.manual_sell_price = manual_sell_price

        if product.manual_sell_price is not None:
            product.sell_price = product.manual_sell_price
        elif product.cost_per_unit is not None and product.lowest_price is not None:
            product.sell_price = self.calculate_sell_price(product.lowest_price, product.cost_per_unit, product.minimum_margin)

        session.commit()
        session.refresh(product)
        session.close()

        return product


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