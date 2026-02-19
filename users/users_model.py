from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.orm import relationship
from core.database import base
from datetime import datetime

class User(base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    fullname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    inventory_items = relationship("Inventory", back_populates="owner")
    inventory_logs = relationship("InventoryLogs", back_populates="user")

class Contacts(base):
    __tablename__ = 'contacts'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True) 
    name = Column('name', String, nullable=False)
    email = Column('email', String, nullable=False)
    phone = Column('phone', String, nullable=False)
    contact_type = Column('contact_type', String, nullable=False) # e.g., 'personal', 'business'
    address = Column('address', String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)