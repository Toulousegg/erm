#uvicorn main:app --reload para rodar o app
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse 
from users.users_route import home_router 
from inventory.inventory_route import inventory_router
from core.database import base, engine


app = FastAPI()

base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/")
def home(request: Request, ruta: str=""):
    if ruta:
        return RedirectResponse(f"/{ruta}", status_code=303)

    return templates.TemplateResponse(
        "base.html",
        {"request": request, "name": ""}
    )

@app.post("/")
def home_post(
    request: Request,
    nombre: str = Form(...)
):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "name": nombre}
    )

app.include_router(home_router)
app.include_router(inventory_router)