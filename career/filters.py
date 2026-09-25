from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta

from .config.filtering import DEVELOPMENT_TERMS, NON_DEVELOPMENT_TITLE_TERMS, SENIOR_TITLE_TERMS
from .models import FilterResult, JobListing, SearchProfile
from .normalizer import normalized_text


def hard_filter(job: JobListing, profile: SearchProfile, now: datetime | None = None) -> FilterResult:
    text = normalized_text(" ".join(filter(None, (job.title, job.description))))
    title = normalized_text(job.title)

    if job.expired:
        return FilterResult(accepted=False, reason="EXPIRED")
    if any(term in title for term in SENIOR_TITLE_TERMS) and "senior" not in profile.allowed_seniorities:
        return FilterResult(accepted=False, reason="SENIORITY_NOT_ALLOWED")
    if job.seniority and job.seniority not in profile.allowed_seniorities:
        return FilterResult(accepted=False, reason="SENIORITY_NOT_ALLOWED")
    if any(term in title for term in NON_DEVELOPMENT_TITLE_TERMS) or not any(term in text for term in DEVELOPMENT_TERMS):
        return FilterResult(accepted=False, reason="NOT_DEVELOPMENT")
    if profile.role_areas and not _matches_role_area(text, profile.role_areas):
        return FilterResult(accepted=False, reason="ROLE_AREA_NOT_ALLOWED")
    if profile.excluded_technologies.intersection(job.technologies):
        return FilterResult(accepted=False, reason="EXCLUDED_TECHNOLOGY")
    if profile.required_technologies and not profile.required_technologies.issubset(set(job.technologies)):
        return FilterResult(accepted=False, reason="REQUIRED_TECHNOLOGY_MISSING")
    if job.workplace_type == "onsite" and "onsite" not in profile.allowed_workplaces:
        return FilterResult(accepted=False, reason="WORKPLACE_NOT_ALLOWED")
    if profile.allowed_regions and "global" not in profile.allowed_regions and not _matches_region(job, profile.allowed_regions):
        return FilterResult(accepted=False, reason="REGION_NOT_ALLOWED")
    if profile.recency_days is not None and job.published_at:
        reference = now or datetime.now(UTC)
        published = job.published_at if job.published_at.tzinfo else job.published_at.replace(tzinfo=UTC)
        if published < reference - timedelta(days=profile.recency_days):
            return FilterResult(accepted=False, reason="TOO_OLD")
    if profile.desired_technologies and job.technologies and not set(job.technologies).intersection(profile.desired_technologies):
        return FilterResult(accepted=False, reason="INCOMPATIBLE_STACK")
    return FilterResult(accepted=True)


def _matches_role_area(text: str, allowed_areas: set[str]) -> bool:
    matches = {
        "backend": bool(re.search(r"\b(back[ -]?end|api|server[- ]side)\b", text)),
        "frontend": bool(re.search(r"\b(front[ -]?end|ui|ux)\b", text)),
        "fullstack": bool(re.search(r"\b(full[ -]?stack)\b", text)),
    }
    return not any(matches.values()) or any(matches[area] for area in allowed_areas)


def _matches_region(job: JobListing, allowed_regions: set[str]) -> bool:
    location = normalized_text(job.location)
    aliases = {
        "brazil": ("brazil", "brasil"),
        "united_states": ("united states", "usa", "u.s."),
        "canada": ("canada",),
        "europe": ("europe", "europa", "germany", "france", "portugal", "spain", "netherlands"),
        "united_kingdom": ("united kingdom", "uk", "england", "reino unido"),
        "latin_america": ("latin america", "america latina", "mexico", "argentina", "chile", "colombia"),
    }
    return bool(location) and any(alias in location for region in allowed_regions for alias in aliases.get(region, ()))
