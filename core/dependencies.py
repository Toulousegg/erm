from core.database import SessionLocal
from fastapi.templating import Jinja2Templates
from core.config.config_loader import RAW_CONFIG
from utilities.storage.storage_service import StorageService
from core.templates_contex import get_template_context

def CreateSession():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="frontend/templates")

def render_template(template_name, request, session, user, context=None):

    data = get_template_context(request, user, session)

    if context:
        data.update(context)

    return templates.TemplateResponse(
        template_name,
        data
    )

def get_storage_service():
    return StorageService(RAW_CONFIG.storage)