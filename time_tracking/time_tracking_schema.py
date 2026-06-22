from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date as DATE, time as TIME
from core.enum.enum import ProjectStageEnum


class TimeEntryCreate(BaseModel):
    project_id: int
    stage: ProjectStageEnum
    task: Optional[str] = None
    description: Optional[str] = None
    work_date: Optional[DATE] = None
    start_time: TIME
    end_time: TIME

    @field_validator("stage", mode="before")
    @classmethod
    def parse_stage(cls, value):
        if isinstance(value, str) and value in ProjectStageEnum.__members__:
            return ProjectStageEnum[value]
        return value

    @field_validator("task", "description", "work_date", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

    class Config:
        from_attributes = True


class TimeEntryUpdate(BaseModel):
    project_id: Optional[int] = None
    stage: Optional[ProjectStageEnum] = None
    task: Optional[str] = None
    description: Optional[str] = None
    work_date: Optional[DATE] = None
    start_time: Optional[TIME] = None
    end_time: Optional[TIME] = None

    @field_validator("stage", mode="before")
    @classmethod
    def parse_stage(cls, value):
        if isinstance(value, str) and value in ProjectStageEnum.__members__:
            return ProjectStageEnum[value]
        return value

    @field_validator("project_id", "stage", "task", "description", "work_date", "start_time", "end_time", mode="before")
    @classmethod
    def empty_string_to_none(cls, value):
        if value == "":
            return None
        return value

    class Config:
        from_attributes = True
