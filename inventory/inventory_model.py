from sqlalchemy import Integer, String, Column, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime
from zoneinfo import ZoneInfo


class InventoryLog(base):
    __tablename__ = 'inventory_logs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inventory_id = Column(Integer, ForeignKey('inventory.id'), nullable=False, index=True)
    inventory = relationship('Inventory', back_populates='logs')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship('User', foreign_keys=[user_id], back_populates='inventory_logs')
    action = Column(String, nullable=False)
    quantity_changed = Column(Integer, nullable=True)
    details = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo('America/Sao_Paulo')), nullable=False)


class Inventory(base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    item_name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(ZoneInfo("America/Sao_Paulo")), nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="inventory_items")
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company = relationship("Company", back_populates="company_items")
    logs = relationship("InventoryLog", back_populates="inventory", cascade="all, delete-orphan")
