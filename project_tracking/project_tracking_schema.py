from datetime import date

from pydantic import BaseModel, Field, field_validator


class TrackingBoardCreate(BaseModel):
    project_id: int = Field(gt=0)
    promised_days: int = Field(default=30, ge=1, le=3650)
    promised_delivery: date


class TrackingStageCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    duration_days: int = Field(default=1, ge=0, le=3650)
    content_kind: str = Field(default="texto", pattern="^(texto|foto|video|pdf)$")
    content_text: str | None = Field(default=None, max_length=10000)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class TrackingStageUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    duration_days: int = Field(ge=0, le=3650)
    content_kind: str = Field(pattern="^(texto|foto|video|pdf)$")

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class TrackingDelayCreate(BaseModel):
    lost_days: int = Field(ge=1, le=3650)
    reason: str = Field(min_length=3, max_length=3000)

    @field_validator("reason")
    @classmethod
    def clean_reason(cls, value: str) -> str:
        return value.strip()


class TrackedFurnitureCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        return value.strip()


class FurnitureNotesUpdate(BaseModel):
    notes: str = Field(default="", max_length=10000)


class TrackingStatusUpdate(BaseModel):
    status: str = Field(pattern="^(executando|espera|cancelada|terminada)$")
