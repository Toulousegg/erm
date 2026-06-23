from payments.payments_models import Subscription
from moduls.moduls_models import Moduls, Moduls_Companies
from datetime import date

def add_module(session, company_id: int, module_id: int): #posiblemente pueda optimizarse, talvez guardando una lista en la db para hacer una sola query y verificar la lista

    exists = session.query(Moduls_Companies).filter(Moduls_Companies.company_id == company_id, Moduls_Companies.modul_id == module_id).first() 

    if exists:
        return exists

    save = Moduls_Companies(
        company_id = company_id, 
        modul_id = module_id
        )

    session.add(save)
    session.flush()

    return save


def remove_module(session, company_id: int, module_id: int):

    relation = session.query(Moduls_Companies).filter(Moduls_Companies.company_id == company_id,Moduls_Companies.modul_id == module_id).first()

    if not relation:
        return False

    session.delete(relation)
    session.flush()

    return True


def assign_modules(session, company_id: int, module_ids: list[int]):

    for module_id in module_ids:
        add_module(session, company_id, module_id)
        
    update_subscription_amount(session, company_id)
    
    session.commit()


def get_company_modules(session, company_id: int):
    
    return session.query(Moduls).join(Moduls_Companies, Moduls.id == Moduls_Companies.modul_id).filter(Moduls_Companies.company_id == company_id).all()


def has_module(session, company_id: int, slug: str):

    module = session.query(Moduls).join(Moduls_Companies,Moduls.id == Moduls_Companies.modul_id).filter(Moduls_Companies.company_id == company_id,Moduls.slug == slug).first()
    
    return module


def calculate_amount(session, company_id: int): #NOTA: posiblemente por problemas de punto flotante tenga problemas con decimales, voy a guardar numeros enteros

    modules = get_company_modules(session, company_id)

    return sum(
        module.price
        for module in modules
    )


def update_subscription_amount(session, company_id: int):

    subscription = session.query(Subscription).filter(Subscription.company_id == company_id).first()

    if not subscription:
        return None

    subscription.amount = calculate_amount(session, company_id)

    session.add(subscription)
    session.flush()

    return subscription


def add_module_to_company(session, company_id: int, module_id: int):

    add_module(session, company_id, module_id)

    subscription = update_subscription_amount(session, company_id)

    session.commit()
    session.refresh(subscription)
    
    #sync_abacatepay(subscription) para futuro, ahi ya actualizo el abacatepay aqui mismo, ahora no quiero pensar xd

    return subscription


def remove_module_from_company(session, company_id: int,module_id: int):

    remove_module(session, company_id, module_id)

    subscription = update_subscription_amount(session, company_id)
    
    session.commit()
    session.refresh(subscription)

    #sync_abacatepay(subscription) para futuro, ahi ya actualizo el abacatepay aqui mismo, ahora no quiero pensar xd

    return subscription

def check_subscription_status(session, company_id: int) -> bool:

    subscription = session.query(Subscription).filter(Subscription.company_id == company_id).first()

    if not subscription:
        return False

    if not subscription.is_active:
        return False
    
    if subscription.current_period_end:
        if subscription.current_period_end < date.today():
            return False

    return True

def create_module(name: str, slug: str, price: int, session):
    if not name:
        raise ValueError('Falta name')
    
    if not slug:
        raise ValueError('Falta slug')
    
    
    if price is None or price <= 0:
        raise ValueError('Falta price')
    
    modulo = session.query(Moduls).filter(Moduls.slug == slug).first()
    
    if modulo:
        raise ValueError('Modulo ya existente')
    
    new_modul = Moduls(
        name = name,
        slug = slug,
        price = price
    )
    
    session.add(new_modul)
    session.commit()
    session.refresh(new_modul)
    
    return new_modul