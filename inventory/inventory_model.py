from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime
from users.users_model import User


class Inventory(base):
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    item_name = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="inventory_items")
    logs = relationship("InventoryLogs", back_populates="inventory")

class InventoryLogs(base):
    __tablename__ = 'inventory_logs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)
    quantity_changed = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    inventory = relationship("Inventory", back_populates="logs")
    user = relationship("User", back_populates="inventory_logs")