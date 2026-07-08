from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse
from math import ceil
from production.production_model import Production
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates 
from core.security import verify_token 
from production.production_schema import create_production
from users.users_model import User
from utilities.limiter.limiter import limiter
from moduls.dependencies import require_module


production_router = APIRouter(prefix="/production", tags=["production"])

@production_router.post("/add", dependencies=[Depends(require_module("production"))])
@limiter.limit("5/minute")
def create_project_in_production(request: Request, production: create_production, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    
    new_production_item = Production(
        project_name=production.project_name,
        client_name=production.client_name,
        description=production.description,
        delivery_date=production.delivery_date,
        status=production.status,
        company_id = user.company_id
    )

    if session.query(Production).filter(Production.project_name == new_production_item.project_name, Production.client_name == new_production_item.client_name, Production.company_id == user.company_id).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This production item already exists, please provide different data to create a new production item")
        
    session.add(new_production_item)
    session.commit()
    session.refresh(new_production_item)

    return {
        "message": "Production item created successfully",
        "item": new_production_item
    }

@production_router.put("/edit/{production_id}", dependencies=[Depends(require_module("production"))])
@limiter.limit("5/minute")
def edit_project_in_production(request: Request, production_id: int, production: create_production, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    production_item = session.query(Production).filter(
        Production.id == production_id,
        Production.company_id == user.company_id
    ).first()

    if not production_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Production item not found")

    duplicated_item = session.query(Production).filter(
        Production.id != production_id,
        Production.project_name == production.project_name,
        Production.client_name == production.client_name,
        Production.company_id == user.company_id
    ).first()

    if duplicated_item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This production item already exists")

    production_item.project_name = production.project_name
    production_item.client_name = production.client_name
    production_item.description = production.description
    production_item.delivery_date = production.delivery_date
    production_item.status = production.status

    session.commit()
    session.refresh(production_item)

    return {
        "message": "Production item updated successfully",
        "item": production_item
    }

@production_router.post("/delete/{production_name}", dependencies=[Depends(require_module("production"))])
@limiter.limit("5/minute")
def delete_production_route(request: Request, project_name: str, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    project_to_delete = session.query(Production).filter(Production.project_name == project_name, Production.company_id == user.company_id).first()

    if not project_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    session.delete(project_to_delete)
    session.commit()

    return {
        "message": "Project deleted successfully",
        "Project": project_to_delete
    }


# VIEWS


@production_router.get("/", dependencies=[Depends(require_module("production"))])
def show_production_by_client(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token), page_projects: int = Query(1, ge=1)):
    PER_PAGE = 30
    
    base_query = session.query(Production).filter(Production.company_id == user.company_id)
    total_projects = base_query.count()
    total_projects_page = ceil(total_projects / PER_PAGE)
    offset_pages = (page_projects - 1) * PER_PAGE
    projects_per_page = (base_query.offset(offset_pages).limit(PER_PAGE).all())
    
    return templates.TemplateResponse(
        "production/production.html",
        {   
            "user": user,
            "request": request,
            "items": [{"client_name": project.client_name,
                        "id": project.id,
                        "project_name": project.project_name, 
                        "delivery_date": project.delivery_date,
                        "description": project.description,
                        "status": project.status               
                        } 
                        for project in projects_per_page
                        ],
            "page": page_projects,
            "total_pages": total_projects_page,
            "param": "page_projects"
        }
    )

@production_router.get("/delete/{production_id}", dependencies=[Depends(require_module("production"))])
@limiter.limit("5/minute")
def delete_project_get(request: Request, production_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    project = session.query(Production).filter(Production.id == production_id, Production.company_id == user.company_id).first()

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Project not found")

    session.delete(project)
    session.commit()

    # Redirigir a la vista principal
    return RedirectResponse(
        url="/production",
        status_code=status.HTTP_303_SEE_OTHER
    )
