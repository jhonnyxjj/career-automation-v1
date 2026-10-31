from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from urllib.parse import urlparse

from pydantic import BaseModel, Field, field_validator


class SourceStatus(StrEnum):
    OK = "OK"
    UNAVAILABLE = "UNAVAILABLE"
    UNSUPPORTED = "UNSUPPORTED"
    ERROR = "ERROR"


class RawJob(BaseModel):
    source: str
    listing_type: str = "job"
    title: str
    company: str
    url: str
    external_id: str | None = None
    description: str | None = None
    location: str | None = None
    workplace_type: str | None = None
    seniority: str | None = None
    apply_url: str | None = None
    published_at: datetime | None = None
    expired: bool = False


class JobListing(BaseModel):
    source: str
    listing_type: str = "job"
    title: str
    company: str
    url: str
    external_id: str | None = None
    description: str | None = None
    location: str | None = None
    workplace_type: str | None = None
    seniority: str | None = None
    apply_url: str | None = None
    published_at: datetime | None = None
    technologies: list[str] = Field(default_factory=list)
    score: int = Field(default=0, ge=0, le=100)
    filter_accepted: bool | None = None
    filter_reason: str | None = None
    expired: bool = False

    @field_validator("url", "apply_url")
    @classmethod
    def require_http_url(cls, value: str | None) -> str | None:
        if value is None:
            return value
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("URL must be an absolute HTTP(S) URL")
        return value


class SearchProfile(BaseModel):
    name: str
    allowed_seniorities: set[str]
    allowed_workplaces: set[str]
    role_areas: set[str] = Field(default_factory=lambda: {"backend", "fullstack", "frontend"})
    desired_technologies: set[str] = Field(default_factory=set)
    required_technologies: set[str] = Field(default_factory=set)
    excluded_technologies: set[str] = Field(default_factory=set)
    primary_languages: set[str]
    frameworks: set[str]
    databases: set[str]
    cloud_devops: set[str]
    allowed_regions: set[str] = Field(default_factory=set)
    recency_days: int | None = None
    minimum_score: int = Field(default=0, ge=0, le=100)


class FilterResult(BaseModel):
    accepted: bool
    reason: str | None = None


class SourceReport(BaseModel):
    source: str
    status: SourceStatus
    count: int = 0
    message: str | None = None


class FetchResult(BaseModel):
    report: SourceReport
    jobs: list[RawJob] = Field(default_factory=list)


class SearchStats(BaseModel):
    collected: int = 0
    normalized: int = 0
    unique: int = 0
    compatible: int = 0


class ReviewJob(BaseModel):
    job: JobListing
    reason: str


class SearchResult(BaseModel):
    jobs: list[JobListing]
    reports: list[SourceReport]
    stats: SearchStats
    needs_review: list[ReviewJob] = Field(default_factory=list)


class ResumePersonalDetails(BaseModel):
    name: str
    headline: str | None = None
    city: str | None = None
    state: str | None = None
    phone: str | None = None
    email: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class TechnicalSkillGroup(BaseModel):
    category: str
    items: list[str] = Field(default_factory=list)


class ResumeExperience(BaseModel):
    company: str
    location: str | None = None
    position: str
    period: str
    bullets: list[str] = Field(default_factory=list)


class ResumeProject(BaseModel):
    name: str
    context: str | None = None
    technologies: list[str] = Field(default_factory=list)
    bullets: list[str] = Field(default_factory=list)


class ResumeEducation(BaseModel):
    institution: str
    location: str | None = None
    course: str
    period: str


class ResumeTemplateData(BaseModel):
    """Structured content only; the LaTeX renderer owns presentation."""

    personal: ResumePersonalDetails
    professional_summary: str | None = None
    technical_skills: list[TechnicalSkillGroup] = Field(default_factory=list)
    experiences: list[ResumeExperience] = Field(default_factory=list)
    projects: list[ResumeProject] = Field(default_factory=list)
    education: list[ResumeEducation] = Field(default_factory=list)


class CandidateProfile(ResumeTemplateData):
    """The immutable source of truth extracted from an original resume."""

    id: str
    original_resume_path: str | None = None


class GeneratedResume(BaseModel):
    id: str
    original_resume_id: str
    job_id: str
    generated_at: datetime
    latex_path: str
    pdf_path: str | None = None
