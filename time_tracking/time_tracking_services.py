from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from zoneinfo import ZoneInfo
from users.users_model import User
from projects.projects_model import Projects
from time_tracking.time_tracking_model import TimeEntry


MANAGER_ROLES = {"admin", "owner", "Administrador"}


def is_time_tracking_manager(user: User):
    return user.role in MANAGER_ROLES


def format_minutes(total_minutes: int):
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return f"{hours}h {minutes:02d}m"


def calculate_total_minutes(work_date, start_time, end_time):
    start_dt = datetime.combine(work_date, start_time)
    end_dt = datetime.combine(work_date, end_time)
    total_minutes = int((end_dt - start_dt).total_seconds() // 60)

    if total_minutes <= 0:
        raise HTTPException(status_code=400, detail="End time must be greater than start time")

    if total_minutes > 1440:
        raise HTTPException(status_code=400, detail="Time entry cannot be greater than 24 hours")

    return total_minutes


def get_project_or_404(user: User, session: Session, project_id: int):
    project = session.get(Projects, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.company_id != user.company_id:
        raise HTTPException(status_code=403, detail="You don't have permission to access this project")

    return project


def get_time_entry_or_404(user: User, session: Session, entry_id: int):
    entry = (
        session.query(TimeEntry)
        .options(joinedload(TimeEntry.employee), joinedload(TimeEntry.project))
        .filter(TimeEntry.id == entry_id, TimeEntry.company_id == user.company_id)
        .first()
    )

    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    return entry


def ensure_can_change_time_entry(user: User, entry: TimeEntry):
    if is_time_tracking_manager(user):
        return

    if entry.employee_id != user.id:
        raise HTTPException(status_code=403, detail="You can only change your own time entries")


def create_time_entry(user: User, session: Session, data):
    project = get_project_or_404(user, session, data.project_id)
    work_date = data.work_date or date.today()
    total_minutes = calculate_total_minutes(work_date, data.start_time, data.end_time)

    entry = TimeEntry(
        employee_id=user.id,
        company_id=user.company_id,
        project_id=project.id,
        stage=data.stage,
        task=data.task,
        description=data.description,
        work_date=work_date,
        start_time=data.start_time,
        end_time=data.end_time,
        total_minutes=total_minutes
    )

    try:
        session.add(entry)
        session.commit()
        session.refresh(entry)
        return entry

    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error creating time entry")


def update_time_entry(user: User, session: Session, entry_id: int, data):
    entry = get_time_entry_or_404(user, session, entry_id)
    ensure_can_change_time_entry(user, entry)

    payload = data.model_dump(exclude_unset=True)

    if "project_id" in payload:
        project = get_project_or_404(user, session, payload["project_id"])
        entry.project_id = project.id

    for field in ["stage", "task", "description", "work_date", "start_time", "end_time"]:
        if field in payload:
            setattr(entry, field, payload[field])

    entry.total_minutes = calculate_total_minutes(entry.work_date, entry.start_time, entry.end_time)
    entry.updated_at = datetime.now(ZoneInfo("America/Sao_Paulo"))

    try:
        session.commit()
        session.refresh(entry)
        return entry

    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error updating time entry")


def delete_time_entry(user: User, session: Session, entry_id: int):
    entry = get_time_entry_or_404(user, session, entry_id)
    ensure_can_change_time_entry(user, entry)

    try:
        session.delete(entry)
        session.commit()
        return {"message": "Time entry deleted"}

    except Exception as e:
        session.rollback()
        print(e)
        raise HTTPException(status_code=500, detail="Error deleting time entry")


def show_time_entries(session: Session, user: User):
    query = (
        session.query(TimeEntry)
        .filter(TimeEntry.company_id == user.company_id)
        .options(joinedload(TimeEntry.employee), joinedload(TimeEntry.project))
        .order_by(TimeEntry.work_date.desc(), TimeEntry.start_time.desc())
    )

    if not is_time_tracking_manager(user):
        query = query.filter(TimeEntry.employee_id == user.id)

    return query


def time_entry_to_dict(entry: TimeEntry):
    return {
        "id": entry.id,
        "employee_id": entry.employee_id,
        "employee": entry.employee.fullname if entry.employee else None,
        "project_id": entry.project_id,
        "project": entry.project.name if entry.project else None,
        "stage": entry.stage.value if entry.stage else None,
        "task": entry.task,
        "description": entry.description,
        "work_date": entry.work_date.isoformat() if entry.work_date else None,
        "start_time": entry.start_time.strftime("%H:%M") if entry.start_time else None,
        "end_time": entry.end_time.strftime("%H:%M") if entry.end_time else None,
        "total_minutes": entry.total_minutes,
        "total_time": format_minutes(entry.total_minutes)
    }


def time_entries_to_dict(entries):
    return [time_entry_to_dict(entry) for entry in entries]


def apply_report_filters(query, user: User, start_date=None, end_date=None, project_id=None, employee_id=None, stage=None):
    query = query.filter(TimeEntry.company_id == user.company_id)

    if not is_time_tracking_manager(user):
        query = query.filter(TimeEntry.employee_id == user.id)
    elif employee_id:
        query = query.filter(TimeEntry.employee_id == employee_id)

    if start_date:
        query = query.filter(TimeEntry.work_date >= start_date)

    if end_date:
        query = query.filter(TimeEntry.work_date <= end_date)

    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)

    if stage:
        query = query.filter(TimeEntry.stage == stage)

    return query


def report_rows_to_minutes(rows, label_getter):
    return [
        {
            "label": label_getter(row),
            "total_minutes": int(row.total_minutes or 0),
            "total_time": format_minutes(int(row.total_minutes or 0))
        }
        for row in rows
    ]


def get_time_report(user: User, session: Session, start_date=None, end_date=None, project_id=None, employee_id=None, stage=None):
    filtered_entries = apply_report_filters(
        session.query(TimeEntry),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    )

    total_minutes = int(filtered_entries.with_entities(func.coalesce(func.sum(TimeEntry.total_minutes), 0)).scalar() or 0)

    by_project_query = apply_report_filters(
        session.query(Projects.name.label("name"), func.sum(TimeEntry.total_minutes).label("total_minutes"))
        .select_from(TimeEntry)
        .join(Projects, Projects.id == TimeEntry.project_id),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    ).group_by(Projects.id, Projects.name).all()

    by_stage_query = apply_report_filters(
        session.query(TimeEntry.stage.label("stage"), func.sum(TimeEntry.total_minutes).label("total_minutes")),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    ).group_by(TimeEntry.stage).all()

    by_employee_query = apply_report_filters(
        session.query(User.fullname.label("fullname"), func.sum(TimeEntry.total_minutes).label("total_minutes"))
        .select_from(TimeEntry)
        .join(User, User.id == TimeEntry.employee_id),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    ).group_by(User.id, User.fullname).all()

    by_date_query = apply_report_filters(
        session.query(TimeEntry.work_date.label("work_date"), func.sum(TimeEntry.total_minutes).label("total_minutes")),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    ).group_by(TimeEntry.work_date).order_by(TimeEntry.work_date).all()

    by_project_stage_query = apply_report_filters(
        session.query(
            Projects.name.label("project_name"),
            TimeEntry.stage.label("stage"),
            func.sum(TimeEntry.total_minutes).label("total_minutes")
        )
        .select_from(TimeEntry)
        .join(Projects, Projects.id == TimeEntry.project_id),
        user,
        start_date=start_date,
        end_date=end_date,
        project_id=project_id,
        employee_id=employee_id,
        stage=stage
    ).group_by(Projects.id, Projects.name, TimeEntry.stage).all()

    return {
        "total_minutes": total_minutes,
        "total_time": format_minutes(total_minutes),
        "hours_decimal": round(total_minutes / 60, 2),
        "by_project": report_rows_to_minutes(by_project_query, lambda row: row.name),
        "by_stage": report_rows_to_minutes(by_stage_query, lambda row: row.stage.value if row.stage else None),
        "by_employee": report_rows_to_minutes(by_employee_query, lambda row: row.fullname),
        "by_date": report_rows_to_minutes(by_date_query, lambda row: row.work_date.isoformat()),
        "by_project_stage": [
            {
                "project": row.project_name,
                "stage": row.stage.value if row.stage else None,
                "total_minutes": int(row.total_minutes or 0),
                "total_time": format_minutes(int(row.total_minutes or 0))
            }
            for row in by_project_stage_query
        ]
    }
