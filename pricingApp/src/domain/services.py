from src.domain.entities import Product, User, PriceHistory
from src.ports.interfaces import PricePort, DatabasePort
import hashlib
from typing import Optional, List
from datetime import datetime, timedelta
import json


class PricingService:
    def __init__(self, database: DatabasePort, scraper: PricePort):
        self.database = database
        self.scraper = scraper

    def calculate_sell_price(self, lowest_price: float, cost_per_unit: float) -> float:
        """
        Calculate sell price based on lowest price and cost.
        Rules:
        - Never go below cost_per_unit
        - If lowest price is above cost, sell at lowest price - 0.01 (to be cheapest)
        - If lowest price is at or below cost, sell at cost + 1% minimum margin
        """
        if lowest_price <= cost_per_unit:
            return round(cost_per_unit * 1.01, 2)
        return round(lowest_price - 0.01, 2)

    def add_product(self, name: str, idealo_link: str, quantity: Optional[int] = 0, cost_per_unit: Optional[float] = None, description: Optional[str] = None, image_data: Optional[str] = None, update_interval_hours: Optional[int] = 24) -> Product:
        session = self.database.get_session()
        product = Product(
            name=name, 
            idealo_link=idealo_link, 
            lowest_price=None,
            lowest_seller=None,
            quantity=quantity, 
            cost_per_unit=cost_per_unit, 
            description=description, 
            image_data=image_data,
            update_interval_hours=update_interval_hours,
            last_price_update=None
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def update_product(self, product_id: int, name: Optional[str] = None, idealo_link: Optional[str] = None, quantity: Optional[int] = None, cost_per_unit: Optional[float] = None, description: Optional[str] = None, image_data: Optional[str] = None, sell_price: Optional[float] = None, update_interval_hours: Optional[int] = None) -> Product | None:
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
            if product.lowest_price:
                product.sell_price = self.calculate_sell_price(product.lowest_price, cost_per_unit)
        if description is not None:
            product.description = description
        if image_data is not None:
            product.image_data = image_data
        if sell_price is not None:
            product.sell_price = sell_price
        if update_interval_hours is not None:
            product.update_interval_hours = update_interval_hours
        
        session.commit()
        session.refresh(product)
        session.close()
        return product

    def scrape_and_update_price(self, product_id: int) -> dict | None:
        """
        Scrape prices from idealo, find cheapest, store in history, and update product.
        """
        session = self.database.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            session.close()
            return None

        try:
            result = self.scraper.fetch_and_scrape_sync(product.idealo_link)
            if not result:
                session.close()
                return None

            cheapest_price = result['price']
            cheapest_seller = result['seller']
        except Exception as e:
            print(f"Error fetching {product.idealo_link}: {e}")
            session.close()
            return None

        product.lowest_price = cheapest_price
        product.lowest_seller = cheapest_seller
        product.last_price_update = datetime.utcnow()
        
        if product.cost_per_unit:
            product.sell_price = self.calculate_sell_price(cheapest_price, product.cost_per_unit)
        
        history_entry = PriceHistory(
            product_id=product_id,
            price=cheapest_price,
            seller=cheapest_seller,
            timestamp=datetime.utcnow()
        )
        session.add(history_entry)
        
        session.commit()
        session.refresh(product)
        session.close()
        
        return {
            'price': cheapest_price,
            'seller': cheapest_seller,
            'sell_price': product.sell_price
        }

    def get_products_needing_update(self) -> List[Product]:
        """
        Get all products that need their prices updated based on their update interval.
        """
        session = self.database.get_session()
        products = session.query(Product).all()
        
        needs_update = []
        now = datetime.utcnow()
        
        for product in products:
            if product.last_price_update is None:
                needs_update.append(product)
            else:
                interval = timedelta(hours=product.update_interval_hours or 24)
                if now - product.last_price_update >= interval:
                    needs_update.append(product)
        
        session.close()
        return needs_update

    def run_scheduled_updates(self) -> dict:
        """
        Run scheduled price updates for all products that need updating.
        """
        products_to_update = self.get_products_needing_update()
        results = {
            'updated': [],
            'failed': []
        }
        
        for product in products_to_update:
            try:
                result = self.scrape_and_update_price(product.id)
                if result:
                    results['updated'].append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'price': result['price'],
                        'seller': result['seller']
                    })
                else:
                    results['failed'].append({
                        'product_id': product.id,
                        'product_name': product.name,
                        'reason': 'No offers found'
                    })
            except Exception as e:
                results['failed'].append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'reason': str(e)
                })
        
        return results

    def get_price_history(self, product_id: int, limit: int = 10) -> List[PriceHistory]:
        """Get price history for a product."""
        session = self.database.get_session()
        history = session.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.timestamp.desc()).limit(limit).all()
        session.close()
        return history

    def update_price(self, product_id: int) -> float | None:
        session = self.database.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            session.close()
            return None

        result = self.scrape_and_update_price(product_id)
        
        session.close()
        return result['price'] if result else None

    def delete_product(self, product_id: int) -> bool:
        session = self.database.get_session()
        product = session.query(Product).filter(Product.id == product_id).first()
        if not product:
            session.close()
            return False
        
        session.query(PriceHistory).filter(PriceHistory.product_id == product_id).delete()
        
        session.delete(product)
        session.commit()
        session.close()
        return True

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
