from sqlalchemy import Column, Integer, String, Float, DateTime
from app.db.database import Base


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
    manual_sell_price = Column(Float, nullable=True)
    minimum_margin = Column(Float, nullable=True)
    update_interval_hours = Column(Integer, nullable=True, default=24)
    last_price_update = Column(DateTime, nullable=True)