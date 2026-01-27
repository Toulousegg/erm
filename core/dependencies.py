from core.database import SessionLocal

def CreateSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()