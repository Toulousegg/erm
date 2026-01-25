import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import DATABASE_URL
from sqlalchemy.orm import declarative_base

base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)