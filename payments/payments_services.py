from core.enum.enum import SubscriptionStatusEnum
from payments.payments_models import Subscription
from payments.provider import create_subscription
from moduls.moduls_models import Moduls
from moduls.moduls_services import assign_modules
from datetime import date, timedelta


def get_modules(session, module_ids: list[int]):
    modules = session.query(Moduls).filter(Moduls.id.in_(module_ids)).all()
    
    if len(modules) != len(module_ids):
        raise ValueError("Some modules not found.")
    
    return modules

def calculate_modules_amount(modules):

    return sum(
        module.price
        for module in modules
        )


def save_subscrition(session, user, company, module_ids, amount):
    existing_subscription = session.query(Subscription).filter(
        Subscription.company_id == company.id
    ).first()

    if existing_subscription: #este if es para actualizar la subs por si alguien quiere contratar otros modulos en el futuro
        existing_subscription.user_id = user.id
        existing_subscription.amount = amount
        existing_subscription.status = SubscriptionStatusEnum.PENDING
        existing_subscription.is_active = False
        existing_subscription.moduls = module_ids
        existing_subscription.frequency = "MONTHLY"
        session.flush()
        session.refresh(existing_subscription)
        return existing_subscription

    subscription = Subscription(
        company_id=company.id,
        user_id=user.id,
        amount=amount,
        status=SubscriptionStatusEnum.PENDING,
        is_active=False,
        frequency="MONTHLY",
        moduls=module_ids
    )

    session.add(subscription)
    session.flush()
    session.refresh(subscription)

    return subscription


def update_provider_subscription(session, subscription, provider_subscription):
    subscription.provider_subscription_id = provider_subscription["id"]

    session.commit()
    session.refresh(subscription)

    return subscription


def create_subscription_service(session, user, module_ids: list[int]):
    company = user.company

    if not company:
        raise ValueError("Company not found.")
    
    name = user.fullname or user.username

    modules = get_modules(session, module_ids)

    amount = calculate_modules_amount(modules)

    subscription = save_subscrition(session, user, company, module_ids, amount)

    provider_subscription = create_subscription(
        name=name,
        email=user.email,
        module_ids=module_ids,
        amount=amount,
        external_id=str(subscription.id),
        session=session
    )

    update_provider_subscription(session, subscription, provider_subscription)

    return {
        "checkout_url": provider_subscription["url"],
        "subscription": subscription
    }


def activate_subscription(session, subscription):
    subscription.status = SubscriptionStatusEnum.ACTIVE
    subscription.is_active = True
    subscription.current_period_start = date.today()
    subscription.current_period_end = date.today() + timedelta(days=30)

    if subscription.company_id and subscription.moduls:
        assign_modules(session, subscription.company_id, subscription.moduls)
        subscription.moduls = None

    session.commit()
    session.refresh(subscription)

    return subscription


def renew_subscription(session, subscription):
    subscription.status = SubscriptionStatusEnum.ACTIVE
    subscription.is_active = True
    subscription.current_period_start = date.today()
    subscription.current_period_end = date.today() + timedelta(days=30)

    session.commit()
    session.refresh(subscription)

    return subscription


def cancel_subscription(session, subscription):
    subscription.status = SubscriptionStatusEnum.CANCELED
    subscription.is_active = False

    session.commit()
    session.refresh(subscription)

    return subscription
