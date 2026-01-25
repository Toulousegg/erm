from sqlalchemy import Integer, String, ForeignKey, create_engine, Column
from sqlalchemy.orm import declarative_base
import os

db = create_engine(os.getenv('DATABASE_URL'))

base = declarative_base()

class inventory(base):
    __tablename__ = 'inventory'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True) 
    item_name = Column('item_name', String, unique=True, index=True, nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    price = Column('price', Integer, nullable=False)

    def __init__(self, item_name, quantity, price):
        self.item_name = item_name
        self.quantity = quantity
        self.price = price

base.metadata.create_all(bind=db)