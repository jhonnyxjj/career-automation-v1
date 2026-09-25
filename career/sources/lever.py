from __future__ import annotations

import asyncio
from datetime import UTC, datetime

import httpx

from ..config.sources import DEFAULT_LEVER_SITES, SourceTarget
from ..models import FetchResult, RawJob, SourceReport, SourceStatus
from ..storage import load_settings
from .base import BaseSource


class LeverSource(BaseSource):
    name = "Lever"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        targets = _targets_from_settings("lever_sites", DEFAULT_LEVER_SITES)
        semaphore = asyncio.Semaphore(3)

        async def fetch_site(target: SourceTarget) -> list[RawJob]:
            async with semaphore:
                response = await client.get(f"https://api.lever.co/v0/postings/{target.identifier}", params={"mode": "json"})
                response.raise_for_status()
                return [
                    RawJob(
                        source=self.name,
                        external_id=str(job["id"]),
                        title=job["text"],
                        company=target.company,
                        description=job.get("descriptionPlain") or job.get("description"),
                        location=(job.get("categories") or {}).get("location"),
                        workplace_type=job.get("workplaceType"),
                        url=job["hostedUrl"],
                        apply_url=job.get("applyUrl"),
                        published_at=_timestamp(job.get("createdAt")),
                    )
                    for job in response.json()
                ]

        responses = await asyncio.gather(*(fetch_site(target) for target in targets), return_exceptions=True)
        jobs = [job for response in responses if isinstance(response, list) for job in response]
        failures = sum(isinstance(response, Exception) for response in responses)
        status = SourceStatus.OK if failures < len(targets) else SourceStatus.UNAVAILABLE
        message = f"{failures}/{len(targets)} sites failed" if failures else None
        return FetchResult(report=SourceReport(source=self.name, status=status, count=len(jobs), message=message), jobs=jobs)


def _timestamp(value: int | None) -> datetime | None:
    return datetime.fromtimestamp(value / 1000, tz=UTC) if value else None


def _targets_from_settings(key: str, defaults: tuple[SourceTarget, ...]) -> tuple[SourceTarget, ...]:
    configured = load_settings().get(key)
    if not isinstance(configured, list):
        return defaults
    targets = [
        SourceTarget(identifier=item["id"], company=item["company"])
        for item in configured
        if isinstance(item, dict) and isinstance(item.get("id"), str) and isinstance(item.get("company"), str)
    ]
    return tuple(targets) or defaults
