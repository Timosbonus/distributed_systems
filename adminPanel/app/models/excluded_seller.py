from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.db.database import Base


class ExcludedSeller(Base):
    __tablename__ = "excluded_sellers"

    id = Column(Integer, primary_key=True, index=True)
    seller_name = Column(String, nullable=False, unique=True)
    reason = Column(String, nullable=True)
    excluded_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
