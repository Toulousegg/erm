import requests
from uuid import uuid4

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


def create_customer(email: str) -> str:
    response = requests.post(
        f"{ABACATE_BASE_URL}/customers/create",
        headers=HEADERS,
        json={
            "email": email
        },
        timeout=15
    )

    data = safe_response(response)

    return data["id"]


def create_subscription_product(name: str, amount: int, module_ids: list[int], external_id: str) -> str:
    response = requests.post(
        f"{ABACATE_BASE_URL}/products/create",
        headers=HEADERS,
        json={
            "externalId": external_id,
            "name": name,
            "price": amount,
            "currency": "BRL",
            "description": f"Assinatura mensal dos módulos: {', '.join(map(str, module_ids))}",
            "cycle": "MONTHLY"
        },
        timeout=15
    )

    data = safe_response(response)

    return data["id"]


def create_subscription(email: str, module_ids: list[int], amount: int, external_id: str | None = None):
    customer_id = create_customer(email)
    local_external_id = external_id or str(uuid4())
    product_id = create_subscription_product(
        name=f"ProntoERP Mensal #{local_external_id}",
        amount=amount,
        module_ids=module_ids,
        external_id=f"prontoerp-monthly-{local_external_id}-{uuid4().hex[:8]}"
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
