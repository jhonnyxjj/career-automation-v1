from __future__ import annotations

from abc import ABC, abstractmethod

import httpx

from ..models import FetchResult, SourceStatus


class BaseSource(ABC):
    name: str

    @abstractmethod
    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        raise NotImplementedError


class StatusSource(BaseSource):
    def __init__(self, name: str, status: SourceStatus, message: str) -> None:
        self.name = name
        self.status = status
        self.message = message

    async def fetch(self, client: httpx.AsyncClient) -> FetchResult:
        from ..models import FetchResult, SourceReport

        return FetchResult(report=SourceReport(source=self.name, status=self.status, message=self.message))
