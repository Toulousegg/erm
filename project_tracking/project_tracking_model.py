from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from core.database import base


def now_local():
    return datetime.now(ZoneInfo("America/Sao_Paulo"))


class TrackingBoard(base):
    __tablename__ = "project_tracking_boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    share_token = Column(String(96), unique=True, nullable=False, index=True)
    promised_days = Column(Integer, nullable=False, default=30)
    promised_delivery = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default="executando", index=True)
    created_at = Column(DateTime, default=now_local, nullable=False)
    updated_at = Column(DateTime, default=now_local, onupdate=now_local, nullable=False)

    project = relationship("Projects")
    stages = relationship("TrackingStage", back_populates="board", cascade="all, delete-orphan", order_by="TrackingStage.position")
    delays = relationship("TrackingDelay", back_populates="board", cascade="all, delete-orphan", order_by="TrackingDelay.created_at.desc()")
    furniture = relationship("TrackedFurniture", back_populates="board", cascade="all, delete-orphan", order_by="TrackedFurniture.id")


class TrackingStage(base):
    __tablename__ = "project_tracking_stages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("project_tracking_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(120), nullable=False)
    duration_days = Column(Integer, nullable=False, default=1)
    position = Column(Integer, nullable=False)
    content_kind = Column(String(20), nullable=False, default="texto")
    content_text = Column(Text, nullable=True)
    media_path = Column(String(500), nullable=True)  # legacy/single-file compatibility
    completed = Column(Boolean, nullable=False, default=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    board = relationship("TrackingBoard", back_populates="stages")
    media_assets = relationship("TrackingStageMedia", back_populates="stage", cascade="all, delete-orphan", order_by="TrackingStageMedia.id")


class TrackingStageMedia(base):
    __tablename__ = "project_tracking_stage_media"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    stage_id = Column(Integer, ForeignKey("project_tracking_stages.id", ondelete="CASCADE"), nullable=False, index=True)
    media_kind = Column(String(20), nullable=False)
    media_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=now_local, nullable=False)

    stage = relationship("TrackingStage", back_populates="media_assets")


class TrackingDelay(base):
    __tablename__ = "project_tracking_delays"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("project_tracking_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    lost_days = Column(Integer, nullable=False)
    reason = Column(Text, nullable=False)
    evidence_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=now_local, nullable=False)

    board = relationship("TrackingBoard", back_populates="delays")


class TrackedFurniture(base):
    __tablename__ = "project_tracked_furniture"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    board_id = Column(Integer, ForeignKey("project_tracking_boards.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    image_path = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=now_local, nullable=False)

    board = relationship("TrackingBoard", back_populates="furniture")
