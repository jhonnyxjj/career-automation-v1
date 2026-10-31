from __future__ import annotations

import asyncio

import httpx
from pydantic import ValidationError

from .deduplicator import deduplicate
from .filters import hard_filter
from .models import FetchResult, ReviewJob, SearchProfile, SearchResult, SearchStats, SourceReport, SourceStatus
from .normalizer import normalize_job
from .scorer import score_job
from .sources.base import BaseSource

SOURCE_TIMEOUT_SECONDS = 40.0


async def find_jobs(profile: SearchProfile, sources: list[BaseSource], limit: int) -> SearchResult:
    timeout = httpx.Timeout(15.0, connect=8.0)
    semaphore = asyncio.Semaphore(4)

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers={"User-Agent": "career-job-finder/0.1"}) as client:
        async def run_source(source: BaseSource) -> FetchResult:
            try:
                async with asyncio.timeout(SOURCE_TIMEOUT_SECONDS):
                    async with semaphore:
                        return await source.fetch(client)
            except Exception:
                return FetchResult(
                    report=SourceReport(source=source.name, status=SourceStatus.ERROR, message="Falha ao consultar a fonte."),
                )

        fetched = await asyncio.gather(*(run_source(source) for source in sources))

    raw_jobs = [job for result in fetched for job in result.jobs]
    normalized = []
    for raw_job in raw_jobs:
        try:
            normalized.append(normalize_job(raw_job))
        except (ValidationError, ValueError):
            continue
    unique = deduplicate(normalized)
    compatible = []
    needs_review = []
    for job in unique:
        result = hard_filter(job, profile)
        if result.accepted:
            compatible.append(job)
        elif result.reason in {"ROLE_AREA_UNKNOWN", "WORKPLACE_UNKNOWN", "REGION_UNKNOWN"}:
            needs_review.append(ReviewJob(job=job, reason=result.reason))
    scored = [score_job(job, profile) for job in compatible]
    eligible = [job for job in scored if job.score >= profile.minimum_score]

    ranked = sorted(eligible, key=lambda job: (-job.score, job.published_at is None, job.title.casefold()))[:limit]

    return SearchResult(
        jobs=ranked,
        needs_review=needs_review[:limit],
        reports=[result.report for result in fetched],
        stats=SearchStats(
            collected=len(raw_jobs),
            normalized=len(normalized),
            unique=len(unique),
            compatible=len(compatible),
        ),
    )
