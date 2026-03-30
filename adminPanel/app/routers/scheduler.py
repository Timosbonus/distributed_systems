from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.product_service import ProductService


router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.get("/status")
def get_scheduler_status(db: Session = Depends(get_db)):
    service = ProductService(db)
    products = service.get_all_products()

    return {
        "running": True,
        "products_needing_update": len(products),
        "total_products": len(products)
    }


@router.post("/run")
async def run_scheduler(db: Session = Depends(get_db)):
    service = ProductService(db)
    products = service.get_all_products()
    updated = []
    failed = []

    for p in products:
        try:
            result = await service.scrape_and_update_price(p.id)
            if result:
                updated.append(p.id)
            else:
                failed.append(p.id)
        except Exception as e:
            print(f"Failed to update product {p.id}: {e}")
            failed.append(p.id)

    return {"updated": updated, "failed": failed}