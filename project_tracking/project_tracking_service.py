import secrets
from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from project_tracking.project_tracking_model import (
    TrackedFurniture,
    TrackingBoard,
    TrackingDelay,
    TrackingStage,
    TrackingStageMedia,
    now_local,
)
from project_tracking.project_tracking_schema import (
    FurnitureNotesUpdate,
    TrackedFurnitureCreate,
    TrackingBoardCreate,
    TrackingDelayCreate,
    TrackingStageCreate,
    TrackingStageUpdate,
)
from projects.projects_services import get_project_for_company


def list_boards(session: Session, company_id: int):
    return (
        session.query(TrackingBoard)
        .filter(TrackingBoard.company_id == company_id)
        .options(selectinload(TrackingBoard.stages), selectinload(TrackingBoard.delays))
        .order_by(TrackingBoard.updated_at.desc())
        .all()
    )


def get_board(session: Session, board_id: int, company_id: int) -> TrackingBoard:
    board = (
        session.query(TrackingBoard)
        .filter(TrackingBoard.id == board_id, TrackingBoard.company_id == company_id)
        .options(selectinload(TrackingBoard.stages), selectinload(TrackingBoard.delays), selectinload(TrackingBoard.furniture))
        .first()
    )
    if not board:
        raise HTTPException(status_code=404, detail="Acompanhamento não encontrado")
    return board


def create_board(session: Session, company_id: int, payload: TrackingBoardCreate) -> TrackingBoard:
    get_project_for_company(session, payload.project_id, company_id)
    existing = session.query(TrackingBoard).filter(TrackingBoard.project_id == payload.project_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Este projeto já tem um acompanhamento")
    board = TrackingBoard(
        project_id=payload.project_id,
        company_id=company_id,
        share_token=secrets.token_urlsafe(36),
        promised_days=payload.promised_days,
        promised_delivery=payload.promised_delivery,
    )
    session.add(board)
    session.commit()
    session.refresh(board)
    return board


def add_stage(session: Session, board: TrackingBoard, payload: TrackingStageCreate) -> TrackingStage:
    if board.status == "terminada":
        raise HTTPException(status_code=400, detail="No se pueden añadir etapas a un proyecto terminado")
    stage = TrackingStage(
        board_id=board.id,
        name=payload.name,
        duration_days=payload.duration_days,
        content_kind=payload.content_kind,
        content_text=payload.content_text,
        position=max((item.position for item in board.stages), default=0) + 1,
    )
    if not board.stages:
        stage.started_at = now_local()
    session.add(stage)
    board.updated_at = now_local()
    session.commit()
    session.refresh(stage)
    return stage


def update_stage_content(session: Session, board: TrackingBoard, stage_id: int, text: str | None, media_path: str | None):
    stage = next((item for item in board.stages if item.id == stage_id), None)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    stage.content_text = (text or "").strip() or None
    if media_path:
        stage.media_path = media_path
    board.updated_at = now_local()
    session.commit()
    session.refresh(stage)
    return stage


def add_stage_media(session: Session, board: TrackingBoard, stage_id: int, uploads: list[tuple[str, str]]):
    stage = next((item for item in board.stages if item.id == stage_id), None)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    for media_kind, media_path in uploads:
        session.add(TrackingStageMedia(stage_id=stage.id, media_kind=media_kind, media_path=media_path))
    board.updated_at = now_local()
    session.commit()
    session.refresh(stage)
    return stage


def update_stage_settings(session: Session, board: TrackingBoard, stage_id: int, payload: TrackingStageUpdate):
    stage = next((item for item in board.stages if item.id == stage_id), None)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    stage.name = payload.name
    stage.duration_days = payload.duration_days
    if payload.content_kind != stage.content_kind:
        stage.media_path = None
    stage.content_kind = payload.content_kind
    board.updated_at = now_local()
    session.commit()
    session.refresh(stage)
    return stage


def delete_stage(session: Session, board: TrackingBoard, stage_id: int):
    stage = next((item for item in board.stages if item.id == stage_id), None)
    if not stage:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    was_current = not stage.completed
    session.delete(stage)
    session.flush()
    remaining = sorted((item for item in board.stages if item.id != stage_id), key=lambda item: item.position)
    for position, item in enumerate(remaining, start=1):
        item.position = position
    if was_current:
        upcoming = next((item for item in remaining if not item.completed), None)
        if upcoming and not upcoming.started_at:
            upcoming.started_at = now_local()
    board.updated_at = now_local()
    session.commit()


def move_stage(session: Session, board: TrackingBoard, stage_id: int, direction: str):
    ordered = list(board.stages)
    index = next((i for i, item in enumerate(ordered) if item.id == stage_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")
    target_index = index + (-1 if direction == "up" else 1 if direction == "down" else 0)
    if direction not in {"up", "down"}:
        raise HTTPException(status_code=422, detail="Dirección inválida")
    if not 0 <= target_index < len(ordered):
        return
    ordered[index].position, ordered[target_index].position = ordered[target_index].position, ordered[index].position
    board.updated_at = now_local()
    session.commit()


def advance_stage(session: Session, board: TrackingBoard):
    if board.status != "executando":
        raise HTTPException(status_code=400, detail="Retome o projeto antes de avançar uma etapa")
    current = next((item for item in board.stages if not item.completed), None)
    if not current:
        raise HTTPException(status_code=400, detail="Todas as etapas já foram concluídas")
    current.completed = True
    current.completed_at = now_local()
    following = next((item for item in board.stages if not item.completed and item.id != current.id), None)
    if following:
        following.started_at = following.started_at or now_local()
    else:
        board.status = "terminada"
    board.updated_at = now_local()
    session.commit()
    return board


def set_board_status(session: Session, board: TrackingBoard, status: str):
    if status not in {"executando", "espera", "cancelada", "terminada"}:
        raise HTTPException(status_code=422, detail="Estado inválido")
    if board.status == "terminada" and status != "terminada":
        raise HTTPException(status_code=400, detail="Um projeto terminado não pode ser reaberto por este formulário")
    if status == "terminada" and (not board.stages or any(not stage.completed for stage in board.stages)):
        raise HTTPException(status_code=400, detail="Conclua todas as etapas antes de encerrar o projeto")
    board.status = status
    board.updated_at = now_local()
    session.commit()
    return board


def add_delay(session: Session, board: TrackingBoard, payload: TrackingDelayCreate, evidence_path: str | None):
    delay = TrackingDelay(board_id=board.id, lost_days=payload.lost_days, reason=payload.reason, evidence_path=evidence_path)
    session.add(delay)
    board.updated_at = now_local()
    session.commit()
    session.refresh(delay)
    return delay


def add_furniture(session: Session, board: TrackingBoard, payload: TrackedFurnitureCreate, image_path: str | None):
    item = TrackedFurniture(board_id=board.id, name=payload.name, image_path=image_path, notes="")
    session.add(item)
    board.updated_at = now_local()
    session.commit()
    session.refresh(item)
    return item


def update_furniture_notes(session: Session, board: TrackingBoard, furniture_id: int, payload: FurnitureNotesUpdate):
    item = next((value for value in board.furniture if value.id == furniture_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Móvel não encontrado")
    item.notes = payload.notes.strip()
    board.updated_at = now_local()
    session.commit()
    return item


def get_public_board(session: Session, token: str):
    board = (
        session.query(TrackingBoard)
        .filter(TrackingBoard.share_token == token)
        .options(selectinload(TrackingBoard.stages), selectinload(TrackingBoard.delays), selectinload(TrackingBoard.furniture))
        .first()
    )
    if not board:
        raise HTTPException(status_code=404, detail="Link de acompanhamento não encontrado")
    project = get_project_for_company(session, board.project_id, board.company_id)
    return board, project


def regenerate_share_token(session: Session, board: TrackingBoard):
    board.share_token = secrets.token_urlsafe(36)
    board.updated_at = now_local()
    session.commit()
    session.refresh(board)
    return board.share_token


def tracking_summary(board: TrackingBoard) -> dict:
    current = next((stage for stage in board.stages if not stage.completed), None)
    total = len(board.stages)
    completed = sum(1 for stage in board.stages if stage.completed)
    lost_days = sum(delay.lost_days for delay in board.delays)
    return {
        "current_stage": current,
        "progress": round(completed / total * 100) if total else 0,
        "completed_stages": completed,
        "total_stages": total,
        "lost_days": lost_days,
        "adjusted_delivery": board.promised_delivery.fromordinal(board.promised_delivery.toordinal() + lost_days),
    }
