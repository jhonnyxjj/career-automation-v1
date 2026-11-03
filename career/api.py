from __future__ import annotations

import asyncio
import ipaddress
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from uuid import UUID, uuid4

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field, field_validator

from .config import TECH_CATALOG
from .finder import find_jobs
from .filters import hard_filter
from .models import CandidateProfile, GeneratedResume, JobListing, RawJob, ResumeTemplateData, SearchProfile, SearchResult
from .normalizer import normalize_job
from .scorer import score_job
from .profile_parser import parse_candidate_profile
from .profile_api import router as profile_router
from .tracker_api import router as tracker_router
from .tracker import TrackerDataError, save_job, save_search
from .resume_storage import RESUMES_DIR, ResumeRepository
from .sources import default_sources


MAX_RESUME_SIZE = 10 * 1024 * 1024
app = FastAPI(title="Career Automation API")


@app.exception_handler(TrackerDataError)
async def tracker_data_error_handler(_request: Request, _error: TrackerDataError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Dados de acompanhamento inválidos."})


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
    regions: set[str] = Field(default_factory=lambda: {"brazil", "global"})
    work_modes: set[str] = Field(default_factory=lambda: {"remote"})
    limit: int = Field(default=20, ge=1, le=50)


class TailorResumeRequest(BaseModel):
    profile_id: str
    job: JobListing


class ManualJobImportRequest(BaseModel):
    profile_id: str
    source: str = Field(min_length=1, max_length=80)
    listing_type: str = Field(default="job", pattern="^(job|recruiter_post)$")
    title: str = Field(min_length=1, max_length=200)
    company: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=20_000)
    source_url: str
    apply_url: str | None = None
    location: str | None = Field(default=None, max_length=200)
    seniorities: set[str] = Field(default_factory=lambda: {"intern", "junior"})
    regions: set[str] = Field(default_factory=lambda: {"brazil", "global"})
    work_modes: set[str] = Field(default_factory=lambda: {"remote"})

    @field_validator("source_url", "apply_url")
    @classmethod
    def require_http_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parsed = urlparse(value)
        if (parsed.scheme not in {"http", "https"} or not parsed.hostname
                or "\\" in parsed.netloc or any(ord(char) <= 32 or ord(char) == 127 for char in value)):
            raise ValueError("URL deve ser HTTP(S) absoluta.")
        host = parsed.hostname.rstrip(".").casefold()
        if not host or "%" in host or host == "localhost" or host.endswith((".localhost", ".local")):
            raise ValueError("URL local ou privada não é permitida.")
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            if ":" in host or "." not in host or re.fullmatch(r"(?:0x[0-9a-f]+|\d+)(?:\.(?:0x[0-9a-f]+|\d+))*", host):
                raise ValueError("URL local ou privada não é permitida.") from None
        else:
            if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
                address = address.ipv4_mapped
            if not address.is_global or address.is_multicast or address.is_reserved:
                raise ValueError("URL local ou privada não é permitida.")
        return value


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
    profile = search_profile(candidate, request.seniorities, request.regions, request.work_modes)
    result = await find_jobs(profile, default_sources(), request.limit)
    await asyncio.to_thread(save_search, candidate.id, request.model_dump(mode="json"), result)
    return result


@app.post("/jobs/import", response_model=JobListing)
def import_job(request: ManualJobImportRequest) -> JobListing:
    try:
        candidate = ResumeRepository().load_original(profile_id_or_404(request.profile_id))
    except FileNotFoundError as error:
        raise HTTPException(status_code=404, detail="Perfil não encontrado.") from error

    profile = search_profile(candidate, request.seniorities, request.regions, request.work_modes)
    job = normalize_job(RawJob(
        source=request.source,
        listing_type=request.listing_type,
        title=request.title,
        company=request.company,
        description=request.description,
        location=request.location,
        url=request.source_url,
        apply_url=request.apply_url,
    ))
    result = hard_filter(job, profile)
    scored = score_job(job, profile).model_copy(update={"filter_accepted": result.accepted, "filter_reason": result.reason})
    save_job(candidate.id, scored)
    return scored


def search_profile(
    candidate: CandidateProfile,
    seniorities: set[str],
    regions: set[str],
    work_modes: set[str],
) -> SearchProfile:
    technologies = {item for group in candidate.technical_skills for item in group.items}
    categories = {technology: TECH_CATALOG[technology][0] for technology in technologies if technology in TECH_CATALOG}
    return SearchProfile(
        name=candidate.personal.name,
        allowed_seniorities=seniorities,
        allowed_workplaces=work_modes,
        allowed_regions=regions,
        role_areas={"backend", "fullstack"},
        desired_technologies=technologies,
        primary_languages={technology for technology, category in categories.items() if category == "language"},
        frameworks={technology for technology, category in categories.items() if category == "framework"},
        databases={technology for technology, category in categories.items() if category == "database"},
        cloud_devops={technology for technology, category in categories.items() if category == "cloud_devops"},
    )


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
