from fastapi import APIRouter


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/health")
def health_check():
    return {"status": "ok"}