from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException, Query
from math import ceil
from projects.projects_model import Projects, Comments
from sqlalchemy import or_
from sqlalchemy import func
from typing import List
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from projects.projects_services import create_project, tranform_contents, add_photo, add_pdf, show_projects, generate_project_share_link, get_shared_project_by_token, public_comment
from utilities.storage.storage_service import StorageService
from projects.projects_schema import CommentPayload
from datetime import date
from core.config.config_loader import RAW_CONFIG
import secrets
from utilities.limiter.limiter import limiter
from time_tracking.time_tracking_model import TimeEntry
from time_tracking.time_tracking_services import format_minutes

projects_router = APIRouter(prefix="/projects", tags=["prj"])

@projects_router.post("/dashboard")
@limiter.limit("3/minute")
def show_projects_router(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    show_projects(session, user)
    return RedirectResponse(url="/projects/dashboard", status_code=303)
    

@projects_router.post("/add")
@limiter.limit("5/minute")
def create_new_project(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession), name: str = Form(...), carpenter_id: int = Form(...), client_name: str = Form(...), delivery: date = Form(...), description: str = Form(...), address: str = Form(...), photo: List[UploadFile] = File([]), pdf: List[UploadFile] = File([])):
    new_project = create_project(user, session, name, carpenter_id, client_name, delivery, description, address)
    
    storage = StorageService(RAW_CONFIG) #nota mental: aqui le estoy pasando toda la config porque el storage necesita saber el valor de variables de entorno
    
    for file in photo:
        add_photo(project_id=new_project.id, file=file, session=session, storage=storage)
    
    for file in pdf:
        add_pdf(project_id=new_project.id, file=file, session=session, storage=storage)
        
    return RedirectResponse(url=f"/projects/dashboard", status_code=303)

@projects_router.post("/create_link/{project_id}")
def create_link(project_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")
    
    link = generate_project_share_link(project_id, session)
    token = link["token"]
    
    return {
        "share_link": link, 
        "token": token
        }

@projects_router.post("/{project_token}/comments") 
def create_comment(request: Request, project_token: str, payload: CommentPayload, session: Session = Depends(CreateSession)): 

    session_token = request.cookies.get("comment_session")

    created_new_cookie = False


    if not session_token:
        session_token = secrets.token_urlsafe(12)
        created_new_cookie = True

    comment = public_comment(
        text=payload.text,
        author=payload.author,
        session=session,
        project_token=project_token,
        session_token=session_token
    )

    response = JSONResponse(content=comment)

    if created_new_cookie: 
        response.set_cookie(
            key="comment_session", 
            value=session_token, 
            httponly=True, 
            max_age=60*60*24*30  #30 dias, 60seg*60min*24hrs*30dias
            )
            
    return response
    
# VIEWS

@projects_router.get("/dashboard")
def show_projects_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession), page_projects: int = Query(1, ge=1)):
    
    PER_PAGE = 10
    
    base_query = show_projects(session, user)
    total_projects = base_query.count()
    total_items_page = ceil(total_projects / PER_PAGE)
    offset_pages = (page_projects - 1) * PER_PAGE
    projects_per_page = (base_query.offset(offset_pages).limit(PER_PAGE).all())
    
    transformed_projects = tranform_contents(base_query)
    
    return templates.TemplateResponse(
        "projects/projects_dashboard.html",
        {
            "request": request,
            "user": user,
            "items": transformed_projects,
            "page": page_projects,
            "total_pages": total_items_page,
            "param": "items_page"
        }
    )

@projects_router.get("/add")
def create_project_view(request: Request):
    return templates.TemplateResponse(
        "projects/projects_add.html",
        {
            "request": request,
        })
    
@projects_router.get("/users/search") #esta funcion es para el autocomplete del input de carpintero en el html
def search_users_route(username: str, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    users = session.query(User).filter((User.company_id == user.company_id), User.username.ilike(f"%{username}%") | (User.fullname.ilike(f"%{username}%"))).all()

    return [
        {"id": user.id, "name": user.username}
        for user in users
    ]
            
@projects_router.get("/public/projects/client")
def shared_projects_client_view(request: Request, token: str, session: Session = Depends(CreateSession)):
    shared_project = get_shared_project_by_token(token, session)
    
    if not shared_project:
        raise HTTPException(status_code=404, detail="Shared project not found")
    
    return templates.TemplateResponse(
        "projects/client_exp.html",
        {
            "request": request,
            "token": token,
            "project": {
                "name": shared_project.name,
                "client_name": shared_project.client_name,
                "delivery": shared_project.delivery,
                "description": shared_project.description,
                "address": shared_project.address,
                "carpenter": shared_project.carpenter.fullname,
                "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in shared_project.photos],
                "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in shared_project.pdfs],
                "company_name": shared_project.company.name,
                #"company_logo": RAW_CONFIG.storage.media_base_url + "/" + project.company.logo_path if project.company.logo_path else None,
                "created_at": shared_project.created_at,
                "comments": [
                    {
                        "author": comment.author_name,
                        "date": comment.created_at,
                        "text": comment.text
                    }
                    for comment in shared_project.comments]
            },
            }
        )
    
@projects_router.get("/{project_id}")
def show_projects_details(request: Request, project_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")

    total_minutes = (
        session.query(func.coalesce(func.sum(TimeEntry.total_minutes), 0))
        .filter(TimeEntry.project_id == project.id, TimeEntry.company_id == user.company_id)
        .scalar()
    )
    stage_rows = (
        session.query(TimeEntry.stage, func.sum(TimeEntry.total_minutes).label("total_minutes"))
        .filter(TimeEntry.project_id == project.id, TimeEntry.company_id == user.company_id)
        .group_by(TimeEntry.stage)
        .all()
    )
    
    return templates.TemplateResponse(
        "projects/projects_details.html",
        {
            "request": request,
            
            "project": {
                "id": project.id,        
                "user": user,
                "description": project.description,
                "name": project.name,
                "client_name": project.client_name,
                "delivery": project.delivery,
                "status": project.status.value,
                "address": project.address,
                "carpenter": project.carpenter.fullname,
                "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in project.photos],
                "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in project.pdfs],
                "company_name": project.company.name,
                #"company_logo": RAW_CONFIG.storage.media_base_url + "/" + project.company.logo_path if project.company.logo_path else None,
                "created_at": project.created_at,
                "time_summary": {
                    "total_minutes": int(total_minutes or 0),
                    "total_time": format_minutes(int(total_minutes or 0)),
                    "by_stage": [
                        {
                            "stage": row.stage.value if row.stage else None,
                            "total_minutes": int(row.total_minutes or 0),
                            "total_time": format_minutes(int(row.total_minutes or 0))
                        }
                        for row in stage_rows
                    ]
                },
                "comments": [
                    {
                        "author": comment.author_name,
                        "date": comment.created_at,
                        "text": comment.text
                    }
                    for comment in project.comments]
            }
        }
    )
