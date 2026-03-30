from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db
from app.services.product_service import ProductService


router = APIRouter(prefix="/audit", tags=["audit"])


class AuditLogResponse:
    def __init__(self, id: int, product_id: int, action: str, old_value: float, new_value: float, reason: str, timestamp: str):
        self.id = id
        self.product_id = product_id
        self.action = action
        self.old_value = old_value
        self.new_value = new_value
        self.reason = reason
        self.timestamp = timestamp

    @classmethod
    def from_model(cls, log):
        return cls(
            id=log.id,
            product_id=log.product_id,
            action=log.action,
            old_value=log.old_value,
            new_value=log.new_value,
            reason=log.reason,
            timestamp=log.timestamp.isoformat()
        )


@router.get("/products/{product_id}", response_model=List[dict])
def get_audit_logs(product_id: int, limit: int = 50, db: Session = Depends(get_db)):
    service = ProductService(db)
    logs = service.get_audit_logs(product_id, limit)
    return [AuditLogResponse.from_model(log).__dict__ for log in logs]
