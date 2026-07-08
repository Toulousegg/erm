from fastapi import APIRouter, Depends, Request, HTTPException, Query
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from math import ceil
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from core.security import verify_token
from users.users_model import User
from projects.projects_model import Projects
from core.enum.enum import ProjectStageEnum
from utilities.limiter.limiter import limiter
from time_tracking.time_tracking_schema import TimeEntryCreate, TimeEntryUpdate
from time_tracking.time_tracking_model import TimeEntry
from time_tracking.time_tracking_services import (
    create_time_entry,
    update_time_entry,
    delete_time_entry,
    show_time_entries,
    time_entry_to_dict,
    time_entries_to_dict,
    get_time_report,
    is_time_tracking_manager
)
from datetime import date


time_tracking_router = APIRouter(prefix="/time-tracking", tags=["time_tracking"])


def get_selected_project_name(user: User, session: Session, project_id: int | None):
    if not project_id:
        return ""

    project = session.query(Projects).filter(Projects.id == project_id, Projects.company_id == user.company_id).first()
    return project.name if project else ""


def get_selected_employee_name(user: User, session: Session, employee_id: int | None):
    if not employee_id:
        return ""

    if not is_time_tracking_manager(user) and employee_id != user.id:
        return ""

    employee = session.query(User).filter(User.id == employee_id, User.company_id == user.company_id).first()
    return employee.fullname if employee else ""


async def parse_time_entry_create(request: Request):
    content_type = request.headers.get("content-type", "")

    try:
        if "application/json" in content_type:
            payload = await request.json()
            return TimeEntryCreate(**payload), False

        form = await request.form()
        payload = dict(form)
        payload["project_id"] = int(payload.get("project_id"))
        return TimeEntryCreate(**payload), True

    except (ValidationError, ValueError, TypeError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@time_tracking_router.post("/add")
@limiter.limit("5/minute")
async def create_time_entry_endpoint(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    data, is_form = await parse_time_entry_create(request)
    entry = create_time_entry(user, session, data)

    if is_form:
        return RedirectResponse(url="/time-tracking/dashboard", status_code=303)

    return time_entry_to_dict(entry)


@time_tracking_router.get("/projects/search")
def search_projects_route(project: str = "", user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    projects = (
        session.query(Projects)
        .filter(Projects.company_id == user.company_id, Projects.name.ilike(f"%{project}%"))
        .limit(10)
        .all()
    )

    return [
        {"id": project.id, "name": project.name, "client_name": project.client_name}
        for project in projects
    ]


@time_tracking_router.get("/users/search")
def search_users_route(username: str = "", user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    if not is_time_tracking_manager(user):
        return [{"id": user.id, "name": user.username, "fullname": user.fullname}]

    users = (
        session.query(User)
        .filter((User.company_id == user.company_id), User.username.ilike(f"%{username}%") | (User.fullname.ilike(f"%{username}%")))
        .limit(10)
        .all()
    )

    return [
        {"id": user.id, "name": user.username, "fullname": user.fullname}
        for user in users
    ]


@time_tracking_router.get("/report/data")
def time_report_data(
    user: User = Depends(verify_token),
    session: Session = Depends(CreateSession),
    start_date: date | None = None,
    end_date: date | None = None,
    project_id: int | None = None,
    employee_id: int | None = None,
    stage: ProjectStageEnum | None = None
):
    return get_time_report(
        user,
        session,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    )


@time_tracking_router.put("/{entry_id}")
@limiter.limit("8/minute")
def update_time_entry_endpoint(request: Request, entry_id: int, data: TimeEntryUpdate, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    entry = update_time_entry(user, session, entry_id, data)
    return time_entry_to_dict(entry)


@time_tracking_router.delete("/{entry_id}")
@limiter.limit("8/minute")
def delete_time_entry_endpoint(request: Request, entry_id: int, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    return delete_time_entry(user, session, entry_id)


# VIEWS

@time_tracking_router.get("/dashboard")
def time_tracking_dashboard(
    request: Request,
    user: User = Depends(verify_token),
    session: Session = Depends(CreateSession),
    page_entries: int = Query(1, ge=1),
    start_date: date | None = None,
    end_date: date | None = None,
    project_id: int | None = None,
    employee_id: int | None = None,
    stage: ProjectStageEnum | None = None
):
    PER_PAGE = 10
    base_query = show_time_entries(session, user)

    if start_date:
        base_query = base_query.filter(TimeEntry.work_date >= start_date)

    if end_date:
        base_query = base_query.filter(TimeEntry.work_date <= end_date)

    if project_id:
        base_query = base_query.filter(TimeEntry.project_id == project_id)

    if employee_id and is_time_tracking_manager(user):
        base_query = base_query.filter(TimeEntry.employee_id == employee_id)

    if stage:
        base_query = base_query.filter(TimeEntry.stage == stage)

    total_entries = base_query.count()
    total_pages = ceil(total_entries / PER_PAGE) if total_entries else 1
    offset_entries = (page_entries - 1) * PER_PAGE
    entries = base_query.offset(offset_entries).limit(PER_PAGE).all()

    report = get_time_report(
        user,
        session,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    )

    return templates.TemplateResponse("time_tracking/dashboard.html", {
        "request": request,
        "user": user,
        "entries": entries,
        "entry_items": time_entries_to_dict(entries),
        "report": report,
        "stages": list(ProjectStageEnum),
        "selected_project_name": get_selected_project_name(user, session, project_id),
        "selected_employee_name": get_selected_employee_name(user, session, employee_id),
        "page": page_entries,
        "total_pages": total_pages,
        "param": "page_entries"
    })


@time_tracking_router.get("/add")
def create_time_entry_view(request: Request, user: User = Depends(verify_token), session: Session = Depends(CreateSession)):
    projects = session.query(Projects).filter(Projects.company_id == user.company_id).order_by(Projects.name).all()

    return templates.TemplateResponse("time_tracking/add.html", {
        "request": request,
        "user": user,
        "projects": projects,
        "stages": list(ProjectStageEnum)
    })


@time_tracking_router.get("/reports")
def time_tracking_reports(
    request: Request,
    user: User = Depends(verify_token),
    session: Session = Depends(CreateSession),
    start_date: date | None = None,
    end_date: date | None = None,
    project_id: int | None = None,
    employee_id: int | None = None,
    stage: ProjectStageEnum | None = None
):
    report = get_time_report(
        user,
        session,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    )
    projects = session.query(Projects).filter(Projects.company_id == user.company_id).order_by(Projects.name).all()
    users = []

    if is_time_tracking_manager(user):
        users = session.query(User).filter(User.company_id == user.company_id).order_by(User.fullname).all()

    return templates.TemplateResponse("time_tracking/reports.html", {
        "request": request,
        "user": user,
        "report": report,
        "projects": projects,
        "users": users,
        "stages": list(ProjectStageEnum),
        "selected_project_name": get_selected_project_name(user, session, project_id),
        "selected_employee_name": get_selected_employee_name(user, session, employee_id)
    })
