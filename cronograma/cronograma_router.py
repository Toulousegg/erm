from fastapi import APIRouter, Depends, Response, status, Request, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import CreateSession, templates
from users.users_model import User
from core.security import verify_token
from cronograma.cronograma_schemas import *
from cronograma.cronograma_services import (create_schedule, 
                                            get_current_schedule, 
                                            update_schedule, 
                                            delete_schedule, 
                                            create_task, 
                                            update_task, 
                                            delete_task, 
                                            create_milestone, 
                                            toggle_milestone, 
                                            delete_milestone, 
                                            get_schedule_board, 
                                            get_schedule_categories, 
                                            create_schedule_category, 
                                            update_schedule_category, 
                                            delete_schedule_category,
                                            generate_share_link,
                                            get_shared_schedule)
from moduls.dependencies import require_module

cronograma_router = APIRouter(prefix="/schedule",tags=["Schedule"])

@cronograma_router.post("/", dependencies=[Depends(require_module("schedule"))])
def create_new_schedule(schedule_data: WeeklyScheduleCreate,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return create_schedule(
        session=session,
        schedule_data=schedule_data,
        company_id=user.company_id
    )
    
@cronograma_router.get("/current", dependencies=[Depends(require_module("schedule"))])
def get_active_schedule(start_date: date, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return get_current_schedule(session=session, company_id=user.company_id, start_date=start_date)
    
@cronograma_router.put("/", dependencies=[Depends(require_module("schedule"))])
def update_active_schedule(schedule_data: WeeklyScheduleUpdate,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return update_schedule(session=session, schedule_data=schedule_data, company_id=user.company_id, start_date=schedule_data.start)
    
@cronograma_router.delete("/{schedule_id}", dependencies=[Depends(require_module("schedule"))])
def remove_schedule(schedule_id: int,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    delete_schedule(session=session, schedule_id=schedule_id, company_id=user.company_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/tasks", dependencies=[Depends(require_module("schedule"))])
def create_new_task(task_data: ScheduleTaskCreate,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return create_task(session=session, task_data=task_data, company_id=user.company_id)
    
@cronograma_router.put("/tasks/{task_id}", dependencies=[Depends(require_module("schedule"))])
def update_existing_task(task_id: int,task_data: ScheduleTaskUpdate,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return update_task(session=session, task_id=task_id, task_data=task_data, company_id=user.company_id)
    
@cronograma_router.delete("/tasks/{task_id}", dependencies=[Depends(require_module("schedule"))])
def remove_task(task_id: int,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    delete_task(session=session, task_id=task_id, company_id=user.company_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/milestones", dependencies=[Depends(require_module("schedule"))])
def create_new_milestone(milestone_data: WeeklyMilestoneCreate,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return create_milestone(session=session, milestone_data=milestone_data, company_id=user.company_id)
    
@cronograma_router.patch("/milestones/{milestone_id}/toggle", dependencies=[Depends(require_module("schedule"))])
def toggle_existing_milestone(milestone_id: int,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    return toggle_milestone(session=session, milestone_id=milestone_id, company_id=user.company_id)
    
@cronograma_router.delete("/milestones/{milestone_id}", dependencies=[Depends(require_module("schedule"))])
def remove_milestone(milestone_id: int,session: Session = Depends(CreateSession),user: User = Depends(verify_token)):
    delete_milestone(session=session, milestone_id=milestone_id, company_id=user.company_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/categories", dependencies=[Depends(require_module("schedule"))])
def create_category(category_data: ScheduleCategoryCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return create_schedule_category(session, category_data=category_data, company_id=user.company_id)


@cronograma_router.put("/categories/{category_id}", dependencies=[Depends(require_module("schedule"))])
def update_category(category_id: int, category_data: ScheduleCategoryUpdate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return update_schedule_category(session, category_id=category_id, category_data=category_data, company_id=user.company_id)


@cronograma_router.delete("/categories/{category_id}", dependencies=[Depends(require_module("schedule"))])
def delete_category(category_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    delete_schedule_category(session, category_id=category_id, company_id=user.company_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@cronograma_router.post("/share/{schedule_id}", dependencies=[Depends(require_module("schedule"))])
def share_schedule(schedule_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    share_link = generate_share_link(session, schedule_id=schedule_id, company_id=user.company_id)
    
    if not share_link:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    return {
        "share_link": share_link["link"],
        "id": schedule_id
    }





#VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS #VIEWS



@cronograma_router.get("/", dependencies=[Depends(require_module("schedule"))])
def get_board(request: Request):

    return templates.TemplateResponse(
        "cronograma/cronograma.html", 
        {
            "request": request
            })
    
@cronograma_router.get("/board", dependencies=[Depends(require_module("schedule"))])
def get_board_data(start: date, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return {"board": get_schedule_board(session=session, company_id=user.company_id, start_date=start)}

@cronograma_router.get("/categories", dependencies=[Depends(require_module("schedule"))])
def get_categories(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):

    return get_schedule_categories(session, company_id=user.company_id)

@cronograma_router.get("/public/schedule", dependencies=[Depends(require_module("schedule"))])
def shared_schedule_view(request: Request, token: str, session: Session = Depends(CreateSession)):
    shared_schedule = get_shared_schedule(session, token)
    
    if not shared_schedule:
        raise HTTPException(status_code=404, detail="Shared schedule not found")
    
    return templates.TemplateResponse(
        "cronograma/shared_schedule.html",
        {
        "request": request,
        "schedule": shared_schedule
        }
    )