from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from core.database import base
from datetime import datetime


class Inventory(base):
    __tablename__ = 'inventory'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True) 
    item_name = Column('item_name', String, unique=True, index=True, nullable=False)
    description = Column('description', String, nullable=False, )
    quantity = Column('quantity', Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, ondelete="CASCADE")