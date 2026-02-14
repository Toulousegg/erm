from fastapi import APIRouter
from production_model import Production
from sqlalchemy.orm import Session, Depends
from core.dependencies import CreateSession
from core.security import verify_token, create_token


production_router = APIRouter(prefix="/production", tags=["production"])

@production_router.get("/")
def show_production(session: Session = Depends(CreateSession), user: str = Depends(verify_token), token: str = Depends(create_token)):
    production_items = session.query(Production).all()
    return {
        "message": "Production items retrieved successfully",
        "items": production_items
    }
    