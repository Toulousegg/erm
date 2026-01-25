from sqlalchemy import Integer, String, ForeignKey, create_engine, Column
import os
from core.database import engine as db
from core.database import base

class User(base):
    __tablename__ = 'users'

    id = Column('id', Integer, primary_key=True, index=True, autoincrement=True) 
    username = Column('username', String, unique=True, index=True, nullable=False)
    email = Column('email', String, unique=True, index=True, nullable=False)
    fullname = Column('fullname', String)
    password = Column('password', String, nullable=False)

    def __init__(self, username, email, password, fullname):
        self.username = username
        self.email = email
        self.password = password
        self.fullname = fullname 

base.metadata.create_all(bind=db)