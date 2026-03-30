from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.services.product_service import ProductService


router = APIRouter(prefix="/pricing", tags=["pricing"])


class SuggestedPriceResponse:
    def __init__(self, id: int, product_id: int, product_name: str, suggested_price: float, 
                 current_price: float, competitor_price: float, competitor_name: str,
                 percentage_change: float, status: str, created_at: str):
        self.id = id
        self.product_id = product_id
        self.product_name = product_name
        self.suggested_price = suggested_price
        self.current_price = current_price
        self.competitor_price = competitor_price
        self.competitor_name = competitor_name
        self.percentage_change = percentage_change
        self.status = status
        self.created_at = created_at

    @classmethod
    def from_model(cls, suggestion, product_name: str = None):
        return cls(
            id=suggestion.id,
            product_id=suggestion.product_id,
            product_name=product_name or f"Product {suggestion.product_id}",
            suggested_price=suggestion.suggested_price,
            current_price=suggestion.current_price,
            competitor_price=suggestion.competitor_price,
            competitor_name=suggestion.competitor_name,
            percentage_change=suggestion.percentage_change,
            status=suggestion.status,
            created_at=suggestion.created_at.isoformat()
        )


@router.get("/suggestions", response_model=List[dict])
def get_pending_suggestions(db: Session = Depends(get_db)):
    service = ProductService(db)
    suggestions = service.get_pending_suggestions()
    return [SuggestedPriceResponse.from_model(s).__dict__ for s in suggestions]


@router.post("/suggestions/{suggestion_id}/approve")
def approve_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    suggestion = service.approve_suggestion(suggestion_id)
    if not suggestion:
        return {"error": "Suggestion not found"}
    return {"message": "Price updated successfully"}


@router.post("/suggestions/{suggestion_id}/reject")
def reject_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    service = ProductService(db)
    suggestion = service.reject_suggestion(suggestion_id)
    if not suggestion:
        return {"error": "Suggestion not found"}
    return {"message": "Suggestion rejected"}
