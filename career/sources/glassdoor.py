from ..models import SourceStatus
from .base import StatusSource


class GlassdoorSource(StatusSource):
    def __init__(self) -> None:
        super().__init__("Glassdoor", SourceStatus.UNSUPPORTED, "No login or browser automation is performed.")
