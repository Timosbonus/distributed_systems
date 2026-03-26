from functools import lru_cache

from app.db.database import get_engine, get_session_factory, create_tables
from app.core.config import settings


@lru_cache
def get_database():
    engine = get_engine(settings.database_url)
    create_tables(engine)
    return get_session_factory(engine)


def get_db():
    db = get_database()
    session = db()
    try:
        yield session
    finally:
        session.close()