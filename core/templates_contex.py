from moduls.moduls_services import get_company_modules
from fastapi.templating import Jinja2Templates
import time


def get_template_context(request, user, session):

    start = time.time()
     
    modules = []

    if user and user.company_id:
        modules = [
            {
                "id": module.id,
                "name": module.name,
                "route": module.module_route,
                "icon": module.icon
            }
            for module in get_company_modules(
                session,
                user.company_id
            )
        ]

    print("Tiempo módulos:", time.time() - start)


    return {
        "request": request,
        "modules": modules
    }
