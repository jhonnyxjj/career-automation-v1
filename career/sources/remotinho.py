from __future__ import annotations

import base64
from html.parser import HTMLParser
from urllib.parse import urljoin

import httpx

from ..models import FetchResult, RawJob, SourceReport, SourceStatus
from .base import BaseSource


class RemotinhoSource(BaseSource):
    name = "Remotinho"
    jobs_url = "https://remotinho.com.br/jobs"

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        response = await client.get(self.jobs_url)
        response.raise_for_status()
        parser = _JobsParser()
        parser.feed(response.text)
        jobs = [_to_raw_job(card, self.name, self.jobs_url) for card in parser.jobs]
        return FetchResult(
            report=SourceReport(source=self.name, status=SourceStatus.OK, count=len(jobs)),
            jobs=jobs,
        )


class _JobsParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.jobs: list[dict[str, str]] = []
        self.current: dict[str, str] = {}
        self.capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        class_name = attributes.get("class") or ""
        if tag == "h3" and "font-size-6" in class_name and "mb-3" in class_name:
            self.current = {"title": ""}
            self.capture = "title"
        elif tag == "p" and self.current.get("title") and "font-size-4 text-gray mb-4" in class_name:
            self.current["description"] = ""
            self.capture = "description"
        elif tag == "a" and self.current.get("title") and (href := attributes.get("href") or "").startswith("/job/"):
            self.current["path"] = href
            self.jobs.append(self.current)
            self.current = {}

    def handle_endtag(self, tag: str) -> None:
        if tag in {"h3", "p"}:
            self.capture = None

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.current[self.capture] = self.current.get(self.capture, "") + data


def _to_raw_job(card: dict[str, str], source: str, jobs_url: str) -> RawJob:
    path = card["path"]
    token = path.rsplit("/", 1)[-1]
    apply_url = _destination_url(token)
    return RawJob(
        source=source,
        external_id=token,
        title=card["title"].strip(),
        company=source,
        description=card.get("description", "").strip() or None,
        seniority=card["title"],
        url=urljoin(jobs_url, path),
        apply_url=apply_url,
    )


def _destination_url(token: str) -> str | None:
    try:
        padding = "=" * (-len(token) % 4)
        _, _, destination = base64.urlsafe_b64decode(token + padding).decode("utf-8").split("|", maxsplit=2)
    except (UnicodeDecodeError, ValueError):
        return None
    return destination if destination.startswith(("https://", "http://")) else None
