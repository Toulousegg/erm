#uvicorn core.main:app --reload para rodar o app
#uvicorn main:app --reload --log-level debug para debugar cuando el log del error no es tan claro
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from users.users_route import home_router 
from inventory.inventory_route import inventory_router
from production.production_route import production_router
from contacts.contacts_route import contacts_router
from notification.notification_route import notification_router
from notification.ws_route import ws_route
from financery.financery_route import financery_router
from projects.projects_route import projects_router
from payments.payments_router import payments_router
from admin.admin_router import admin_router
from cronograma.cronograma_router import cronograma_router
from time_tracking.time_tracking_route import time_tracking_router
from moduls.moduls_router import modules_router
from core.database import base, engine
from core.dependencies import templates
from core.exceptions import AuthenticationRequired


app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
    "home/index.html",
    {"request": request}
    )

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, error: StarletteHTTPException):

    if error.status_code == 404:  #usuario visito pagina inexistente, da 404 y redirect
        return templates.TemplateResponse(
            "responses/404.html",
            {"request": request},
            status_code=404
        )

    return JSONResponse(
        status_code=error.status_code,
        content={"detail": error.detail}
    )
    
@app.exception_handler(AuthenticationRequired)
async def authentication_required_handler(
    request: Request,
    error: AuthenticationRequired
):
    return RedirectResponse(
        url="/home/login",
        status_code=302
    )

app.include_router(home_router)
app.include_router(inventory_router)
app.include_router(production_router)
app.include_router(contacts_router)
app.include_router(notification_router)
app.include_router(ws_route)
app.include_router(financery_router)
app.include_router(projects_router)
app.include_router(payments_router)
app.include_router(admin_router)
app.include_router(cronograma_router)
app.include_router(time_tracking_router)
app.include_router(modules_router)