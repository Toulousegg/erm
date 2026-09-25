from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from core.config.config_loader import RAW_CONFIG
from core.dependencies import CreateSession, render_template, templates
from core.security import verify_token
from moduls.dependencies import require_module
from project_tracking.project_tracking_schema import (
    FurnitureNotesUpdate,
    TrackedFurnitureCreate,
    TrackingBoardCreate,
    TrackingDelayCreate,
    TrackingStageCreate,
    TrackingStageUpdate,
    TrackingStatusUpdate,
)
from project_tracking.project_tracking_service import (
    add_delay,
    add_furniture,
    add_stage_media,
    add_stage,
    advance_stage,
    create_board,
    delete_stage,
    get_board,
    get_public_board,
    list_boards,
    move_stage,
    regenerate_share_token,
    set_board_status,
    tracking_summary,
    update_furniture_notes,
    update_stage_content,
    update_stage_settings,
)
from projects.projects_services import show_projects
from utilities.storage.storage_service import StorageService
from users.users_model import User

tracking_router = APIRouter(prefix="/tracking", tags=["project-tracking"])
AUTH = [Depends(require_module("projects"))]
PUBLIC_STATUS = {"executando", "espera", "cancelada", "terminada"}
MEDIA_URL = RAW_CONFIG.storage.media_base_url.rstrip("/")


def get_tracking_storage():
    return StorageService(RAW_CONFIG)


def _media_url(path: str | None) -> str | None:
    return f"{MEDIA_URL}/{path}" if path else None


def _upload(file: UploadFile | None, storage):
    if not file or not file.filename:
        return None
    try:
        return storage.upload_file(file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
    except Exception as error:
        raise HTTPException(status_code=502, detail="Não foi possível enviar o arquivo") from error


def _board_json(board, project):
    summary = tracking_summary(board)
    return {
        "id": board.id,
        "project": {"id": project.id, "name": project.name, "client_name": project.client_name},
        "share_url": f"{RAW_CONFIG.url.base_url.rstrip('/')}/tracking/public/{board.share_token}",
        "promised_days": board.promised_days,
        "promised_delivery": board.promised_delivery,
        "adjusted_delivery": summary["adjusted_delivery"],
        "lost_days": summary["lost_days"],
        "status": board.status,
        "updated_at": board.updated_at,
        "progress": summary["progress"],
        "current_stage_id": summary["current_stage"].id if summary["current_stage"] else None,
        "stages": [{"id": stage.id, "name": stage.name, "duration_days": stage.duration_days,
                    "position": stage.position, "content_kind": stage.content_kind,
                    "content_text": stage.content_text, "media_url": _media_url(stage.media_path),
                    "media_assets": [{"id": asset.id, "kind": asset.media_kind, "url": _media_url(asset.media_path)} for asset in stage.media_assets],
                    "completed": stage.completed} for stage in board.stages],
        "delays": [{"id": delay.id, "lost_days": delay.lost_days, "reason": delay.reason,
                    "evidence_url": _media_url(delay.evidence_path), "created_at": delay.created_at}
                   for delay in board.delays],
        "furniture": [{"id": item.id, "name": item.name, "image_url": _media_url(item.image_path),
                       "notes": item.notes} for item in board.furniture],
    }


def _dashboard_context(session: Session, user: User):
    projects = show_projects(session, user).all()
    boards = list_boards(session, user.company_id)
    linked_ids = {board.project_id for board in boards}
    return {
        "projects": [project for project in projects if project.id not in linked_ids],
        "boards": boards,
        "summaries": {board.id: tracking_summary(board) for board in boards},
        "share_base": RAW_CONFIG.url.base_url.rstrip("/"),
    }


@tracking_router.get("/", dependencies=AUTH)
def tracking_dashboard(request: Request, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    return render_template("project_tracking/dashboard.html", request, session, user, _dashboard_context(session, user))


@tracking_router.post("/boards", dependencies=AUTH)
def create_tracking_board(
    project_id: int = Form(...), promised_days: int = Form(...), promised_delivery: date = Form(...),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    payload = TrackingBoardCreate(project_id=project_id, promised_days=promised_days, promised_delivery=promised_delivery)
    board = create_board(session, user.company_id, payload)
    return RedirectResponse(f"/tracking/{board.id}", status_code=303)


@tracking_router.get("/{board_id}", dependencies=AUTH)
def tracking_detail(request: Request, board_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = get_board(session, board_id, user.company_id)
    from projects.projects_services import get_project_for_company
    project = get_project_for_company(session, board.project_id, user.company_id)
    context = {"board": board, "project": project, "summary": tracking_summary(board), "share_url": f"{RAW_CONFIG.url.base_url.rstrip('/')}/tracking/public/{board.share_token}", "media_url": _media_url}
    return render_template("project_tracking/detail.html", request, session, user, context)


@tracking_router.post("/{board_id}/stages", dependencies=AUTH)
def create_tracking_stage(
    board_id: int, name: str = Form(...), duration_days: int = Form(1), content_kind: str = Form("texto"),
    content_text: str = Form(""), session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    payload = TrackingStageCreate(name=name, duration_days=duration_days, content_kind=content_kind, content_text=content_text)
    add_stage(session, board, payload)
    return RedirectResponse(f"/tracking/{board_id}#stages", status_code=303)


@tracking_router.post("/{board_id}/stages/{stage_id}/settings", dependencies=AUTH)
def save_stage_settings(
    board_id: int, stage_id: int, name: str = Form(...), duration_days: int = Form(...), content_kind: str = Form(...),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    payload = TrackingStageUpdate(name=name, duration_days=duration_days, content_kind=content_kind)
    update_stage_settings(session, board, stage_id, payload)
    return RedirectResponse(f"/tracking/{board_id}#stage-{stage_id}", status_code=303)


@tracking_router.post("/{board_id}/stages/{stage_id}/move", dependencies=AUTH)
def move_tracking_stage(
    board_id: int, stage_id: int, direction: str = Form(...),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    move_stage(session, board, stage_id, direction)
    return RedirectResponse(f"/tracking/{board_id}#stage-{stage_id}", status_code=303)


@tracking_router.post("/{board_id}/stages/{stage_id}/delete", dependencies=AUTH)
def remove_tracking_stage(board_id: int, stage_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = get_board(session, board_id, user.company_id)
    delete_stage(session, board, stage_id)
    return RedirectResponse(f"/tracking/{board_id}#stages", status_code=303)


@tracking_router.post("/{board_id}/stages/{stage_id}/content", dependencies=AUTH)
def save_stage_content(
    board_id: int, stage_id: int, content_text: str = Form(""), media: list[UploadFile] = File([]),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token), storage=Depends(get_tracking_storage),
):
    board = get_board(session, board_id, user.company_id)
    stage = next((item for item in board.stages if item.id == stage_id), None)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    uploads = []
    for file in media:
        if not file.filename:
            continue
        allowed = {
            "foto": (file.content_type or "").startswith("image/"),
            "video": (file.content_type or "").startswith("video/"),
            "pdf": file.content_type == "application/pdf",
        }
        if stage.content_kind == "texto" or not allowed.get(stage.content_kind, False):
            raise HTTPException(status_code=400, detail="El archivo no coincide con el tipo de contenido configurado para esta etapa")
        uploads.append((stage.content_kind, _upload(file, storage)))
    update_stage_content(session, board, stage_id, content_text, None)
    if uploads:
        add_stage_media(session, board, stage_id, uploads)
    return RedirectResponse(f"/tracking/{board_id}#stage-{stage_id}", status_code=303)


@tracking_router.post("/{board_id}/advance", dependencies=AUTH)
def advance_tracking_stage(board_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    advance_stage(session, get_board(session, board_id, user.company_id))
    return RedirectResponse(f"/tracking/{board_id}#stages", status_code=303)


@tracking_router.post("/{board_id}/status", dependencies=AUTH)
def change_tracking_status(board_id: int, status: str = Form(...), session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    if status not in PUBLIC_STATUS:
        raise HTTPException(status_code=422, detail="Estado inválido")
    set_board_status(session, get_board(session, board_id, user.company_id), status)
    return RedirectResponse(f"/tracking/{board_id}", status_code=303)


@tracking_router.post("/{board_id}/delays", dependencies=AUTH)
def create_tracking_delay(
    board_id: int, lost_days: int = Form(...), reason: str = Form(...), evidence: UploadFile | None = File(None),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token), storage=Depends(get_tracking_storage),
):
    board = get_board(session, board_id, user.company_id)
    payload = TrackingDelayCreate(lost_days=lost_days, reason=reason)
    add_delay(session, board, payload, _upload(evidence, storage))
    return RedirectResponse(f"/tracking/{board_id}#delays", status_code=303)


@tracking_router.post("/{board_id}/furniture", dependencies=AUTH)
def create_tracked_furniture(
    board_id: int, name: str = Form(...), image: UploadFile | None = File(None),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token), storage=Depends(get_tracking_storage),
):
    board = get_board(session, board_id, user.company_id)
    add_furniture(session, board, TrackedFurnitureCreate(name=name), _upload(image, storage))
    return RedirectResponse(f"/tracking/{board_id}#furniture", status_code=303)


@tracking_router.post("/{board_id}/furniture/{furniture_id}/notes", dependencies=AUTH)
def save_furniture_notes(
    board_id: int, furniture_id: int, notes: str = Form(""),
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    update_furniture_notes(session, board, furniture_id, FurnitureNotesUpdate(notes=notes))
    return RedirectResponse(f"/tracking/{board_id}#furniture-{furniture_id}", status_code=303)


@tracking_router.post("/{board_id}/share/renew", dependencies=AUTH)
def renew_tracking_link(board_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    regenerate_share_token(session, get_board(session, board_id, user.company_id))
    return RedirectResponse(f"/tracking/{board_id}#share", status_code=303)


# Stable JSON contract for a future React client. The Jinja pages call the same service layer.
@tracking_router.get("/api/boards", dependencies=AUTH)
def tracking_boards_api(session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    from projects.projects_services import get_project_for_company
    return [_board_json(board, get_project_for_company(session, board.project_id, user.company_id))
            for board in list_boards(session, user.company_id)]


@tracking_router.get("/api/boards/{board_id}", dependencies=AUTH)
def tracking_board_api(board_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    from projects.projects_services import get_project_for_company
    board = get_board(session, board_id, user.company_id)
    return _board_json(board, get_project_for_company(session, board.project_id, user.company_id))


@tracking_router.post("/api/boards", dependencies=AUTH)
def create_tracking_board_api(payload: TrackingBoardCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = create_board(session, user.company_id, payload)
    from projects.projects_services import get_project_for_company
    return _board_json(get_board(session, board.id, user.company_id), get_project_for_company(session, board.project_id, user.company_id))


@tracking_router.post("/api/boards/{board_id}/stages", dependencies=AUTH)
def create_tracking_stage_api(board_id: int, payload: TrackingStageCreate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = get_board(session, board_id, user.company_id)
    add_stage(session, board, payload)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.post("/api/boards/{board_id}/advance", dependencies=AUTH)
def advance_tracking_stage_api(board_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = get_board(session, board_id, user.company_id)
    advance_stage(session, board)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.patch("/api/boards/{board_id}/status", dependencies=AUTH)
def update_tracking_status_api(board_id: int, payload: TrackingStatusUpdate, session: Session = Depends(CreateSession), user: User = Depends(verify_token)):
    board = get_board(session, board_id, user.company_id)
    set_board_status(session, board, payload.status)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.put("/api/boards/{board_id}/stages/{stage_id}", dependencies=AUTH)
def update_tracking_stage_api(
    board_id: int, stage_id: int, payload: TrackingStageUpdate,
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    update_stage_settings(session, board, stage_id, payload)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.delete("/api/boards/{board_id}/stages/{stage_id}", dependencies=AUTH)
def delete_tracking_stage_api(
    board_id: int, stage_id: int, session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    delete_stage(session, board, stage_id)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.post("/api/boards/{board_id}/delays", dependencies=AUTH)
def create_tracking_delay_api(
    board_id: int, payload: TrackingDelayCreate,
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    add_delay(session, board, payload, None)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.post("/api/boards/{board_id}/furniture", dependencies=AUTH)
def create_tracked_furniture_api(
    board_id: int, payload: TrackedFurnitureCreate,
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    add_furniture(session, board, payload, None)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.put("/api/boards/{board_id}/furniture/{furniture_id}/notes", dependencies=AUTH)
def save_furniture_notes_api(
    board_id: int, furniture_id: int, payload: FurnitureNotesUpdate,
    session: Session = Depends(CreateSession), user: User = Depends(verify_token),
):
    board = get_board(session, board_id, user.company_id)
    update_furniture_notes(session, board, furniture_id, payload)
    return _board_json(get_board(session, board_id, user.company_id), board.project)


@tracking_router.get("/api/public/{token}")
def public_tracking_api(token: str, session: Session = Depends(CreateSession)):
    board, project = get_public_board(session, token)
    return _board_json(board, project)


@tracking_router.get("/public/{token}")
def public_tracking_page(request: Request, token: str, session: Session = Depends(CreateSession)):
    board, project = get_public_board(session, token)
    context = {"board": board, "project": project, "summary": tracking_summary(board), "media_url": _media_url}
    return templates.TemplateResponse("project_tracking/public.html", {"request": request, **context})
