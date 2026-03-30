from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.dependencies import get_db
from app.services.product_service import ProductService


router = APIRouter(prefix="/sellers", tags=["sellers"])


class ExcludedSellerCreate(BaseModel):
    seller_name: str
    reason: Optional[str] = None


class ExcludedSellerResponse(BaseModel):
    id: int
    seller_name: str
    reason: Optional[str]
    excluded_at: str


@router.get("/excluded", response_model=List[ExcludedSellerResponse])
def get_excluded_sellers(db: Session = Depends(get_db)):
    service = ProductService(db)
    sellers = service.get_all_excluded_sellers()
    return [
        ExcludedSellerResponse(
            id=s.id,
            seller_name=s.seller_name,
            reason=s.reason,
            excluded_at=s.excluded_at.isoformat()
        )
        for s in sellers
    ]


@router.post("/excluded", response_model=ExcludedSellerResponse)
async def add_excluded_seller(seller: ExcludedSellerCreate, db: Session = Depends(get_db)):
    service = ProductService(db)
    new_seller = service.add_excluded_seller(seller.seller_name, seller.reason)
    
    await service.run_scheduled_updates()
    
    return ExcludedSellerResponse(
        id=new_seller.id,
        seller_name=new_seller.seller_name,
        reason=new_seller.reason,
        excluded_at=new_seller.excluded_at.isoformat()
    )


@router.delete("/excluded/{seller_name}")
async def remove_excluded_seller(seller_name: str, db: Session = Depends(get_db)):
    service = ProductService(db)
    success = service.remove_excluded_seller(seller_name)
    if not success:
        return {"message": "Seller not found"}
    
    await service.run_scheduled_updates()
    
    return {"message": "Seller removed from exclusion list"}
