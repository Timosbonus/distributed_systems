from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db.database import get_engine, create_tables
from app.core.config import settings
from app.routers import products, auth, scheduler
from app.internal import admin
from app.services.product_service import ProductService
from app.dependencies import get_database


engine = get_engine(settings.database_url)
create_tables(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    db_factory = get_database()
    db = db_factory()
    service = ProductService(db)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(service.run_scheduled_updates, "interval", minutes=1)
    scheduler.start()

    yield

    scheduler.shutdown()
    db.close()


app = FastAPI(title="Pricing App", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(scheduler.router)
app.include_router(admin.router)