from ..models import SourceStatus
from .base import StatusSource


class LinkedInSource(StatusSource):
    def __init__(self) -> None:
        super().__init__("LinkedIn", SourceStatus.UNSUPPORTED, "No login, CAPTCHA bypass, or browser automation is performed.")
