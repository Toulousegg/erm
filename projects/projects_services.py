from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
from core.config import URL_EXPIRATION_MINUTES, BASE_URL
from sqlalchemy.orm import Session, selectinload, joinedload
from users.users_model import User
from projects.projects_model import Projects, ProjectsPhotos, ProjectsPDFs, Comments, SharedProjects
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService
from datetime import date
import secrets

def map_user(user): #esta funcion es para transformar los datos de un objeto ORM a un dict y que toda la app lo entienda
    return {
    "id": user.id,
    "username": user.username,
    "fullname": user.fullname,
    "role": user.role
    }


def create_project(user: User, session: Session, name: str, carpenter_id: int, client_name: str, delivery: date, description: str, address: str):
    new_project = Projects(
        name=name,
        carpenter_id=carpenter_id,
        client_name=client_name,
        delivery=delivery,
        description=description,
        address=address,
        company_id=user.company_id
    )
    

    usuario = session.get(User, carpenter_id)
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Carpenter not found")
    
    if usuario.company_id != user.company_id:
        raise HTTPException(status_code=400, detail="Carpenter does not belong to the same company")
    
    role = usuario.role
    
    if role not in ["carpenter", "admin", "owner"]:
        raise HTTPException(status_code=400, detail="User is not a carpenter or admin")
    
    
    try:
        session.add(new_project)
        session.commit()
        session.refresh(new_project)
        
    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error creating project")
    
    return new_project


def add_photo(project_id: int, file, session: Session, storage: StorageService):
    
    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        path = storage.upload_file(file)
        
    except Exception:
        raise HTTPException(500, "Error uploading file")
    
    photo = ProjectsPhotos(
        project_id=project_id,
        photo_path=path
    )
    
    try:
        session.add(photo)
        session.commit()
        session.refresh(photo)
        
        return photo
        
    except Exception:
        session.rollback()
        
        try:
            storage.delete_file(path)
        
        except:
            pass 
        
        raise HTTPException(status_code=500, detail="Error saving photo to database")

def add_pdf(project_id: int, file, session: Session, storage: StorageService):

    project = session.get(Projects, project_id)
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        path = storage.upload_file(file)
    except Exception:
        raise HTTPException(500, "Error uploading file")
    
    pdf = ProjectsPDFs(
        project_id=project_id,
        pdf_path=path
    )   
    
    try:
        session.add(pdf)
        session.commit()
        session.refresh(pdf)
        
        return pdf
    
    except Exception as e:
        session.rollback()
        
        try:
            storage.delete_file(path)
        
        except:
            pass 
        
        raise HTTPException(status_code=500, detail="Error saving pdf to database")
    
def tranform_contents(projects):
    return [
        {
            "id": project.id,
            "name": project.name,
            "carpenter": map_user(project.carpenter),
            "client_name": project.client_name,
            "delivery": project.delivery,
            "status": project.status.value,
            "description": project.description,
            "address": project.address,
            "photos": [RAW_CONFIG.storage.media_base_url + "/" + photo.photo_path for photo in project.photos],
            "pdfs": [RAW_CONFIG.storage.media_base_url + "/" + pdf.pdf_path for pdf in project.pdfs] #aqui estoy creando un link agarrando la url de mi storage y juntandola con la ruta del archivo que quiero
        }
        for project in projects
    ]

def show_projects(session: Session, user: User):
    return session.query(Projects).filter(Projects.company_id == user.company_id).options(selectinload(Projects.photos), selectinload(Projects.pdfs), joinedload(Projects.carpenter))  


def get_project_for_company(session: Session, project_id: int, company_id: int):
    """Return a project after checking tenant ownership for other module services."""
    project = (
        session.query(Projects)
        .filter(Projects.id == project_id, Projects.company_id == company_id)
        .options(selectinload(Projects.photos), selectinload(Projects.pdfs), joinedload(Projects.carpenter), joinedload(Projects.company))
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


def generate_project_share_link(project_id: int, session: Session):
    link = session.query(SharedProjects).filter(SharedProjects.project_id == project_id).first()
            
    if link:
        
        if link.expired_at < datetime.now(timezone.utc):
            try:
                session.delete(link)
                
            except Exception as e:
                print("Error deleting expired link:", str(e))
                raise HTTPException(
                    status_code=500,
                    detail="Error deleting expired link"
                )
            
        return {
            "link": f'{BASE_URL}/projects/public/projects/client?token={link.token}',
            "token": link.token
        }
        
    project = session.get(Projects, project_id)
            
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        token = secrets.token_urlsafe(36) 
        
        session.add(SharedProjects(
                        project_id=project_id,
                        token=token,
                        company_id=project.company_id
                    ))
                                    
        session.commit()
        
        link = f'{BASE_URL}/projects/public/projects/client?token={token}' #generando link para compartir proyecto usando token para mas seguridad
        
        return {
            "link": link,
            "token": token
            }
    
    except Exception as e:
        print("Error generating share link:", str(e))
        
        raise HTTPException(
            status_code=500,
            detail="Error generating share link"
        )
        
def get_shared_project_by_token(token: str, session: Session):
    shared_project = session.query(SharedProjects).filter(SharedProjects.token == token).first()
    
    if not shared_project:
        raise HTTPException(status_code=404, detail="Shared project not found")
    
    if shared_project.expired_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Link has expired")
    
    project = (
        session.query(Projects).options(
            selectinload(Projects.photos),
            selectinload(Projects.pdfs),
            joinedload(Projects.carpenter)
        ).filter(Projects.id == shared_project.project_id).first())  
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return project

def delete_link(token: str, session: Session):
    shared_project = session.query(SharedProjects).filter(SharedProjects.token == token).first()
    
    if not shared_project:
        raise HTTPException(status_code=404, detail="Shared project not found")
    
    try:
        session.delete(shared_project)
        session.commit()
        
        return {"detail": "Link deleted successfully"}
    
    except Exception as e:
        print("Error deleting share link:", str(e))
        
        raise HTTPException(
            status_code=500,
            detail="Error deleting share link"
        )
        
def public_comment(text, author, session, project_token, session_token): 
    
    shared = session.query(SharedProjects).filter( SharedProjects.token == project_token ).first() 
    
    if not shared: 
        raise HTTPException( status_code=404, detail="Project not found" ) 
    
    if not author.strip(): 
        raise HTTPException( status_code=400, detail="Author is required" )
    
    if len(author) < 2: 
        raise HTTPException( status_code=400, detail="Author name too short" ) 
    
    if not text.strip(): 
        raise HTTPException( status_code=400, detail="Comment is required" ) 
    
    if len(text) > 255: 
        raise HTTPException( status_code=400, detail="Comment too long" ) 

    new_comment = Comments( 
                           text=text, 
                           author_name=author, 
                           session_token=session_token, 
                           project_id=shared.project_id
                           ) 
    
    session.add(new_comment) 
    session.commit() 
    session.refresh(new_comment) 
    
    return { 
            "author": new_comment.author_name, 
            "text": new_comment.text, 
            "created_at": str(new_comment.created_at) 
            }
