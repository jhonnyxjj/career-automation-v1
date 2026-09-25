from ..models import SourceStatus
from .base import StatusSource


class GupySource(StatusSource):
    def __init__(self) -> None:
        super().__init__("Gupy", SourceStatus.UNAVAILABLE, "No stable public aggregate API is configured.")
