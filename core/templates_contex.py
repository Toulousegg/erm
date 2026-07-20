from moduls.moduls_services import get_company_modules


def get_template_context(request, user, session):
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

    return {
        "request": request,
        "user": user,
        "modules": modules
    }
