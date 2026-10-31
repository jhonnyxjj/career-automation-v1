from .glassdoor import GlassdoorSource
from .greenhouse import GreenhouseSource
from .gupy import GupySource
from .indeed import IndeedSource
from .lever import LeverSource
from .linkedin import LinkedInSource
from .programathor import ProgramaThorSource
from .primeiravagatech import PrimeiraVagaTechSource
from .remotinho import RemotinhoSource
from .wellfound import WellfoundSource


def default_sources():
    return [
        GreenhouseSource(), LeverSource(), PrimeiraVagaTechSource(), RemotinhoSource(), GupySource(), ProgramaThorSource(), WellfoundSource(),
        LinkedInSource(), IndeedSource(), GlassdoorSource(),
    ]
