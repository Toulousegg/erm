import requests
from fastapi import HTTPException, UploadFile
from core.config import ABACATE_PAY_KEY, ABACATE_BASE_URL
from payments.payments_models import Plans
from moduls.moduls_models import Moduls
from uuid import uuid4
import os
import shutil

UPLOAD_FOLDER = "frontend/static/uploads"

HEADERS = {
    "Authorization": f"Bearer {ABACATE_PAY_KEY}",
    "Content-Type": "application/json"
}


def safe_response(response):
    try:
        data = response.json()
    except Exception:
        raise ValueError("Respuesta inválida de AbacatePay")

    if not data.get("success", False):
        raise ValueError(f"AbacatePay error: {data.get('error')}")

    return data["data"]

def create_plan(user, name: str, amount: float, frequency: int, session):
    if user.role != "admin":
        raise ValueError("Unauthorized")

    url = f"{ABACATE_BASE_URL}/products/create"

    cycle_map = {
        1: "MONTHLY",
        12: "ANNUALLY"
    }

    cycle = cycle_map.get(frequency, "MONTHLY")

    payload = {
        "externalId": f"plan_{name.lower()}_{uuid4().hex[:8]}",
        "name": name,
        "price": amount,
        "currency": "BRL",
        "cycle": cycle
    }

    response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
    
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)
    
    data = safe_response(response)
    
    plan = Plans(
        name=name,
        amount=amount,
        frequency=frequency,
        external_id=data["id"]
    )

    session.add(plan)
    session.commit()

    return {
        "plan_id": plan.id,
        "external_id": plan.external_id
    }

def delete_plan_abacatepay(product_id, api_key, user, session):
    if user.role != "admin":
        raise ValueError("Unauthorized")

    url = "https://api.abacatepay.com/v2/products/delete"
    
    plan = session.query(Plans).filter(Plans.external_id == product_id).first()

    if not plan:
        raise HTTPException(404, "Plan no encontrado")
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.post(
    url,
    params={"id": product_id},
    headers=headers
)

    print(response.status_code)
    print(response.text)
    
    session.delete(plan)
    session.commit()

    return safe_response(response)


def list_modules(session):
    return session.query(Moduls).order_by(Moduls.id).all()

def create_module(name: str, slug: str, price: int, description: str, frequency: int, image: UploadFile, session):
    if not name:
        raise ValueError("Falta name")

    if not slug:
        raise ValueError("Falta slug")

    if not description:
        raise ValueError("Falta description")

    if price is None or price <= 0:
        raise ValueError("Falta price")

    if image is None:
        raise ValueError("Falta image")

    modulo = session.query(Moduls).filter(Moduls.slug == slug).first()

    if modulo:
        raise ValueError("Modulo ya existente")
    
    url = f"{ABACATE_BASE_URL}/products/create"

    cycle_map = {
        1: "MONTHLY",
        12: "ANNUALLY"
    }

    cycle = cycle_map.get(frequency, "MONTHLY")

    payload = {
        "externalId": f"plan_{name.lower()}_{uuid4().hex[:8]}",
        "name": name,
        "price": price,
        "currency": "BRL",
        "cycle": cycle
    }

    response = requests.post(url, json=payload, headers=HEADERS, timeout=15)
    
    print("STATUS:", response.status_code)
    print("TEXT:", response.text)
    
    data = safe_response(response)

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    extension = os.path.splitext(image.filename)[1]

    filename = f"{uuid4()}{extension}"

    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    db_path = f"/static/uploads/{filename}"

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    new_modul = Moduls(
        name=name,
        slug=slug,
        description=description,
        price=price,
        icon_url=db_path,
        external_id=data["id"]
    )

    session.add(new_modul)
    session.commit()
    session.refresh(new_modul)

    return new_modul