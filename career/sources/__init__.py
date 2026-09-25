from .glassdoor import GlassdoorSource
from .greenhouse import GreenhouseSource
from .gupy import GupySource
from .indeed import IndeedSource
from .lever import LeverSource
from .linkedin import LinkedInSource
from .programathor import ProgramaThorSource
from .wellfound import WellfoundSource


def default_sources():
    return [
        GreenhouseSource(), LeverSource(), GupySource(), ProgramaThorSource(), WellfoundSource(),
        LinkedInSource(), IndeedSource(), GlassdoorSource(),
    ]
