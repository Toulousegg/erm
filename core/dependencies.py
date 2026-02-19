from core.database import SessionLocal
from fastapi.templating import Jinja2Templates

def CreateSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")