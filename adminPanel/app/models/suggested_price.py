from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from datetime import datetime
from app.db.database import Base


class SuggestedPrice(Base):
    __tablename__ = "suggested_prices"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    suggested_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    competitor_price = Column(Float, nullable=True)
    competitor_name = Column(String, nullable=True)
    percentage_change = Column(Float, nullable=False)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
