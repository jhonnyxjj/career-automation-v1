from ..models import SourceStatus
from .base import StatusSource


class IndeedSource(StatusSource):
    def __init__(self) -> None:
        super().__init__("Indeed", SourceStatus.UNSUPPORTED, "No public API is configured for this prototype.")
