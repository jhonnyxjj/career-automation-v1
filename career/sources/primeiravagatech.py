from __future__ import annotations

import asyncio
import re
from datetime import UTC, datetime
from html import unescape

import httpx

from ..models import FetchResult, RawJob, SourceReport, SourceStatus
from .base import BaseSource


class PrimeiraVagaTechSource(BaseSource):
    name = "PrimeiraVagaTech"
    base_url = "https://www.primeiravagatech.com.br"
    api_url = "https://primeiravagatech-production.up.railway.app/minhavagatech/vagas/paginated"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        response = await client.get(self.api_url)
        response.raise_for_status()
        listings = response.json().get("content", [])
        semaphore = asyncio.Semaphore(3)

        async def fetch_detail(listing: dict) -> RawJob | None:
            slug = listing.get("slug")
            if not isinstance(slug, str):
                return None
            try:
                async with semaphore:
                    detail_response = await client.get(f"{self.api_url.rsplit('/', 1)[0]}/{slug}")
                    detail_response.raise_for_status()
                detail = detail_response.json()
            except (httpx.HTTPError, ValueError):
                return None
            return _to_raw_job(listing, detail, self.name, self.base_url)

        detailed_jobs = await asyncio.gather(*(fetch_detail(listing) for listing in listings if isinstance(listing, dict)))
        jobs = [job for job in detailed_jobs if job is not None]
        failed_details = len(listings) - len(jobs)
        message = f"{failed_details} detalhes indisponíveis" if failed_details else None
        return FetchResult(
            report=SourceReport(source=self.name, status=SourceStatus.OK, count=len(jobs), message=message),
            jobs=jobs,
        )


def _to_raw_job(listing: dict, detail: dict, source: str, base_url: str) -> RawJob | None:
    slug = listing.get("slug")
    title = detail.get("title") or listing.get("title")
    company = detail.get("companyName") or listing.get("companyName")
    if not isinstance(slug, str) or not isinstance(title, str) or not isinstance(company, str):
        return None
    if not all(value.strip() for value in (slug, title, company)):
        return None
    city = detail.get("city") or listing.get("city")
    state = detail.get("state") or listing.get("state")
    location = " - ".join(value for value in (city, state) if isinstance(value, str) and value.strip()) or None
    return RawJob(
        source=source,
        external_id=str(detail.get("id") or listing.get("id") or slug),
        title=title,
        company=company,
        description=_plain_text(detail.get("description")),
        location=location,
        seniority=title,
        url=f"{base_url}/vaga/{slug}",
        apply_url=detail.get("originalUrl") if isinstance(detail.get("originalUrl"), str) else None,
        published_at=_date(detail.get("datePosted") or listing.get("datePosted")),
    )


def _plain_text(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    return re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", value))).strip() or None


def _date(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed.astimezone(UTC)
    except ValueError:
        return None
