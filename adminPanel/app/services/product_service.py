from typing import Optional, List
from datetime import datetime, timedelta
import json

from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.excluded_seller import ExcludedSeller
from app.models.audit_log import AuditLog
from app.models.suggested_price import SuggestedPrice
from app.services.scraper import Scraper


class ProductService:
    def __init__(self, db_session):
        self.db = db_session
        self.scraper = Scraper()
        self.price_change_threshold = 5.0

    def calculate_sell_price(self, lowest_price: Optional[float], cost: Optional[float], minimum_margin: Optional[float] = None) -> Optional[float]:
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

    def add_product(self, name: str, idealo_link: str, quantity: int = 0, cost_per_unit: Optional[float] = None,
                    image_data: Optional[List[str]] = None, description: Optional[str] = None,
                    update_interval_hours: int = 24, minimum_margin: Optional[float] = None,
                    manual_sell_price: Optional[float] = None) -> Product:
        product = Product(
            name=name,
            idealo_link=idealo_link,
            quantity=quantity,
            cost_per_unit=cost_per_unit,
            image_data=json.dumps(image_data) if image_data else None,
            description=description,
            update_interval_hours=update_interval_hours,
            minimum_margin=minimum_margin,
            manual_sell_price=manual_sell_price
        )
        self.db.add(product)
        self.db.commit()
        self.db.refresh(product)
        return product

    def get_all_products(self) -> List[Product]:
        return self.db.query(Product).all()

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def delete_product(self, product_id: int) -> bool:
        product = self.get_product(product_id)
        if not product:
            return False
        self.db.delete(product)
        self.db.commit()
        return True

    def update_product(self, product_id: int, name: Optional[str] = None, idealo_link: Optional[str] = None,
                       quantity: Optional[int] = None, cost_per_unit: Optional[float] = None,
                       description: Optional[str] = None, update_interval_hours: Optional[int] = None,
                       minimum_margin: Optional[float] = None, image_data: Optional[List[str]] = None,
                       manual_sell_price: Optional[float] = None) -> Optional[Product]:
        product = self.get_product(product_id)
        if not product:
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

        self.db.commit()
        self.db.refresh(product)
        return product

    async def scrape_and_update_price(self, product_id: int) -> Optional[dict]:
        product = self.get_product(product_id)
        if not product:
            return None

        excluded_sellers = self.get_excluded_sellers()
        result = await self.scraper.fetch_and_scrape(product.idealo_link, excluded_sellers=excluded_sellers)

        if not result:
            if excluded_sellers:
                self.log_audit(
                    product_id, "scrape_failed",
                    product.sell_price, product.sell_price,
                    f"Price update skipped - all sellers excluded: {', '.join(excluded_sellers)}"
                )
            if product.cost_per_unit is not None and product.minimum_margin is not None:
                product.sell_price = round(product.cost_per_unit * (1 + product.minimum_margin / 100), 2)
                product.last_price_update = datetime.utcnow()
                self.db.commit()
            return None

        price = result["price"]
        seller = result["seller"]

        product.lowest_price = price
        product.lowest_seller = seller
        product.last_price_update = datetime.utcnow()

        if product.manual_sell_price is not None:
            product.sell_price = product.manual_sell_price
        elif product.cost_per_unit is not None:
            new_price = self.calculate_sell_price(price, product.cost_per_unit, product.minimum_margin)
            current_price = product.sell_price or 0
            
            if excluded_sellers:
                reason_suffix = f" (excluded sellers: {', '.join(excluded_sellers)})"
            else:
                reason_suffix = ""
            
            if current_price > 0 and new_price != current_price:
                percent_change = abs((new_price - current_price) / current_price * 100)
                if percent_change > self.price_change_threshold:
                    self.create_suggested_price(
                        product_id, new_price, current_price, price, seller
                    )
                    self.log_audit(
                        product_id, "price_suggestion_created",
                        current_price, new_price,
                        f"Price change of {percent_change:.1f}% suggested (€{current_price} -> €{new_price}) due to {seller} at €{price}{reason_suffix}"
                    )
                else:
                    old_price = product.sell_price
                    product.sell_price = new_price
                    self.log_audit(
                        product_id, "price_change",
                        old_price, new_price,
                        f"Price lowered from €{old_price} to €{new_price} because {seller} dropped to €{price}{reason_suffix}"
                    )
            else:
                product.sell_price = new_price
                self.log_audit(
                    product_id, "price_change",
                    current_price, new_price,
                    f"Price set to €{new_price} because {seller} at €{price}{reason_suffix}"
                )

        history = PriceHistory(
            product_id=product_id,
            price=price,
            seller=seller,
            timestamp=datetime.utcnow()
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(product)

        return result

    def get_price_history(self, product_id: int, limit: int = 10) -> List[PriceHistory]:
        return (
            self.db.query(PriceHistory)
            .filter(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.timestamp.desc())
            .limit(limit)
            .all()
        )

    def get_products_needing_update(self) -> List[Product]:
        products = self.get_all_products()
        now = datetime.utcnow()
        result = []

        for p in products:
            if not p.last_price_update:
                result.append(p)
                continue
            interval = timedelta(hours=p.update_interval_hours or 24)
            if now - p.last_price_update >= interval:
                result.append(p)

        return result

    async def run_scheduled_updates(self):
        products = self.get_products_needing_update()
        for p in products:
            try:
                await self.scrape_and_update_price(p.id)
            except Exception as e:
                print(f"Update failed for {p.name}: {e}")

    def get_excluded_sellers(self) -> List[str]:
        sellers = self.db.query(ExcludedSeller).all()
        return [s.seller_name for s in sellers]

    def add_excluded_seller(self, seller_name: str, reason: str = None) -> ExcludedSeller:
        seller = ExcludedSeller(seller_name=seller_name, reason=reason)
        self.db.add(seller)
        self.db.commit()
        self.db.refresh(seller)
        return seller

    def remove_excluded_seller(self, seller_name: str) -> bool:
        seller = self.db.query(ExcludedSeller).filter(ExcludedSeller.seller_name == seller_name).first()
        if not seller:
            return False
        self.db.delete(seller)
        self.db.commit()
        return True

    def get_all_excluded_sellers(self) -> List[ExcludedSeller]:
        return self.db.query(ExcludedSeller).all()

    def log_audit(self, product_id: int, action: str, old_value: float, new_value: float, reason: str):
        log = AuditLog(
            product_id=product_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            reason=reason
        )
        self.db.add(log)
        self.db.commit()

    def get_audit_logs(self, product_id: int, limit: int = 50) -> List[AuditLog]:
        return (
            self.db.query(AuditLog)
            .filter(AuditLog.product_id == product_id)
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )

    def create_suggested_price(self, product_id: int, suggested_price: float, current_price: float,
                                competitor_price: float, competitor_name: str) -> SuggestedPrice:
        percent_change = abs((suggested_price - current_price) / current_price * 100) if current_price > 0 else 0
        suggestion = SuggestedPrice(
            product_id=product_id,
            suggested_price=suggested_price,
            current_price=current_price,
            competitor_price=competitor_price,
            competitor_name=competitor_name,
            percentage_change=percent_change,
            status="pending"
        )
        self.db.add(suggestion)
        self.db.commit()
        self.db.refresh(suggestion)
        return suggestion

    def get_pending_suggestions(self) -> List[SuggestedPrice]:
        return self.db.query(SuggestedPrice).filter(SuggestedPrice.status == "pending").all()

    def approve_suggestion(self, suggestion_id: int) -> Optional[SuggestedPrice]:
        suggestion = self.db.query(SuggestedPrice).filter(SuggestedPrice.id == suggestion_id).first()
        if not suggestion:
            return None
        product = self.get_product(suggestion.product_id)
        if not product:
            return None
        old_price = product.sell_price
        product.sell_price = suggestion.suggested_price
        suggestion.status = "approved"
        self.db.commit()
        self.log_audit(
            product.id, "price_change_approved",
            old_price, suggestion.suggested_price,
            f"Approved price change from €{old_price} to €{suggestion.suggested_price} (suggested due to {suggestion.competitor_name} at €{suggestion.competitor_price})"
        )
        self.db.refresh(suggestion)
        return suggestion

    def reject_suggestion(self, suggestion_id: int) -> Optional[SuggestedPrice]:
        suggestion = self.db.query(SuggestedPrice).filter(SuggestedPrice.id == suggestion_id).first()
        if not suggestion:
            return None
        suggestion.status = "rejected"
        self.db.commit()
        self.db.refresh(suggestion)
        return suggestion