from sqlalchemy import Integer, String, Column, ForeignKey, DateTime, Date, Time, Enum as SQLEnum
from sqlalchemy.orm import relationship
from core.database import base
from core.enum.enum import ProjectStageEnum
from datetime import date, datetime
from zoneinfo import ZoneInfo


class TimeEntry(base):
    __tablename__ = "time_entries"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    employee = relationship("User", back_populates="time_entries")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    company = relationship("Company", back_populates="company_time_entries")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    project = relationship("Projects", back_populates="time_entries")
    stage = Column(SQLEnum(ProjectStageEnum), nullable=False, index=True)
    task = Column(String, nullable=True, index=True)
    description = Column(String, nullable=True)
    work_date = Column(Date, default=date.today, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    total_minutes = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
