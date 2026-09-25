from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .config import TECH_CATALOG
from .models import JobListing, RawJob


def normalized_text(value: str | None) -> str:
    if not value:
        return ""
    value = unicodedata.normalize("NFKD", value)
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", value).strip().casefold()


def display_text(value: str | None) -> str | None:
    if not value:
        return None
    return re.sub(r"\s+", " ", value).strip()


def canonical_url(url: str) -> str:
    parts = urlsplit(url)
    query = [(key, value) for key, value in parse_qsl(parts.query) if not key.lower().startswith("utm_")]
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), path, urlencode(sorted(query)), ""))


def infer_seniority(text: str) -> str | None:
    value = normalized_text(text)
    if re.search(r"\b(estagio|estagiario|intern(ship)?)\b", value):
        return "intern"
    if re.search(r"\b(junior|jr\.?|entry level)\b", value):
        return "junior"
    if re.search(r"\b(pleno|mid[- ]?level|mid)\b", value):
        return "mid"
    if re.search(r"\b(senior|sr\.?|staff|principal|lead|manager|architect)\b", value):
        return "senior"
    return None


def infer_workplace(text: str) -> str | None:
    value = normalized_text(text)
    if re.search(r"\b(remote|remoto|home office|work from home)\b", value):
        return "remote"
    if re.search(r"\b(hybrid|hibrido)\b", value):
        return "hybrid"
    if re.search(r"\b(on[- ]?site|in[- ]?office|presencial|office based)\b", value):
        return "onsite"
    return None


def extract_technologies(text: str) -> list[str]:
    value = normalized_text(text)
    technologies: list[str] = []
    for technology, (_, aliases) in TECH_CATALOG.items():
        if any(re.search(rf"(?<!\w){re.escape(alias)}(?!\w)", value) for alias in aliases):
            technologies.append(technology)
    return technologies


def normalize_job(raw: RawJob) -> JobListing:
    title = display_text(raw.title) or ""
    company = display_text(raw.company) or ""
    description = display_text(raw.description)
    combined_text = " ".join(part for part in (title, description, raw.seniority) if part)
    return JobListing(
        source=display_text(raw.source) or raw.source,
        external_id=display_text(raw.external_id),
        title=title,
        company=company,
        description=description,
        location=display_text(raw.location),
        workplace_type=infer_workplace(raw.workplace_type or " ".join((combined_text, raw.location or ""))),
        seniority=infer_seniority(raw.seniority or combined_text),
        url=canonical_url(raw.url),
        apply_url=canonical_url(raw.apply_url) if raw.apply_url else None,
        published_at=raw.published_at,
        technologies=extract_technologies(combined_text),
        expired=raw.expired,
    )


def job_fingerprint(job: JobListing) -> str:
    return "|".join(normalized_text(value) for value in (job.company, job.title, job.location))
