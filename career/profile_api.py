from uuid import UUID

from fastapi import APIRouter, HTTPException

from .models import ResumeTemplateData
from .profile_store import load_current, save_confirmed


router = APIRouter(prefix="/profile")


def _public(profile):
    return {"id": profile.id, **profile.model_dump(exclude={"id", "original_resume_path"})}


@router.get("/current")
def current_profile():
    try:
        return _public(load_current())
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Nenhum perfil confirmado.") from error


@router.post("/{profile_id}/confirm")
def confirm_profile(profile_id: str, data: ResumeTemplateData):
    try:
        safe_id = str(UUID(profile_id))
        return _public(save_confirmed(safe_id, data))
    except (ValueError, FileNotFoundError) as error:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.") from error
