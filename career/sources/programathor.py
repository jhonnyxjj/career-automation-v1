from ..models import SourceStatus
from .base import StatusSource


class ProgramaThorSource(StatusSource):
    def __init__(self) -> None:
        super().__init__("ProgramaThor", SourceStatus.UNAVAILABLE, "Public adapter has not been configured yet.")
