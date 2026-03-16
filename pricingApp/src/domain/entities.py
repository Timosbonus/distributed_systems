from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime
from src.adapters.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    idealo_link = Column(String, nullable=False)
    lowest_price = Column(Float, nullable=True)
    lowest_seller = Column(String, nullable=True)
    quantity = Column(Integer, nullable=True, default=0)
    cost_per_unit = Column(Float, nullable=True)
    description = Column(String, nullable=True)
    image_data = Column(String, nullable=True)
    sell_price = Column(Float, nullable=True)
    minimum_margin = Column(Float, nullable=True)
    update_interval_hours = Column(Integer, nullable=True, default=24)
    last_price_update = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, lowest_price={self.lowest_price}, lowest_seller={self.lowest_seller}, cost_per_unit={self.cost_per_unit}, sell_price={self.sell_price})>"


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    seller = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price={self.price}, seller={self.seller}, timestamp={self.timestamp})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
