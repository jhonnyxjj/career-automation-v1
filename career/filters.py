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
    if job.seniority == "senior" or any(term in title for term in SENIOR_TITLE_TERMS):
        return FilterResult(accepted=False, reason="SENIORITY_NOT_ALLOWED")
    if job.seniority and job.seniority not in profile.allowed_seniorities:
        return FilterResult(accepted=False, reason="SENIORITY_NOT_ALLOWED")
    if any(term in title for term in NON_DEVELOPMENT_TITLE_TERMS) or not any(term in text for term in DEVELOPMENT_TERMS):
        return FilterResult(accepted=False, reason="NOT_DEVELOPMENT")
    if (profile.role_areas and "frontend" not in profile.role_areas
            and re.search(r"\bfront[ -]?end\b", title)
            and not re.search(r"\b(?:back[ -]?end|full[ -]?stack)\b", title)):
        return FilterResult(accepted=False, reason="ROLE_AREA_NOT_ALLOWED")
    if profile.role_areas and not _matches_role_area(text, profile.role_areas):
        reason = "ROLE_AREA_NOT_ALLOWED" if _matches_role_area(text, {"backend", "frontend", "fullstack"}) else "ROLE_AREA_UNKNOWN"
        return FilterResult(accepted=False, reason=reason)
    if profile.excluded_technologies.intersection(job.technologies):
        return FilterResult(accepted=False, reason="EXCLUDED_TECHNOLOGY")
    if profile.required_technologies and not profile.required_technologies.issubset(set(job.technologies)):
        return FilterResult(accepted=False, reason="REQUIRED_TECHNOLOGY_MISSING")
    if not job.workplace_type:
        return FilterResult(accepted=False, reason="WORKPLACE_UNKNOWN")
    if job.workplace_type not in profile.allowed_workplaces:
        return FilterResult(accepted=False, reason="WORKPLACE_NOT_ALLOWED")
    if profile.allowed_regions:
        location = normalized_text(job.location).strip(" -/(),")
        if not location or location in {"remote", "remoto", "home office", "work from home"}:
            return FilterResult(accepted=False, reason="REGION_UNKNOWN")
        if not _matches_region(job, profile.allowed_regions):
            return FilterResult(accepted=False, reason="REGION_NOT_ALLOWED")
        if _has_geographic_restriction(job.description):
            return FilterResult(accepted=False, reason="REGION_UNKNOWN")
        if job.workplace_type in {"hybrid", "onsite"} and "brazil" in profile.allowed_regions and _matches_region(job, {"brazil"}):
            location = normalized_text(job.location)
            city = re.split(r"\s*[,;/]\s*|\s+-\s+", location, maxsplit=1)[0]
            if city in {"brazil", "brasil", "rj", "estado do rio de janeiro"}:
                return FilterResult(accepted=False, reason="LOCALITY_UNKNOWN")
            if city not in {"rio de janeiro", "petropolis"}:
                return FilterResult(accepted=False, reason="LOCALITY_NOT_ALLOWED")
    if job.seniority == "mid" and not {"JavaScript", "TypeScript"}.intersection(job.technologies):
        reason = "MID_STACK_NOT_ALLOWED" if {"Java", "C#"}.intersection(job.technologies) else "MID_STACK_UNKNOWN"
        return FilterResult(accepted=False, reason=reason)
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
    return any(matches.get(area, False) for area in allowed_areas)


def _matches_region(job: JobListing, allowed_regions: set[str]) -> bool:
    location = normalized_text(job.location)
    if re.search(r"\b(except|excluding|excluded|not|outside|exceto|excluindo|nao|fora)\b", location):
        return False
    aliases = {
        "brazil": ("brazil", "brasil", "rio de janeiro", "petropolis"),
        "united_states": ("united states", "usa", "u.s."),
        "canada": ("canada",),
        "europe": ("europe", "europa", "germany", "france", "portugal", "spain", "netherlands"),
        "united_kingdom": ("united kingdom", "uk", "england", "reino unido"),
        "latin_america": ("latin america", "america latina", "mexico", "argentina", "chile", "colombia"),
    }
    specific_regions = allowed_regions - {"global"}
    if any(alias in location for region in specific_regions for alias in aliases.get(region, ())):
        return True
    return job.workplace_type == "remote" and "global" in allowed_regions and location in {
        "worldwide", "global", "anywhere", "remote worldwide", "remote - worldwide",
    }


def _has_geographic_restriction(description: str | None) -> bool:
    value = normalized_text(description)
    region = r"\b(?:brazil|brasil|us|usa|united states|estados unidos|canada|europe|europa|uk|united kingdom|reino unido)\b"
    restriction = r"\b(?:only|restricted|excluding|except|outside|must be based|must reside|exclusiv[oa]s?|apenas|somente|exceto|fora|residentes)\b"
    return bool(re.search(rf"(?:{region}[^.;]{{0,100}}{restriction}|{restriction}[^.;]{{0,100}}{region})", value))
