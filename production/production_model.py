from sqlalchemy import Integer, String, ForeignKey, create_engine, Column
from sqlalchemy.orm import declarative_base
import os

db = create_engine(os.getenv('DATABASE_URL'))

base = declarative_base()

class Production(base):
    __tablename__ = 'production'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True)
    client_name = Column('client_name', String, unique=True, index=True, nullable=False)
    project_name = Column('project_name', String, nullable=False)
    price = Column('price', Integer, nullable=False)

    def __init__(self, client_name, project_name, price):
        self.client_name = client_name
        self.project_name = project_name
        self.price = price