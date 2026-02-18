from fastapi import APIRouter, Depends, HTTPException, status, Query
from production.production_model import Production
from sqlalchemy.orm import Session
from core.dependencies import CreateSession
from core.security import verify_token, create_token
from production.production_schema import query_production, create_production


production_router = APIRouter(prefix="/production", tags=["production"])

@production_router.get("/", response_model=list[query_production])
def show_production_by_client(client_name: str = Query(..., description="Client name"), session: Session = Depends(CreateSession), user: str = Depends(verify_token)
):
    
    production_projects = session.query(Production).filter(Production.client_name == client_name).all()

    if not production_projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Not found projects to '{client_name}'"
        )
    
    return production_projects



@production_router.post("/add")
def create_project_in_production(production: create_production, session: Session = Depends(CreateSession), user: str = Depends(verify_token)):
    access_token = create_token(user.id)

    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized, invalid token")
    
    new_production_item = Production(
        project_name=production.project_name,
        client_name=production.client_name,
        description=production.description,
        delivery_date=production.delivery_date,
        status=production.status
    )

    if session.query(Production).filter(Production.project_name == new_production_item.project_name, Production.client_name == new_production_item.client_name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This production item already exists, please provide different data to create a new production item")
        

    if not new_production_item.project_name or not new_production_item.client_name or not new_production_item.description:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Please, check the data provided, all fields are required to create a production item")

    session.add(new_production_item)
    session.commit()
    session.refresh(new_production_item)

    if not new_production_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create production item, check the data provided")

    return {
        "message": "Production item created successfully",
        "item": new_production_item
    }