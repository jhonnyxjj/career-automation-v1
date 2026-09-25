from ..models import SourceStatus
from .base import StatusSource


class WellfoundSource(StatusSource):
    def __init__(self) -> None:
        super().__init__("Wellfound", SourceStatus.UNSUPPORTED, "Search requires browser/session behavior not used by this prototype.")
