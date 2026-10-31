from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .config import TECH_CATALOG
from .finder import find_jobs
from .models import CandidateProfile, GeneratedResume, JobListing, ResumeTemplateData, SearchProfile, SearchResult
from .profile_parser import parse_candidate_profile
from .profile_api import router as profile_router
from .tracker_api import router as tracker_router
from .tracker import save_search
from .resume_storage import RESUMES_DIR, ResumeRepository
from .sources import default_sources


MAX_RESUME_SIZE = 10 * 1024 * 1024
app = FastAPI(title="Career Automation API")
app.include_router(profile_router)
app.include_router(tracker_router)
allowed_origins = [origin for origin in os.getenv("CAREER_ALLOWED_ORIGINS", "http://localhost:3000").split(",") if origin]
app.add_middleware(CORSMiddleware, allow_origins=allowed_origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Content-Type"])


class CandidateProfileResponse(ResumeTemplateData):
    id: str


class ProfileUploadResponse(BaseModel):
    profile: CandidateProfileResponse
    warnings: list[str] = Field(default_factory=list)


class JobSearchRequest(BaseModel):
    profile_id: str
    seniorities: set[str] = Field(default_factory=lambda: {"intern", "junior"})
    regions: set[str] = Field(default_factory=lambda: {"brazil", "europe", "global"})
    work_modes: set[str] = Field(default_factory=lambda: {"remote"})
    limit: int = Field(default=20, ge=1, le=50)


class TailorResumeRequest(BaseModel):
    profile_id: str
    job: JobListing


class GeneratedResumeResponse(BaseModel):
    id: str
    original_resume_id: str
    job_id: str
    generated_at: datetime
    pdf_available: bool


@app.get("/health")
def health() -> dict[str, bool]:
    return {"ok": True}


def profile_id_or_404(profile_id: str) -> str:
    try:
        return str(UUID(profile_id))
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.") from error


@app.post("/profiles/upload", response_model=ProfileUploadResponse)
async def upload_profile(file: UploadFile = File(...)) -> ProfileUploadResponse:
    content = await file.read(MAX_RESUME_SIZE + 1)
    if len(content) > MAX_RESUME_SIZE:
        raise HTTPException(status_code=413, detail="O PDF deve ter no máximo 10 MB.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=415, detail="Envie um arquivo PDF válido.")

    profile_id = str(uuid4())
    original_path = RESUMES_DIR / "original" / f"{profile_id}.pdf"
    original_path.parent.mkdir(parents=True, exist_ok=True)
    original_path.write_bytes(content)
    try:
        profile = await asyncio.to_thread(parse_candidate_profile, content, profile_id, original_path)
        ResumeRepository().save_original(profile)
    except ValueError as error:
        original_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=str(error)) from error
    public_profile = CandidateProfileResponse.model_validate(profile.model_dump(exclude={"original_resume_path"}))
    return ProfileUploadResponse(profile=public_profile, warnings=["Confirme o perfil identificado antes de gerar um currículo adaptado."])


@app.get("/profiles/{profile_id}", response_model=CandidateProfileResponse)
def get_profile(profile_id: str) -> CandidateProfileResponse:
    try:
        profile = ResumeRepository().load_original(profile_id_or_404(profile_id))
        return CandidateProfileResponse.model_validate(profile.model_dump(exclude={"original_resume_path"}))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.") from error


@app.post("/jobs/search", response_model=SearchResult)
async def search_jobs(request: JobSearchRequest) -> SearchResult:
    try:
        candidate = ResumeRepository().load_original(profile_id_or_404(request.profile_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.") from error
    technologies = {item for group in candidate.technical_skills for item in group.items}
    categories = {technology: TECH_CATALOG[technology][0] for technology in technologies if technology in TECH_CATALOG}
    profile = SearchProfile(
        name=candidate.personal.name,
        allowed_seniorities=request.seniorities,
        allowed_workplaces=request.work_modes,
        allowed_regions=request.regions,
        role_areas={"backend", "fullstack", "frontend"},
        desired_technologies=technologies,
        primary_languages={technology for technology, category in categories.items() if category == "language"},
        frameworks={technology for technology, category in categories.items() if category == "framework"},
        databases={technology for technology, category in categories.items() if category == "database"},
        cloud_devops={technology for technology, category in categories.items() if category == "cloud_devops"},
    )
    result = await find_jobs(profile, default_sources(), request.limit)
    await asyncio.to_thread(save_search, candidate.id, request.model_dump(mode="json"), result)
    return result


@app.post("/resumes/tailor", response_model=GeneratedResumeResponse)
async def tailor_resume(request: TailorResumeRequest) -> GeneratedResumeResponse:
    try:
        profile = ResumeRepository().load_confirmed(profile_id_or_404(request.profile_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Perfil confirmado não encontrado.") from error
    generated = await asyncio.to_thread(ResumeRepository().generate_tailored, profile, request.job)
    return GeneratedResumeResponse(
        id=generated.id,
        original_resume_id=generated.original_resume_id,
        job_id=generated.job_id,
        generated_at=generated.generated_at,
        pdf_available=generated.pdf_path is not None,
    )


@app.get("/resumes/{resume_id}/download/{format}")
def download_resume(resume_id: str, format: str) -> FileResponse:
    if format not in {"tex", "pdf"}:
        raise HTTPException(status_code=404, detail="Formato não suportado.")
    try:
        safe_id = str(UUID(resume_id))
    except ValueError as error:
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.") from error
    path = RESUMES_DIR / "tailored" / safe_id / f"resume.{format}"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
    media_type = "application/pdf" if format == "pdf" else "application/x-tex"
    return FileResponse(path, media_type=media_type, filename=f"curriculo-adaptado.{format}")
