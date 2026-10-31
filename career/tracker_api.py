from typing import Literal
from uuid import UUID

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .models import JobListing
from .resume_storage import ResumeRepository
from .tracker import load_tracker, save_job, update_job


router = APIRouter(prefix="/tracker")


class ApplicationUpdate(BaseModel):
    status: Literal["discovered", "saved", "applied", "interview", "offer", "closed"]
    notes: str = Field(default="", max_length=10_000)
    favorite: bool = False


def _profile_id(value: str) -> str:
    try:
        safe_id = str(UUID(value))
        ResumeRepository().load_confirmed(safe_id)
        return safe_id
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Perfil confirmado não encontrado.") from error


@router.get("/{profile_id}")
def get_tracker(profile_id: str):
    return load_tracker(_profile_id(profile_id))


@router.post("/{profile_id}/jobs")
def add_job(profile_id: str, job: JobListing):
    return save_job(_profile_id(profile_id), job)


@router.post("/{profile_id}/jobs/{job_id}")
def change_application(profile_id: str, job_id: str, update: ApplicationUpdate):
    safe_id = _profile_id(profile_id)
    try:
        safe_job_id = str(UUID(job_id))
        return update_job(safe_id, safe_job_id, **update.model_dump())
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Vaga não encontrada.") from error
