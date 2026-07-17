import requests
from uuid import uuid4
from moduls.moduls_models import Moduls

from core.config import ABACATE_BASE_URL, ABACATE_PAY_KEY, BASE_URL


HEADERS = {
    "Authorization": f"Bearer {ABACATE_PAY_KEY}",
    "Content-Type": "application/json"
}


def safe_response(response):
    try:
        body = response.json()
    except Exception:
        raise ValueError("Respuesta inválida de AbacatePay")

    if not body.get("success", False):
        raise ValueError(body.get("error", "Error desconocido"))

    return body["data"]


def create_customer(email: str, name: str):
    response = requests.post(
        f"{ABACATE_BASE_URL}/customers/create",
        headers=HEADERS,
        json={
            "email": email,
            "name": name
        },
        timeout=15
    )

    data = safe_response(response)

    return data["id"]


def create_subscription_product(amount: int, module_ids: list[int], session) -> str:
    sorted_ids = sorted(module_ids)
    ids_string = "-".join(map(str, sorted_ids))
    composite_external_id = f"prod-modulos-{ids_string}-val-{amount}"
    moduls_names = session.query(Moduls.name).filter(Moduls.id.in_(module_ids)).all()
    
    print(f"DEBUG: Buscando/Creando producto con ID: {composite_external_id} y Precio: {amount}")

    list_response = requests.get(
        f"{ABACATE_BASE_URL}/products/list",
        headers=HEADERS,
        timeout=15
    )

    products_list = safe_response(list_response)

    if isinstance(products_list, list):
        for product in products_list:
            if product.get("externalId") == composite_external_id:
                print(f"reutilizando id: {product['id']}")
                return product["id"]

    create_response = requests.post(
        f"{ABACATE_BASE_URL}/products/create",
        headers=HEADERS,
        json={
            "externalId": composite_external_id,
            "name": f"Assinatura ERP - {len(module_ids)} - {moduls_names}",
            "price": amount,
            "currency": "BRL",
            "cycle": "MONTHLY"
        },
        timeout=15
    )
    
    new_data = safe_response(create_response)
    
    return new_data["id"]

def create_subscription(session, name: str, email: str, module_ids: list[int], amount: int, external_id: str | None = None):
    customer_id = create_customer(email, name)
    local_external_id = external_id or str(uuid4())
    
    product_id = create_subscription_product(
        amount=amount,
        module_ids=module_ids,
        session=session
    )

    payload = {
        "customerId": customer_id,
        "items": [
            {
                "id": product_id,
                "quantity": 1
            }
        ],
        "externalId": local_external_id,
        "methods": ["CARD"],
        "metadata": {
            "module_ids": module_ids
        },
        "retryPolicy": {
            "maxRetry": 3,
            "retryEvery": 2
        }
    }

    if BASE_URL:
        payload["returnUrl"] = f"{BASE_URL}/payments/modules"
        payload["completionUrl"] = f"{BASE_URL}/payments/success"

    response = requests.post(
        f"{ABACATE_BASE_URL}/subscriptions/create",
        headers=HEADERS,
        json=payload,
        timeout=15
    )

    return safe_response(response)



def get_subscription(subscription_id: str):
    response = requests.get(
        f"{ABACATE_BASE_URL}/subscriptions/one?id={subscription_id}",
        headers=HEADERS,
        timeout=15
    )

    if response.status_code != 200:
        return None

    return safe_response(response)


def cancel_subscription(subscription_id: str):
    response = requests.post(
        f"{ABACATE_BASE_URL}/subscriptions/cancel",
        headers=HEADERS,
        json={
            "id": subscription_id
        },
        timeout=15
    )

    return safe_response(response)


def get_checkout(checkout_id: str):
    response = requests.get(
        f"{ABACATE_BASE_URL}/checkouts/one?id={checkout_id}",
        headers=HEADERS,
        timeout=15
    )

    if response.status_code != 200:
        return None

    return safe_response(response)
