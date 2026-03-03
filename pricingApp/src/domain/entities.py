from sqlalchemy import Column, Integer, String, Float
from src.adapters.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    idealo_link = Column(String, nullable=False)
    lowest_price = Column(Float, nullable=True)

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, idealo_link={self.idealo_link}, lowest_price={self.lowest_price})>"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"
