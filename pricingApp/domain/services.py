from pricingApp.domain.entities import Product
from pricingApp.ports.interfaces import PricePort, DatabasePort


class PricingService:
    def __init__(self, database: DatabasePort, scraper: PricePort):
        self.database = database
        self.scraper = scraper

    def add_product(self, name: str, idealo_link: str) -> Product:
        session = self.database.get_session()
        product = Product(name=name, idealo_link=idealo_link, lowest_price=None)
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
