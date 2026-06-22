from sqlalchemy import Integer, String, Column, ForeignKey, Boolean, DateTime, Date, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.config import URL_EXPIRATION_MINUTES
from core.database import base
from datetime import date, datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from core.enum.enum import StatusEnum

class Projects(base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    carpenter_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    carpenter = relationship("User", back_populates="carpenter_projects")
    client_name =  Column(String, nullable=True, index=True)
    delivery = Column(Date, default=date.today, nullable=False, index=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.planning, nullable=False, index=True)
    photo_path = Column(String, index=True, nullable=True)
    pdf_path = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    description = Column(String, nullable=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_projects")
    active = Column(Boolean, default=False, nullable=False, index=True) #esto es para decir si el proyecto ya se esta ejecutando en la fabrica o no
    address = Column(String, nullable=True, index=True) #direccion del cliente
    photos = relationship("ProjectsPhotos", back_populates="project", cascade="all, delete-orphan")
    pdfs = relationship("ProjectsPDFs", back_populates="project", cascade="all, delete-orphan")
    comments = relationship("Comments", back_populates="project", cascade="all, delete-orphan")
    time_entries = relationship("TimeEntry", back_populates="project", cascade="all, delete-orphan")
    
class ProjectsPhotos(base):
    __tablename__ = 'projects_photos'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    photo_path = Column(String, index=True, nullable=False)
    project = relationship("Projects", back_populates="photos")
    
class ProjectsPDFs(base):
    __tablename__ = 'projects_pdfs'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    pdf_path = Column(String, index=True, nullable=False)
    project = relationship("Projects", back_populates="pdfs")
    
class Comments(base):
    __tablename__ = 'comments'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    author_name = Column(String, nullable=False, index=True)
    session_token = Column(String, nullable=True, index=True)
    text = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    project = relationship("Projects", back_populates="comments")
    author = relationship("User", back_populates="user_comments")
    
class SharedProjects(base):
    __tablename__ = 'shared_projects'
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True)
    token = Column(String, nullable=False, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    expired_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc) + timedelta(minutes=URL_EXPIRATION_MINUTES), nullable=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
