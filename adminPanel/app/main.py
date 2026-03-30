from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import get_engine, create_tables, SessionLocal
from app.core.config import settings
from app.routers import products, auth, scheduler as scheduler_router, sellers, audit
from app.internal import admin
from app.services.product_service import ProductService


engine = get_engine(settings.database_url)
create_tables(engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.db.database import SessionLocal

    def run_updates():
        db = SessionLocal()
        try:
            service = ProductService(db)
            service.run_scheduled_updates_sync()
        finally:
            db.close()

    job_scheduler = AsyncIOScheduler()
    job_scheduler.add_job(run_updates, "interval", seconds=30)
    job_scheduler.start()
    yield
    job_scheduler.shutdown()



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
app.include_router(scheduler_router.router)
app.include_router(sellers.router)
app.include_router(audit.router)
app.include_router(admin.router)