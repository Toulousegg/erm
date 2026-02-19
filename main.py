#uvicorn main:app --reload para rodar o app
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse 
from users.users_route import home_router 
from inventory.inventory_route import inventory_router
from production.production_route import production_router
from core.database import base, engine


app = FastAPI()

base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(home_router)
app.include_router(inventory_router)
app.include_router(production_router)