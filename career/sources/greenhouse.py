from __future__ import annotations

import asyncio

import httpx
from pydantic import ValidationError

from ..config.sources import DEFAULT_GREENHOUSE_BOARDS, SourceTarget
from ..models import FetchResult, RawJob, SourceReport, SourceStatus
from ..storage import load_settings
from .base import BaseSource


class GreenhouseSource(BaseSource):
    name = "Greenhouse"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        targets = _targets_from_settings("greenhouse_boards", DEFAULT_GREENHOUSE_BOARDS)
        semaphore = asyncio.Semaphore(3)

        async def fetch_board(target: SourceTarget) -> list[RawJob]:
            async with semaphore:
                response = await client.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{target.identifier}/jobs",
                    params={"content": "true"},
                )
                response.raise_for_status()
                payload = response.json()
                return [
                    RawJob(
                        source=self.name,
                        external_id=str(job["id"]),
                        title=job["title"],
                        company=target.company,
                        description=job.get("content"),
                        location=(job.get("location") or {}).get("name"),
                        url=job["absolute_url"],
                        published_at=job.get("updated_at"),
                    )
                    for job in payload.get("jobs", [])
                ]

        responses = await asyncio.gather(*(fetch_board(target) for target in targets), return_exceptions=True)
        jobs = [job for response in responses if isinstance(response, list) for job in response]
        failures = sum(isinstance(response, Exception) for response in responses)
        status = SourceStatus.OK if failures < len(targets) else SourceStatus.UNAVAILABLE
        message = f"{failures}/{len(targets)} boards failed" if failures else None
        return FetchResult(report=SourceReport(source=self.name, status=status, count=len(jobs), message=message), jobs=jobs)


def _targets_from_settings(key: str, defaults: tuple[SourceTarget, ...]) -> tuple[SourceTarget, ...]:
    configured = load_settings().get(key)
    if not isinstance(configured, list):
        return defaults
    targets: list[SourceTarget] = []
    for item in configured:
        try:
            targets.append(SourceTarget(identifier=item["id"], company=item["company"]))
        except (KeyError, TypeError, ValidationError):
            continue
    return tuple(targets) or defaults
