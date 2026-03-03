from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()


class Database:
    def __init__(self, database_url: str = "sqlite:///./pricing.db"):
        self.engine = create_engine(database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self.SessionLocal()

    def create_all(self):
        Base.metadata.create_all(bind=self.engine)
