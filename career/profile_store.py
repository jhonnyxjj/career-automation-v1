from __future__ import annotations

import os
import tempfile
from pathlib import Path

from .models import CandidateProfile, ResumeTemplateData
from .resume_storage import RESUMES_DIR, ResumeRepository


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def confirmed_path(profile_id: str) -> Path:
    return RESUMES_DIR / "confirmed" / f"{profile_id}.json"


def save_confirmed(profile_id: str, data: ResumeTemplateData) -> CandidateProfile:
    original = ResumeRepository().load_original(profile_id)
    profile = CandidateProfile(id=original.id, original_resume_path=original.original_resume_path, **data.model_dump())
    _atomic_write(confirmed_path(profile_id), profile.model_dump_json(indent=2))
    _atomic_write(RESUMES_DIR / "current-profile", profile_id)
    return profile


def load_current() -> CandidateProfile:
    profile_id = (RESUMES_DIR / "current-profile").read_text(encoding="utf-8").strip()
    from uuid import UUID
    profile_id = str(UUID(profile_id))
    return CandidateProfile.model_validate_json(confirmed_path(profile_id).read_text(encoding="utf-8"))
