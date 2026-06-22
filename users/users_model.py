from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime
from core.enum.enum import UserRoleEnum
from zoneinfo import ZoneInfo

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    temp_password = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    is_verified = Column(Integer, default=0, nullable=False)
    verification_code = Column(String, nullable=True)
    verification_code_expires_at = Column(DateTime(timezone=True), nullable=True)
    inventory_items = relationship("Inventory", back_populates="owner")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    company = relationship("Company", foreign_keys=[company_id])
    role = Column(String, default=UserRoleEnum.auxiliary.value, nullable=False) #admin, carpenter, auxiliary, owner
    sells = relationship("Sells", foreign_keys="Sells.user_id", back_populates="user") # quien hizo la venta, relacion entre sells y users
    in_charge = relationship("Sells", foreign_keys="Sells.carpenter_id", back_populates="carpenter")
    to_recebe = relationship("Receivable", foreign_keys="Receivable.receiver_id", back_populates="receiver")
    carpenter_projects = relationship("Projects",back_populates="carpenter")
    user_comments = relationship("Comments", back_populates="author")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    time_entries = relationship("TimeEntry", back_populates="employee")

class Company(base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True, nullable=False)
    legal_name = Column(String, index=True, nullable=False)
    tax_id = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    plan = Column(String, default='free', nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", foreign_keys=[owner_id])
    company_items = relationship("Inventory", back_populates="company")
    contacts = relationship("Contacts", back_populates="company")
    productions = relationship("Production", back_populates="company")
    company_messages = relationship("Notification", back_populates="company")
    company_sells = relationship("Sells", back_populates="company")
    company_debts = relationship("Debt", back_populates="company")
    company_payments = relationship("Payment", back_populates="company")
    company_receivable = relationship("Receivable", back_populates="company")
    company_financial_transactions = relationship("FinancialTransaction", back_populates="company")
    company_projects = relationship("Projects", back_populates="company")
    company_subscription = relationship("Subscription", back_populates="company", uselist=False)
    company_schedules = relationship("WeeklySchedule", back_populates="company")
    company_time_entries = relationship("TimeEntry", back_populates="company")
    
class CompanyJoinRequest(base):
    __tablename__ = 'company_join_requests'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    user = relationship("User", foreign_keys=[user_id])
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    company = relationship("Company", foreign_keys=[company_id])
    status = Column(String, default="pending", index=True, nullable=False)#pending, rejected, accepted
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    message = Column(JSONB, index=True, nullable=True)
